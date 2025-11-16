"""
Celery tasks for image analysis processing

These tasks handle long-running image analysis operations asynchronously,
preventing backend thread exhaustion and improving scalability.
"""

import base64
from typing import Dict, Any
from celery import Task

from ..celery_app import celery_app
from ..logging_config import get_logger, bind_contextvars, clear_contextvars

logger = get_logger(__name__)


class AnalysisTask(Task):
    """
    Base task class with logging and error handling
    """

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails"""
        logger.error(
            "analysis_task_failed",
            task_id=task_id,
            exception=str(exc),
            exception_type=type(exc).__name__,
            traceback=str(einfo)
        )

    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds"""
        logger.info(
            "analysis_task_succeeded",
            task_id=task_id,
            result_keys=list(retval.keys()) if isinstance(retval, dict) else None
        )

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried"""
        logger.warning(
            "analysis_task_retry",
            task_id=task_id,
            exception=str(exc),
            retry_count=self.request.retries
        )


@celery_app.task(
    bind=True,
    base=AnalysisTask,
    max_retries=3,
    default_retry_delay=60,  # Retry after 60 seconds
    name="src.tasks.analysis_tasks.process_image_analysis_task"
)
def process_image_analysis_task(
    self,
    image_data_b64: str,
    filename: str,
    confidence_threshold: float = 0.5,
    include_gps: bool = True,
    user_id: str = None,
    request_id: str = None
) -> Dict[str, Any]:
    """
    Async task for processing image analysis with YOLO

    Args:
        image_data_b64: Base64 encoded image data
        filename: Original filename
        confidence_threshold: Detection confidence threshold
        include_gps: Whether to extract GPS metadata
        user_id: User ID for the analysis
        request_id: Request ID for distributed tracing

    Returns:
        dict: Analysis results with detections and metadata

    Raises:
        Exception: If analysis fails after retries
    """
    # Bind request ID for logging
    if request_id:
        bind_contextvars(request_id=request_id)

    task_id = self.request.id

    logger.info(
        "analysis_task_started",
        task_id=task_id,
        filename=filename,
        confidence_threshold=confidence_threshold,
        user_id=user_id
    )

    try:
        # Decode base64 image data
        image_data = base64.b64decode(image_data_b64)

        # Import here to avoid circular dependencies
        from ..core.services.yolo_service import yolo_client
        from ..services.analysis_service import AnalysisService

        logger.info(
            "calling_yolo_service",
            task_id=task_id,
            image_size=len(image_data)
        )

        # Call YOLO service (this is the slow operation)
        # Note: We're calling the synchronous wrapper since Celery doesn't use asyncio by default
        # For async support, you'd need to configure Celery with async worker pool
        import asyncio

        # Create event loop for async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Call YOLO detection
            yolo_result = loop.run_until_complete(
                yolo_client.detect_image(
                    image_data=image_data,
                    filename=filename,
                    confidence_threshold=confidence_threshold,
                    include_gps=include_gps
                )
            )

            logger.info(
                "yolo_detection_completed_in_task",
                task_id=task_id,
                total_detections=yolo_result.get("total_detections", 0),
                processing_time_ms=yolo_result.get("processing_time_ms")
            )

            # Process and store results
            analysis_service = AnalysisService()

            # Create analysis record in database
            analysis_data = {
                "user_id": user_id,
                "filename": filename,
                "status": "completed",
                "total_detections": yolo_result.get("total_detections", 0),
                "risk_level": yolo_result.get("risk_assessment", {}).get("risk_level"),
                "has_gps_data": yolo_result.get("location") is not None,
                "processing_time_ms": yolo_result.get("processing_time_ms"),
                "model_used": yolo_result.get("model_used"),
                "confidence_threshold": confidence_threshold,
                "task_id": task_id,
            }

            # Store analysis result
            # Note: This would need proper async handling in production
            result = {
                "task_id": task_id,
                "status": "completed",
                "analysis_data": analysis_data,
                "yolo_result": yolo_result,
            }

            logger.info(
                "analysis_task_completed",
                task_id=task_id,
                total_detections=yolo_result.get("total_detections", 0)
            )

            return result

        finally:
            loop.close()

    except Exception as exc:
        logger.error(
            "analysis_task_error",
            task_id=task_id,
            exception=str(exc),
            exception_type=type(exc).__name__,
            retry_count=self.request.retries
        )

        # Retry on certain exceptions
        if self.request.retries < self.max_retries:
            # Exponential backoff
            countdown = 2 ** self.request.retries * 60  # 60s, 120s, 240s
            logger.info(
                "analysis_task_retrying",
                task_id=task_id,
                retry_count=self.request.retries + 1,
                countdown_seconds=countdown
            )
            raise self.retry(exc=exc, countdown=countdown)
        else:
            # Max retries reached, return error result
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(exc),
                "error_type": type(exc).__name__
            }

    finally:
        # Clear context
        clear_contextvars()


__all__ = ["process_image_analysis_task"]
