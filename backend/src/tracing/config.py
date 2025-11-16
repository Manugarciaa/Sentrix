"""
OpenTelemetry Tracing Configuration

Provides centralized configuration for distributed tracing.
"""

from typing import Optional
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SpanExporter,
)
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace.sampling import (
    TraceIdRatioBased,
    ParentBasedTraceIdRatioBased,
)

from ..config import get_settings


class TracingConfig:
    """
    OpenTelemetry tracing configuration.

    Provides centralized setup for distributed tracing with multiple
    exporter backends (OTLP, Jaeger, Console).
    """

    def __init__(self):
        self.settings = get_settings()
        self.tracer_provider: Optional[TracerProvider] = None
        self.tracer: Optional[trace.Tracer] = None

    def setup_tracing(
        self,
        service_name: str = "sentrix-backend",
        service_version: str = "1.0.0",
        exporter_type: str = "otlp",  # "otlp", "jaeger", "console", or "none"
        sampling_rate: float = 1.0,
    ) -> trace.Tracer:
        """
        Setup OpenTelemetry tracing with specified configuration.

        Args:
            service_name: Name of the service
            service_version: Version of the service
            exporter_type: Type of exporter ("otlp", "jaeger", "console", "none")
            sampling_rate: Sampling rate (0.0 to 1.0)

        Returns:
            Configured tracer instance

        Example:
            from src.tracing.config import TracingConfig

            tracing = TracingConfig()
            tracer = tracing.setup_tracing(
                service_name="sentrix-backend",
                exporter_type="otlp",
                sampling_rate=1.0 if settings.environment == "development" else 0.1
            )
        """
        # Create resource with service information
        resource = Resource.create({
            SERVICE_NAME: service_name,
            SERVICE_VERSION: service_version,
            "deployment.environment": self.settings.environment,
        })

        # Configure sampling
        # Parent-based means: if parent span is sampled, child is sampled
        sampler = ParentBasedTraceIdRatioBased(sampling_rate)

        # Create tracer provider
        self.tracer_provider = TracerProvider(
            resource=resource,
            sampler=sampler,
        )

        # Add span processor with appropriate exporter
        exporter = self._create_exporter(exporter_type)
        if exporter:
            span_processor = BatchSpanProcessor(exporter)
            self.tracer_provider.add_span_processor(span_processor)

        # Set as global tracer provider
        trace.set_tracer_provider(self.tracer_provider)

        # Get tracer instance
        self.tracer = trace.get_tracer(service_name, service_version)

        return self.tracer

    def _create_exporter(self, exporter_type: str) -> Optional[SpanExporter]:
        """
        Create span exporter based on type.

        Args:
            exporter_type: Type of exporter

        Returns:
            SpanExporter instance or None
        """
        if exporter_type == "none":
            return None

        elif exporter_type == "console":
            # Console exporter - useful for development/debugging
            return ConsoleSpanExporter()

        elif exporter_type == "otlp":
            # OTLP exporter - standard protocol, works with many backends
            # (Jaeger, Tempo, Zipkin, Cloud providers, etc.)
            endpoint = self._get_otlp_endpoint()
            return OTLPSpanExporter(
                endpoint=endpoint,
                # Optional: Add headers for authentication
                # headers=(("api-key", "your-api-key"),)
            )

        elif exporter_type == "jaeger":
            # Jaeger exporter - direct Jaeger integration
            return JaegerExporter(
                agent_host_name=self._get_jaeger_host(),
                agent_port=self._get_jaeger_port(),
            )

        else:
            raise ValueError(f"Unknown exporter type: {exporter_type}")

    def _get_otlp_endpoint(self) -> str:
        """Get OTLP collector endpoint from settings or environment."""
        # Default to local collector
        endpoint = getattr(
            self.settings,
            "otel_exporter_otlp_endpoint",
            "http://localhost:4317"
        )
        return endpoint

    def _get_jaeger_host(self) -> str:
        """Get Jaeger agent host from settings or environment."""
        return getattr(
            self.settings,
            "jaeger_agent_host",
            "localhost"
        )

    def _get_jaeger_port(self) -> int:
        """Get Jaeger agent port from settings or environment."""
        return getattr(
            self.settings,
            "jaeger_agent_port",
            6831
        )

    def get_tracer(self) -> trace.Tracer:
        """
        Get the configured tracer instance.

        Returns:
            Tracer instance

        Raises:
            RuntimeError: If tracing not setup
        """
        if self.tracer is None:
            raise RuntimeError(
                "Tracing not setup. Call setup_tracing() first."
            )
        return self.tracer

    def shutdown(self):
        """
        Shutdown tracing and flush remaining spans.

        Should be called on application shutdown.
        """
        if self.tracer_provider:
            self.tracer_provider.shutdown()


# Global tracing config instance
_tracing_config: Optional[TracingConfig] = None


def get_tracing_config() -> TracingConfig:
    """
    Get global tracing configuration instance.

    Returns:
        TracingConfig instance (singleton)

    Example:
        config = get_tracing_config()
        tracer = config.get_tracer()

        with tracer.start_as_current_span("my-operation"):
            # ... do work
            pass
    """
    global _tracing_config

    if _tracing_config is None:
        _tracing_config = TracingConfig()

    return _tracing_config


def get_tracer(name: str = "sentrix") -> trace.Tracer:
    """
    Get a tracer instance for manual instrumentation.

    Args:
        name: Name of the tracer (usually module or component name)

    Returns:
        Tracer instance

    Example:
        from src.tracing.config import get_tracer

        tracer = get_tracer(__name__)

        with tracer.start_as_current_span("process_image") as span:
            span.set_attribute("image.size", image_size)
            result = process_image(image)
            return result
    """
    return trace.get_tracer(name)


def setup_tracing_from_settings() -> trace.Tracer:
    """
    Setup tracing using application settings.

    Reads configuration from Settings and initializes tracing accordingly.

    Returns:
        Configured tracer instance

    Example:
        # In app.py startup
        from src.tracing.config import setup_tracing_from_settings

        @app.on_event("startup")
        async def startup():
            setup_tracing_from_settings()
    """
    settings = get_settings()
    config = get_tracing_config()

    # Determine exporter type from settings
    exporter_type = getattr(
        settings,
        "otel_exporter_type",
        "console" if settings.environment == "development" else "otlp"
    )

    # Adjust sampling rate based on environment
    if settings.environment == "production":
        sampling_rate = 0.1  # 10% sampling in production
    elif settings.environment == "staging":
        sampling_rate = 0.5  # 50% sampling in staging
    else:
        sampling_rate = 1.0  # 100% sampling in development

    # Allow override via settings
    sampling_rate = getattr(
        settings,
        "otel_sampling_rate",
        sampling_rate
    )

    return config.setup_tracing(
        service_name="sentrix-backend",
        service_version="1.0.0",
        exporter_type=exporter_type,
        sampling_rate=sampling_rate,
    )
