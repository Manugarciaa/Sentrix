"""
OpenTelemetry Distributed Tracing

Provides distributed tracing capabilities for the Sentrix application.

Quick Start:
    # In your FastAPI app startup
    from src.tracing import setup_instrumentation

    @app.on_event("startup")
    async def startup():
        setup_instrumentation(app)

    @app.on_event("shutdown")
    async def shutdown():
        from src.tracing import teardown_instrumentation
        teardown_instrumentation()

Manual Instrumentation:
    from src.tracing import traced, get_tracer

    # Using decorator
    @traced(name="process_image", attributes={"version": "v1"})
    async def process_image(image_path: str):
        return result

    # Using context manager
    tracer = get_tracer(__name__)
    with tracer.start_as_current_span("custom_operation") as span:
        span.set_attribute("operation_type", "analysis")
        # ... do work
        pass
"""

# Configuration
from .config import (
    TracingConfig,
    get_tracing_config,
    get_tracer,
    setup_tracing_from_settings,
)

# Instrumentation
from .instrumentation import (
    InstrumentationManager,
    get_instrumentation_manager,
    setup_instrumentation,
    teardown_instrumentation,
)

# Decorators
from .decorators import (
    traced,
    traced_method,
    trace_database_operation,
    trace_external_call,
    add_span_attributes,
    add_span_event,
    get_trace_context,
)

# Middleware
from .middleware import (
    TracingEnrichmentMiddleware,
    PerformanceTracingMiddleware,
    add_user_context_to_span,
    add_business_context_to_span,
    record_metric_event,
    create_child_span,
)

__all__ = [
    # Configuration
    "TracingConfig",
    "get_tracing_config",
    "get_tracer",
    "setup_tracing_from_settings",
    # Instrumentation
    "InstrumentationManager",
    "get_instrumentation_manager",
    "setup_instrumentation",
    "teardown_instrumentation",
    # Decorators
    "traced",
    "traced_method",
    "trace_database_operation",
    "trace_external_call",
    "add_span_attributes",
    "add_span_event",
    "get_trace_context",
    # Middleware
    "TracingEnrichmentMiddleware",
    "PerformanceTracingMiddleware",
    "add_user_context_to_span",
    "add_business_context_to_span",
    "record_metric_event",
    "create_child_span",
]
