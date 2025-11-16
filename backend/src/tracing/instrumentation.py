"""
OpenTelemetry Auto-Instrumentation

Provides automatic instrumentation for common libraries and frameworks.
"""

from typing import Optional
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor

from ..config import get_settings
from ..logging_config import get_logger

logger = get_logger(__name__)


class InstrumentationManager:
    """
    Manages automatic instrumentation of libraries and frameworks.

    Provides centralized setup and teardown of auto-instrumentation.
    """

    def __init__(self):
        self.settings = get_settings()
        self._instrumented = False
        self._instrumentors = []

    def instrument_all(self, app=None, engine=None):
        """
        Instrument all supported libraries.

        Args:
            app: FastAPI application instance (optional)
            engine: SQLAlchemy engine instance (optional)

        Example:
            from fastapi import FastAPI
            from src.tracing.instrumentation import InstrumentationManager

            app = FastAPI()
            instrumentation = InstrumentationManager()
            instrumentation.instrument_all(app=app)
        """
        if self._instrumented:
            return

        # Instrument FastAPI
        if app is not None:
            self.instrument_fastapi(app)

        # Instrument HTTPX (HTTP client)
        self.instrument_httpx()

        # Instrument Redis
        self.instrument_redis()

        # Instrument SQLAlchemy
        if engine is not None:
            self.instrument_sqlalchemy(engine)

        # Instrument Celery
        self.instrument_celery()

        self._instrumented = True

    def instrument_fastapi(self, app):
        """
        Instrument FastAPI application.

        Automatically creates spans for HTTP requests with:
        - HTTP method, path, status code
        - Request/response headers (configurable)
        - Exceptions and error details

        Args:
            app: FastAPI application instance

        Example:
            from fastapi import FastAPI
            from src.tracing.instrumentation import InstrumentationManager

            app = FastAPI()
            manager = InstrumentationManager()
            manager.instrument_fastapi(app)
        """
        instrumentor = FastAPIInstrumentor()
        instrumentor.instrument_app(
            app,
            excluded_urls=self._get_excluded_urls(),
            # Optional: customize span names
            # server_request_hook=self._request_hook,
            # client_response_hook=self._response_hook,
        )
        self._instrumentors.append(instrumentor)

    def instrument_httpx(self):
        """
        Instrument HTTPX HTTP client.

        Automatically creates spans for outgoing HTTP requests.

        Example:
            import httpx
            from src.tracing.instrumentation import InstrumentationManager

            manager = InstrumentationManager()
            manager.instrument_httpx()

            # Now all httpx calls are traced
            async with httpx.AsyncClient() as client:
                response = await client.get("https://api.example.com")
        """
        instrumentor = HTTPXClientInstrumentor()
        instrumentor.instrument()
        self._instrumentors.append(instrumentor)

    def instrument_redis(self):
        """
        Instrument Redis client.

        Automatically creates spans for Redis operations.

        Example:
            import redis
            from src.tracing.instrumentation import InstrumentationManager

            manager = InstrumentationManager()
            manager.instrument_redis()

            # Now all Redis operations are traced
            r = redis.Redis()
            r.set("key", "value")  # This will be traced
        """
        instrumentor = RedisInstrumentor()
        instrumentor.instrument()
        self._instrumentors.append(instrumentor)

    def instrument_sqlalchemy(self, engine):
        """
        Instrument SQLAlchemy ORM.

        Automatically creates spans for database queries.

        Args:
            engine: SQLAlchemy engine instance

        Example:
            from sqlalchemy import create_engine
            from src.tracing.instrumentation import InstrumentationManager

            engine = create_engine("postgresql://...")
            manager = InstrumentationManager()
            manager.instrument_sqlalchemy(engine)
        """
        instrumentor = SQLAlchemyInstrumentor()
        instrumentor.instrument(
            engine=engine,
            enable_commenter=True,  # Add trace context to SQL comments
        )
        self._instrumentors.append(instrumentor)

    def instrument_celery(self):
        """
        Instrument Celery task queue.

        Automatically creates spans for Celery tasks with:
        - Task name and arguments
        - Queue information
        - Execution time
        - Success/failure status

        Example:
            from celery import Celery
            from src.tracing.instrumentation import InstrumentationManager

            app = Celery("sentrix")
            manager = InstrumentationManager()
            manager.instrument_celery()

            @app.task
            def my_task(x, y):
                return x + y  # This will be traced
        """
        instrumentor = CeleryInstrumentor()
        instrumentor.instrument()
        self._instrumentors.append(instrumentor)

    def uninstrument_all(self):
        """
        Remove all instrumentation.

        Should be called on application shutdown or for testing.

        Example:
            manager = InstrumentationManager()
            manager.instrument_all(app)

            # ... application runs

            # On shutdown
            manager.uninstrument_all()
        """
        for instrumentor in self._instrumentors:
            try:
                instrumentor.uninstrument()
            except Exception as e:
                logger.error("error uninstrumenting", instrumentor=str(instrumentor), error=str(e))

        self._instrumentors.clear()
        self._instrumented = False

    def _get_excluded_urls(self) -> str:
        """
        Get URLs to exclude from tracing.

        Returns:
            Comma-separated URL patterns to exclude
        """
        # Exclude health checks and metrics endpoints from tracing
        # to avoid trace spam
        excluded = [
            "/health",
            "/health/ready",
            "/health/live",
            "/metrics",
            "/favicon.ico",
        ]

        # Allow override via settings
        if hasattr(self.settings, "otel_excluded_urls"):
            additional = self.settings.otel_excluded_urls.split(",")
            excluded.extend([url.strip() for url in additional if url.strip()])

        return ",".join(excluded)

    @staticmethod
    def _request_hook(span, scope):
        """
        Custom hook to add request information to span.

        Args:
            span: Current span
            scope: ASGI scope dict
        """
        # Add custom attributes from request
        if "user" in scope:
            span.set_attribute("user.id", str(scope["user"].get("id")))
            span.set_attribute("user.email", scope["user"].get("email"))

        # Add request ID if present
        for header_name, header_value in scope.get("headers", []):
            if header_name == b"x-request-id":
                span.set_attribute("request.id", header_value.decode())

    @staticmethod
    def _response_hook(span, message):
        """
        Custom hook to add response information to span.

        Args:
            span: Current span
            message: ASGI message dict
        """
        # Add response size
        if "body" in message:
            span.set_attribute("response.size", len(message["body"]))


# Global instrumentation manager
_instrumentation_manager: Optional[InstrumentationManager] = None


def get_instrumentation_manager() -> InstrumentationManager:
    """
    Get global instrumentation manager instance.

    Returns:
        InstrumentationManager instance (singleton)

    Example:
        from src.tracing.instrumentation import get_instrumentation_manager

        manager = get_instrumentation_manager()
        manager.instrument_all(app=app, engine=engine)
    """
    global _instrumentation_manager

    if _instrumentation_manager is None:
        _instrumentation_manager = InstrumentationManager()

    return _instrumentation_manager


def setup_instrumentation(app, engine=None):
    """
    Setup all instrumentation for the application.

    Convenience function that combines tracing config and instrumentation.

    Args:
        app: FastAPI application
        engine: SQLAlchemy engine (optional)

    Example:
        from fastapi import FastAPI
        from src.tracing.instrumentation import setup_instrumentation

        app = FastAPI()

        @app.on_event("startup")
        async def startup():
            setup_instrumentation(app)
    """
    # Setup tracing configuration
    from .config import setup_tracing_from_settings
    setup_tracing_from_settings()

    # Setup instrumentation
    manager = get_instrumentation_manager()
    manager.instrument_all(app=app, engine=engine)


def teardown_instrumentation():
    """
    Teardown all instrumentation.

    Should be called on application shutdown.

    Example:
        @app.on_event("shutdown")
        async def shutdown():
            teardown_instrumentation()
    """
    manager = get_instrumentation_manager()
    manager.uninstrument_all()

    from .config import get_tracing_config
    config = get_tracing_config()
    config.shutdown()
