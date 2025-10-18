"""
OpenTelemetry Tracing Middleware

Provides middleware for enriching traces with custom context.
"""

from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode


class TracingEnrichmentMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enrich traces with additional context.

    Adds user information, request IDs, and other custom attributes
    to the current span.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process request and enrich trace with context.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response
        """
        span = trace.get_current_span()

        # Add request context
        if span.is_recording():
            # Add request ID if present
            request_id = request.headers.get("X-Request-ID")
            if request_id:
                span.set_attribute("request.id", request_id)

            # Add correlation ID if present
            correlation_id = request.headers.get("X-Correlation-ID")
            if correlation_id:
                span.set_attribute("correlation.id", correlation_id)

            # Add user information if authenticated
            if hasattr(request.state, "user"):
                user = request.state.user
                if user:
                    span.set_attribute("user.id", str(user.id))
                    span.set_attribute("user.email", user.email)

            # Add client information
            client_host = request.client.host if request.client else "unknown"
            span.set_attribute("client.address", client_host)

            # Add user agent
            user_agent = request.headers.get("User-Agent", "unknown")
            span.set_attribute("http.user_agent", user_agent)

            # Add API version if present
            api_version = request.headers.get("X-API-Version")
            if api_version:
                span.set_attribute("api.version", api_version)

        try:
            # Process request
            response = await call_next(request)

            # Add response context
            if span.is_recording():
                span.set_attribute("http.response.status_code", response.status_code)

                # Mark span as error if status code indicates error
                if response.status_code >= 400:
                    span.set_status(
                        Status(StatusCode.ERROR, f"HTTP {response.status_code}")
                    )
                else:
                    span.set_status(Status(StatusCode.OK))

            return response

        except Exception as e:
            # Record exception in span
            if span.is_recording():
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)

            raise


class PerformanceTracingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add performance metrics to traces.

    Records detailed timing information for different stages
    of request processing.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process request and record performance metrics.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response
        """
        import time

        span = trace.get_current_span()
        start_time = time.perf_counter()

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Add performance metrics
            if span.is_recording():
                span.set_attribute("performance.duration_ms", round(duration_ms, 2))

                # Add performance category
                if duration_ms < 100:
                    category = "fast"
                elif duration_ms < 500:
                    category = "normal"
                elif duration_ms < 1000:
                    category = "slow"
                else:
                    category = "very_slow"

                span.set_attribute("performance.category", category)

                # Add event for slow requests
                if duration_ms > 1000:
                    span.add_event(
                        "slow_request_detected",
                        attributes={
                            "duration_ms": round(duration_ms, 2),
                            "threshold_ms": 1000,
                        }
                    )

            return response

        except Exception as e:
            # Still record duration even on error
            duration_ms = (time.perf_counter() - start_time) * 1000

            if span.is_recording():
                span.set_attribute("performance.duration_ms", round(duration_ms, 2))
                span.set_attribute("performance.category", "error")

            raise


def add_user_context_to_span(user):
    """
    Add user context to current span.

    Args:
        user: User object with id, email, etc.

    Example:
        from src.tracing.middleware import add_user_context_to_span

        @app.get("/profile")
        async def get_profile(current_user: User = Depends(get_current_user)):
            add_user_context_to_span(current_user)
            return {"user": current_user}
    """
    span = trace.get_current_span()

    if span.is_recording() and user:
        span.set_attribute("user.id", str(user.id))
        span.set_attribute("user.email", user.email)

        if hasattr(user, "role"):
            span.set_attribute("user.role", user.role)

        if hasattr(user, "organization_id"):
            span.set_attribute("user.organization_id", str(user.organization_id))


def add_business_context_to_span(**context):
    """
    Add business/domain context to current span.

    Args:
        **context: Business context attributes

    Example:
        from src.tracing.middleware import add_business_context_to_span

        @app.post("/analyses")
        async def create_analysis(data: AnalysisCreate):
            add_business_context_to_span(
                analysis_type=data.analysis_type,
                image_count=len(data.images),
                priority=data.priority
            )
            return await service.create_analysis(data)
    """
    span = trace.get_current_span()

    if span.is_recording():
        for key, value in context.items():
            span.set_attribute(f"business.{key}", str(value))


def record_metric_event(metric_name: str, value: float, unit: str = ""):
    """
    Record a metric event in the current span.

    Args:
        metric_name: Name of the metric
        value: Metric value
        unit: Unit of measurement (optional)

    Example:
        from src.tracing.middleware import record_metric_event

        async def process_batch(items: List[Item]):
            record_metric_event("batch_size", len(items), "items")

            start = time.time()
            result = await process(items)
            duration = time.time() - start

            record_metric_event("processing_time", duration, "seconds")
            record_metric_event("items_per_second", len(items) / duration, "items/s")

            return result
    """
    span = trace.get_current_span()

    if span.is_recording():
        attributes = {
            "metric.name": metric_name,
            "metric.value": value,
        }

        if unit:
            attributes["metric.unit"] = unit

        span.add_event("metric_recorded", attributes=attributes)


def create_child_span(name: str, attributes: dict = None):
    """
    Create a child span for manual instrumentation.

    Returns a context manager that creates a child span.

    Args:
        name: Span name
        attributes: Optional attributes to add

    Returns:
        Span context manager

    Example:
        from src.tracing.middleware import create_child_span

        async def complex_operation():
            with create_child_span("validation") as validation_span:
                validation_span.set_attribute("rules_count", len(rules))
                validate_data(data)

            with create_child_span("processing") as processing_span:
                processing_span.set_attribute("items_count", len(items))
                result = process_data(data)

            with create_child_span("persistence") as persistence_span:
                save_result(result)

            return result
    """
    tracer = trace.get_tracer(__name__)
    span = tracer.start_as_current_span(name)

    if attributes and span.is_recording():
        for key, value in attributes.items():
            span.set_attribute(key, value)

    return span
