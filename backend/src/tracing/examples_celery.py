"""
Celery Integration Examples

Shows how to integrate OpenTelemetry tracing with Celery tasks.
"""

from celery import Celery, Task
from typing import Optional
from uuid import UUID

from .decorators import (
    traced,
    add_span_attributes,
    add_span_event,
    get_trace_context,
)
from .middleware import record_metric_event


# ============================================
# Example 1: Basic Task Tracing
# ============================================
# Celery tasks are automatically traced by the instrumentation


def example_basic_task():
    """
    Example of a basic traced Celery task.

    Tasks are automatically traced by CeleryInstrumentor.
    """
    app = Celery("sentrix")

    @app.task
    def process_image(image_path: str):
        """
        Process image task - automatically traced.

        Span includes:
        - Task name
        - Task arguments
        - Execution time
        - Success/failure status
        """
        # Add custom attributes
        add_span_attributes(
            task_type="image_processing",
            image_path=image_path
        )

        # Process image
        result = perform_image_processing(image_path)

        # Record metrics
        record_metric_event("images_processed", 1, "count")

        return result


# ============================================
# Example 2: Task with Manual Spans
# ============================================


def example_complex_task():
    """Example of task with manual span creation."""
    from .config import get_tracer

    app = Celery("sentrix")
    tracer = get_tracer(__name__)

    @app.task
    def analyze_images(image_paths: list):
        """
        Analyze multiple images with detailed tracing.
        """
        # Parent span created automatically by Celery instrumentation

        add_span_attributes(image_count=len(image_paths))
        add_span_event("analysis_started")

        results = []

        # Create span for each image
        for i, path in enumerate(image_paths):
            with tracer.start_as_current_span(f"analyze_image_{i}") as span:
                span.set_attribute("image.path", path)
                span.set_attribute("image.index", i)

                try:
                    result = analyze_single_image(path)
                    results.append(result)
                    span.set_attribute("analysis.success", True)

                except Exception as e:
                    span.record_exception(e)
                    span.set_attribute("analysis.success", False)

        add_span_event("analysis_completed", {
            "total_images": len(image_paths),
            "successful": len(results)
        })

        return results


# ============================================
# Example 3: Task Chain with Trace Propagation
# ============================================


def example_task_chain():
    """
    Example of task chains with trace context propagation.

    Important: Trace context needs to be explicitly propagated
    between tasks to maintain the trace.
    """
    app = Celery("sentrix")

    @app.task
    def step1_validate_images(image_paths: list):
        """First step: validate images."""
        add_span_event("validation_started")

        valid_paths = []
        for path in image_paths:
            if is_valid_image(path):
                valid_paths.append(path)

        record_metric_event("valid_images", len(valid_paths), "count")

        # Get trace context to propagate to next task
        trace_context = get_trace_context()

        # Call next task with trace context
        return step2_process_images.apply_async(
            args=[valid_paths],
            headers=trace_context  # Propagate trace context
        )

    @app.task
    def step2_process_images(image_paths: list):
        """Second step: process validated images."""
        add_span_event("processing_started")

        results = []
        for path in image_paths:
            result = process_image_internal(path)
            results.append(result)

        # Get trace context for next step
        trace_context = get_trace_context()

        return step3_save_results.apply_async(
            args=[results],
            headers=trace_context
        )

    @app.task
    def step3_save_results(results: list):
        """Third step: save results."""
        add_span_event("saving_started")

        saved_count = 0
        for result in results:
            save_result_to_db(result)
            saved_count += 1

        record_metric_event("results_saved", saved_count, "count")
        add_span_event("saving_completed")

        return {"saved": saved_count}


# ============================================
# Example 4: Task with Retries and Tracing
# ============================================


def example_task_with_retries():
    """Example of task with retry logic and tracing."""
    app = Celery("sentrix")

    @app.task(bind=True, max_retries=3, default_retry_delay=60)
    def fetch_external_data(self, url: str):
        """
        Fetch data from external API with retries.

        Each retry attempt is recorded in the trace.
        """
        from opentelemetry.trace import Status, StatusCode
        from .config import get_tracer

        tracer = get_tracer(__name__)

        # Add retry information
        add_span_attributes(
            retry_count=self.request.retries,
            max_retries=self.max_retries
        )

        if self.request.retries > 0:
            add_span_event("task_retry_attempt", {
                "attempt": self.request.retries + 1,
                "max_attempts": self.max_retries + 1
            })

        try:
            with tracer.start_as_current_span("fetch_data") as span:
                span.set_attribute("url", url)

                # Attempt to fetch data
                data = fetch_from_external_api(url)

                span.set_status(Status(StatusCode.OK))
                add_span_event("fetch_successful")

                return data

        except Exception as e:
            add_span_event("fetch_failed", {
                "error": str(e),
                "retry_count": self.request.retries
            })

            # Retry if we haven't exceeded max retries
            if self.request.retries < self.max_retries:
                add_span_event("scheduling_retry", {
                    "delay_seconds": 60
                })
                raise self.retry(exc=e, countdown=60)
            else:
                add_span_event("max_retries_exceeded")
                raise


# ============================================
# Example 5: Periodic Tasks with Tracing
# ============================================


def example_periodic_task():
    """Example of periodic task with tracing."""
    from celery.schedules import crontab

    app = Celery("sentrix")

    @app.task
    def cleanup_old_data():
        """
        Periodic cleanup task - runs daily.

        Trace helps monitor cleanup performance and identify issues.
        """
        from .config import get_tracer

        tracer = get_tracer(__name__)

        add_span_event("cleanup_started")
        add_span_attributes(task_type="maintenance")

        deleted_count = 0

        # Cleanup expired analyses
        with tracer.start_as_current_span("cleanup_analyses") as span:
            count = delete_expired_analyses()
            deleted_count += count
            span.set_attribute("deleted_analyses", count)

        # Cleanup orphaned files
        with tracer.start_as_current_span("cleanup_files") as span:
            count = delete_orphaned_files()
            deleted_count += count
            span.set_attribute("deleted_files", count)

        # Record metrics
        record_metric_event("total_deleted", deleted_count, "items")

        add_span_event("cleanup_completed", {
            "deleted_items": deleted_count
        })

        return {"deleted": deleted_count}

    # Schedule task
    app.conf.beat_schedule = {
        "cleanup-daily": {
            "task": "cleanup_old_data",
            "schedule": crontab(hour=2, minute=0),  # 2 AM daily
        }
    }


# ============================================
# Example 6: Task with Database Operations
# ============================================


def example_task_with_database():
    """Example of task with database operations."""
    from .decorators import trace_database_operation

    app = Celery("sentrix")

    @app.task
    def update_user_statistics(user_id: str):
        """
        Update user statistics - with traced database operations.
        """
        add_span_attributes(user_id=user_id)

        @trace_database_operation("query")
        def get_user_analyses():
            # Query automatically traced with db.operation="query"
            return db.query(Analysis).filter_by(user_id=user_id).all()

        @trace_database_operation("update")
        def update_stats(stats):
            # Update automatically traced with db.operation="update"
            user = db.query(User).filter_by(id=user_id).first()
            user.statistics = stats
            db.commit()

        # Get analyses
        analyses = get_user_analyses()

        # Calculate statistics
        stats = calculate_statistics(analyses)
        record_metric_event("analyses_processed", len(analyses), "count")

        # Update user
        update_stats(stats)

        add_span_event("statistics_updated")

        return stats


# ============================================
# Example 7: Task with External Service Calls
# ============================================


def example_task_with_external_service():
    """Example of task calling external services."""
    from .decorators import trace_external_call

    app = Celery("sentrix")

    @app.task
    def process_with_yolo(image_path: str):
        """
        Process image with YOLO service.

        External call is traced separately for better observability.
        """
        add_span_attributes(
            image_path=image_path,
            service="yolo"
        )

        @trace_external_call("yolo-service", "detect")
        async def call_yolo():
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://yolo-service:8001/detect",
                    json={"image_path": image_path},
                    timeout=30.0
                )
                return response.json()

        # Call YOLO service
        add_span_event("calling_yolo_service")
        detections = await call_yolo()

        record_metric_event("detections_found", len(detections), "count")

        # Save results
        save_detections(image_path, detections)

        add_span_event("processing_completed")

        return detections


# ============================================
# Example 8: Custom Task Base Class with Tracing
# ============================================


class TracedTask(Task):
    """
    Custom task base class with built-in tracing enhancements.

    Adds automatic trace context, error handling, and metrics.
    """

    def __call__(self, *args, **kwargs):
        """
        Execute task with enhanced tracing.
        """
        import time
        from opentelemetry.trace import Status, StatusCode

        start_time = time.perf_counter()

        # Add task metadata
        add_span_attributes(
            task_name=self.name,
            task_id=self.request.id,
            retry_count=self.request.retries
        )

        try:
            # Execute task
            result = super().__call__(*args, **kwargs)

            # Record success
            duration_ms = (time.perf_counter() - start_time) * 1000
            record_metric_event("task_duration", duration_ms, "ms")
            add_span_event("task_completed_successfully")

            return result

        except Exception as e:
            # Record failure
            duration_ms = (time.perf_counter() - start_time) * 1000
            record_metric_event("task_duration", duration_ms, "ms")

            add_span_event("task_failed", {
                "error": str(e),
                "error_type": type(e).__name__
            })

            raise


def example_with_custom_task_class():
    """Example using custom task base class."""
    app = Celery("sentrix")

    @app.task(base=TracedTask)
    def my_task(data: dict):
        """
        Task using custom base class.

        Automatically gets enhanced tracing from TracedTask.
        """
        return process_data(data)


# Dummy functions for examples
def perform_image_processing(path): pass
def analyze_single_image(path): pass
def is_valid_image(path): pass
def process_image_internal(path): pass
def save_result_to_db(result): pass
def fetch_from_external_api(url): pass
def delete_expired_analyses(): pass
def delete_orphaned_files(): pass
def calculate_statistics(analyses): pass
def save_detections(path, detections): pass
def process_data(data): pass
