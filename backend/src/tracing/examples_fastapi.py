"""
FastAPI Integration Examples

Shows how to integrate OpenTelemetry tracing with FastAPI routes and dependencies.
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from typing import Optional
from uuid import UUID

from .decorators import (
    traced,
    traced_method,
    add_span_attributes,
    add_span_event,
    trace_database_operation,
)
from .middleware import (
    add_user_context_to_span,
    add_business_context_to_span,
    record_metric_event,
)


# ============================================
# Example 1: Basic Route Tracing
# ============================================
# FastAPI routes are automatically traced by the instrumentation,
# but you can add custom attributes and events


async def example_basic_route():
    """
    Example of a basic traced route.

    The route is automatically traced by FastAPIInstrumentor,
    but we add custom attributes for additional context.
    """
    from fastapi import APIRouter
    router = APIRouter()

    @router.get("/users/{user_id}")
    async def get_user(user_id: str):
        # Add custom attributes to the automatic span
        add_span_attributes(
            user_id=user_id,
            endpoint="get_user",
            version="v1"
        )

        # Simulate fetching user
        user = await fetch_user(user_id)

        # Add event for important moments
        add_span_event("user_fetched", {
            "user_id": user_id,
            "user_email": user.email
        })

        return user


# ============================================
# Example 2: Manual Span for Complex Operations
# ============================================


async def example_complex_operation():
    """
    Example of manually creating spans for complex operations.
    """
    from fastapi import APIRouter
    from .config import get_tracer

    router = APIRouter()
    tracer = get_tracer(__name__)

    @router.post("/analyses")
    async def create_analysis(data: dict):
        # Parent span created automatically by FastAPI instrumentation

        # Create child span for validation
        with tracer.start_as_current_span("validate_input") as span:
            span.set_attribute("field_count", len(data))
            validate_analysis_data(data)

        # Create child span for image processing
        with tracer.start_as_current_span("process_images") as span:
            image_count = len(data.get("images", []))
            span.set_attribute("image_count", image_count)

            results = []
            for i, image in enumerate(data.get("images", [])):
                # Create span for each image
                with tracer.start_as_current_span(f"process_image_{i}") as img_span:
                    img_span.set_attribute("image_id", image["id"])
                    result = await process_image(image)
                    results.append(result)

        # Create child span for database save
        with tracer.start_as_current_span("save_analysis") as span:
            analysis = await save_analysis(data, results)
            span.set_attribute("analysis_id", str(analysis.id))

        return analysis


# ============================================
# Example 3: Using Decorators for Business Logic
# ============================================


class AnalysisService:
    """Example service with traced methods."""

    @traced_method(include_args=True, exclude_args=["password", "token"])
    async def create_analysis(self, user_id: UUID, image_paths: list):
        """
        Create analysis with automatic tracing.

        The decorator automatically:
        - Creates a span named "AnalysisService.create_analysis"
        - Adds user_id and image_paths as span attributes
        - Records exceptions if any occur
        """
        add_span_event("analysis_creation_started")

        # Validate images
        validated_images = await self._validate_images(image_paths)

        # Process with YOLO service
        detections = await self._call_yolo_service(validated_images)

        # Save to database
        analysis = await self._save_analysis(user_id, detections)

        add_span_event("analysis_creation_completed", {
            "analysis_id": str(analysis.id),
            "detection_count": len(detections)
        })

        return analysis

    @traced_method()
    async def _validate_images(self, image_paths: list):
        """Validate images - automatically traced."""
        add_span_attributes(image_count=len(image_paths))

        valid_images = []
        for path in image_paths:
            if await is_valid_image(path):
                valid_images.append(path)

        record_metric_event("valid_images", len(valid_images), "count")
        record_metric_event("invalid_images", len(image_paths) - len(valid_images), "count")

        return valid_images

    @traced_method()
    async def _call_yolo_service(self, images: list):
        """Call YOLO service - automatically traced with external service context."""
        from .decorators import trace_external_call

        @trace_external_call("yolo-service", "detect")
        async def call_yolo():
            # This creates a child span specifically for external calls
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://yolo-service:8001/detect",
                    json={"images": images},
                    timeout=30.0
                )
                return response.json()

        return await call_yolo()

    @trace_database_operation("insert")
    async def _save_analysis(self, user_id: UUID, detections: list):
        """Save analysis to database - traced as database operation."""
        from ..database.models import Analysis

        analysis = Analysis(
            user_id=user_id,
            detection_count=len(detections),
            # ... other fields
        )

        # Database operations automatically traced by SQLAlchemy instrumentation
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)

        return analysis


# ============================================
# Example 4: Dependency Injection with Tracing
# ============================================


async def get_current_user(request: Request):
    """
    Dependency that extracts current user and adds to trace context.
    """
    # Extract user from JWT or session
    user = await extract_user_from_request(request)

    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Add user context to span
    add_user_context_to_span(user)

    return user


async def example_with_dependency():
    """Example route with dependency injection."""
    from fastapi import APIRouter

    router = APIRouter()

    @router.get("/profile")
    async def get_profile(current_user=Depends(get_current_user)):
        """
        Route with user dependency.

        The dependency automatically adds user context to the trace.
        """
        # User context already added by dependency
        # Just add business context
        add_business_context_to_span(
            action="get_profile",
            resource="user_profile"
        )

        profile = await fetch_user_profile(current_user.id)
        return profile


# ============================================
# Example 5: Error Handling and Tracing
# ============================================


async def example_error_handling():
    """Example of error handling with tracing."""
    from fastapi import APIRouter

    router = APIRouter()

    @router.post("/process")
    async def process_data(data: dict):
        from opentelemetry.trace import Status, StatusCode
        from .config import get_tracer

        tracer = get_tracer(__name__)

        with tracer.start_as_current_span("data_processing") as span:
            try:
                # Process data
                result = await process(data)

                # Mark span as successful
                span.set_status(Status(StatusCode.OK))
                span.set_attribute("result.count", len(result))

                return result

            except ValueError as e:
                # Mark span as error and record exception
                span.set_status(Status(StatusCode.ERROR, "Validation failed"))
                span.record_exception(e)
                span.set_attribute("error.type", "validation")

                raise HTTPException(status_code=400, detail=str(e))

            except Exception as e:
                # Mark span as error and record exception
                span.set_status(Status(StatusCode.ERROR, "Processing failed"))
                span.record_exception(e)
                span.set_attribute("error.type", "processing")

                raise HTTPException(status_code=500, detail="Internal error")


# ============================================
# Example 6: Performance Monitoring
# ============================================


async def example_performance_monitoring():
    """Example of performance monitoring with tracing."""
    from fastapi import APIRouter
    import time

    router = APIRouter()

    @router.get("/slow-operation")
    async def slow_operation():
        import time
        from .middleware import record_metric_event

        start_time = time.perf_counter()

        # Simulate slow operation
        await perform_slow_operation()

        duration_ms = (time.perf_counter() - start_time) * 1000

        # Record performance metrics
        record_metric_event("operation_duration", duration_ms, "ms")

        if duration_ms > 1000:
            add_span_event("slow_operation_detected", {
                "duration_ms": duration_ms,
                "threshold_ms": 1000
            })

        return {"duration_ms": duration_ms}


# ============================================
# Example 7: Batch Operations with Tracing
# ============================================


async def example_batch_operations():
    """Example of tracing batch operations."""
    from fastapi import APIRouter

    router = APIRouter()

    @router.post("/batch-process")
    @traced(name="batch_process_endpoint")
    async def batch_process(items: list):
        from .config import get_tracer

        tracer = get_tracer(__name__)

        # Record batch size
        add_span_attributes(batch_size=len(items))

        results = []
        failed = 0

        # Process each item with individual span
        for i, item in enumerate(items):
            with tracer.start_as_current_span(f"process_item_{i}") as span:
                span.set_attribute("item.index", i)
                span.set_attribute("item.id", item.get("id"))

                try:
                    result = await process_item(item)
                    results.append(result)
                    span.set_status(Status(StatusCode.OK))

                except Exception as e:
                    failed += 1
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)

        # Record batch metrics
        record_metric_event("batch_processed", len(results), "items")
        record_metric_event("batch_failed", failed, "items")

        success_rate = len(results) / len(items) if items else 0
        record_metric_event("batch_success_rate", success_rate * 100, "percent")

        return {
            "processed": len(results),
            "failed": failed,
            "success_rate": success_rate
        }


# Dummy functions for examples
async def fetch_user(user_id): pass
async def fetch_user_profile(user_id): pass
async def process_image(image): pass
async def save_analysis(data, results): pass
async def is_valid_image(path): pass
async def extract_user_from_request(request): pass
async def perform_slow_operation(): pass
async def process_item(item): pass
def validate_analysis_data(data): pass
