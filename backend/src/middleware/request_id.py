"""
Request ID Middleware
Adds unique request IDs to all requests for tracing across services
"""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable

from ..logging_config import bind_contextvars, clear_contextvars, get_logger

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request IDs to all requests

    Features:
    - Generates UUID for each request (or uses existing X-Request-ID header)
    - Binds request ID to context for automatic logging inclusion
    - Adds X-Request-ID to response headers
    - Clears context after request completes
    - Logs request start and completion with timing
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add request ID

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response with X-Request-ID header
        """
        # Get or generate request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Bind to context for logging
        bind_contextvars(request_id=request_id)

        # Log request start
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            client_host=request.client.host if request.client else "unknown"
        )

        # Store start time for duration calculation
        import time
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Log request completion
            logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Log request failure
            logger.error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms,
                exception=str(e),
                exception_type=type(e).__name__
            )
            raise

        finally:
            # Always clear context after request
            clear_contextvars()


def setup_request_id_middleware(app):
    """
    Add RequestIDMiddleware to FastAPI application

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(RequestIDMiddleware)
    logger.info("RequestIDMiddleware configured")
