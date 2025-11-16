"""
OpenTelemetry Tracing Decorators

Provides decorators for manual instrumentation of functions and methods.
"""

from functools import wraps
from typing import Callable, Optional, Any, Dict
import asyncio

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from .config import get_tracer


def traced(
    name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
    record_exception: bool = True,
):
    """
    Decorator to trace function execution with a span.

    Creates a new span for the decorated function and records:
    - Function name, module, and arguments (configurable)
    - Execution time
    - Return value (if configured)
    - Exceptions (if any)

    Args:
        name: Custom span name (defaults to function name)
        attributes: Static attributes to add to span
        record_exception: Whether to record exceptions in span

    Example:
        from src.tracing.decorators import traced

        @traced(name="process_image", attributes={"service": "image-processing"})
        def process_image(image_path: str):
            # ... processing logic
            return result

        @traced()  # Uses function name as span name
        async def fetch_user(user_id: str):
            # ... async logic
            return user
    """
    def decorator(func: Callable) -> Callable:
        span_name = name or f"{func.__module__}.{func.__name__}"
        tracer = get_tracer(func.__module__)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name) as span:
                # Add static attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                # Add function metadata
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)

                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result

                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    if record_exception:
                        span.record_exception(e)
                    raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name) as span:
                # Add static attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                # Add function metadata
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)

                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result

                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    if record_exception:
                        span.record_exception(e)
                    raise

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def traced_method(
    name: Optional[str] = None,
    include_args: bool = False,
    exclude_args: Optional[list] = None,
):
    """
    Decorator for tracing class methods with automatic span naming.

    Similar to @traced but designed for class methods with better
    automatic naming and argument handling.

    Args:
        name: Custom span name (defaults to ClassName.method_name)
        include_args: Whether to include method arguments as span attributes
        exclude_args: List of argument names to exclude (e.g., ["password"])

    Example:
        from src.tracing.decorators import traced_method

        class UserService:
            @traced_method(include_args=True, exclude_args=["password"])
            def create_user(self, email: str, password: str):
                # ... logic
                return user

            @traced_method()
            async def fetch_user_data(self, user_id: str):
                # ... async logic
                return data
    """
    exclude_args = exclude_args or []

    def decorator(func: Callable) -> Callable:
        tracer = get_tracer(func.__module__)

        @wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            # Generate span name with class name
            class_name = self.__class__.__name__
            span_name = name or f"{class_name}.{func.__name__}"

            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("class.name", class_name)
                span.set_attribute("method.name", func.__name__)

                # Add method arguments if requested
                if include_args:
                    _add_arguments_to_span(
                        span, func, args, kwargs, exclude_args
                    )

                try:
                    result = await func(self, *args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result

                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        @wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            # Generate span name with class name
            class_name = self.__class__.__name__
            span_name = name or f"{class_name}.{func.__name__}"

            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("class.name", class_name)
                span.set_attribute("method.name", func.__name__)

                # Add method arguments if requested
                if include_args:
                    _add_arguments_to_span(
                        span, func, args, kwargs, exclude_args
                    )

                try:
                    result = func(self, *args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result

                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def trace_database_operation(operation_type: str = "query"):
    """
    Decorator specifically for database operations.

    Adds database-specific attributes to spans following OpenTelemetry
    semantic conventions.

    Args:
        operation_type: Type of database operation (query, insert, update, delete)

    Example:
        from src.tracing.decorators import trace_database_operation

        @trace_database_operation("query")
        def get_user_by_email(email: str):
            return db.query(User).filter(User.email == email).first()

        @trace_database_operation("insert")
        async def create_analysis(data: dict):
            analysis = Analysis(**data)
            db.add(analysis)
            await db.commit()
            return analysis
    """
    def decorator(func: Callable) -> Callable:
        tracer = get_tracer(func.__module__)
        span_name = f"db.{operation_type}.{func.__name__}"

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("db.operation", operation_type)
                span.set_attribute("db.system", "postgresql")

                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result

                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("db.operation", operation_type)
                span.set_attribute("db.system", "postgresql")

                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result

                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def trace_external_call(service_name: str, operation: Optional[str] = None):
    """
    Decorator for tracing external service calls.

    Adds external service attributes to spans following OpenTelemetry
    semantic conventions.

    Args:
        service_name: Name of external service (e.g., "yolo-service", "redis")
        operation: Operation being performed (e.g., "detect", "classify")

    Example:
        from src.tracing.decorators import trace_external_call

        @trace_external_call("yolo-service", "detect")
        async def call_yolo_service(image_path: str):
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{YOLO_SERVICE_URL}/detect",
                    json={"image_path": image_path}
                )
                return response.json()
    """
    def decorator(func: Callable) -> Callable:
        tracer = get_tracer(func.__module__)
        op = operation or func.__name__
        span_name = f"{service_name}.{op}"

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("peer.service", service_name)
                span.set_attribute("rpc.operation", op)

                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result

                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("peer.service", service_name)
                span.set_attribute("rpc.operation", op)

                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result

                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def add_span_attributes(**attributes):
    """
    Add attributes to the current active span.

    Args:
        **attributes: Attributes to add to span

    Example:
        from src.tracing.decorators import add_span_attributes

        @app.get("/users/{user_id}")
        async def get_user(user_id: str):
            add_span_attributes(
                user_id=user_id,
                endpoint="get_user",
                version="v1"
            )
            return await fetch_user(user_id)
    """
    span = trace.get_current_span()
    if span.is_recording():
        for key, value in attributes.items():
            span.set_attribute(key, value)


def add_span_event(name: str, attributes: Optional[Dict[str, Any]] = None):
    """
    Add an event to the current active span.

    Events represent important moments within a span's lifetime.

    Args:
        name: Event name
        attributes: Event attributes

    Example:
        from src.tracing.decorators import add_span_event

        async def process_image(image_path: str):
            add_span_event("image_validation_started")

            if not is_valid(image_path):
                add_span_event("image_validation_failed", {
                    "reason": "invalid_format"
                })
                raise ValueError("Invalid image")

            add_span_event("image_validation_passed")
            # ... continue processing
    """
    span = trace.get_current_span()
    if span.is_recording():
        span.add_event(name, attributes=attributes or {})


def get_trace_context() -> Dict[str, str]:
    """
    Extract current trace context as HTTP headers.

    Useful for propagating trace context to external services.

    Returns:
        Dictionary of trace context headers

    Example:
        from src.tracing.decorators import get_trace_context
        import httpx

        async def call_external_service():
            headers = get_trace_context()
            async with httpx.AsyncClient() as client:
                # Trace context propagated to external service
                response = await client.get(
                    "https://api.example.com/data",
                    headers=headers
                )
                return response.json()
    """
    carrier = {}
    TraceContextTextMapPropagator().inject(carrier)
    return carrier


def _add_arguments_to_span(span, func, args, kwargs, exclude_args):
    """
    Helper to add function arguments as span attributes.

    Args:
        span: Current span
        func: Function being traced
        args: Positional arguments
        kwargs: Keyword arguments
        exclude_args: Arguments to exclude
    """
    import inspect

    # Get function signature
    sig = inspect.signature(func)
    param_names = list(sig.parameters.keys())

    # Add positional arguments
    for i, arg in enumerate(args):
        if i < len(param_names):
            param_name = param_names[i]
            if param_name not in exclude_args:
                try:
                    span.set_attribute(f"arg.{param_name}", str(arg))
                except Exception:
                    # Skip if can't convert to string
                    pass

    # Add keyword arguments
    for key, value in kwargs.items():
        if key not in exclude_args:
            try:
                span.set_attribute(f"arg.{key}", str(value))
            except Exception:
                # Skip if can't convert to string
                pass
