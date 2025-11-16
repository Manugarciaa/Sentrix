"""
Celery Application Configuration for Sentrix Backend
Enables async task processing for long-running operations
"""

import os
from celery import Celery
from .logging_config import get_logger

logger = get_logger(__name__)

# Get Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "sentrix",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["src.tasks.analysis_tasks"]  # Auto-discover tasks
)

# Celery configuration
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task execution
    task_track_started=True,
    task_time_limit=300,  # 5 minutes hard limit
    task_soft_time_limit=270,  # 4.5 minutes soft limit

    # Worker configuration
    worker_prefetch_multiplier=1,  # Important for long-running tasks
    worker_max_tasks_per_child=50,  # Prevent memory leaks

    # Result backend
    result_expires=3600,  # Keep results for 1 hour
    result_extended=True,  # Store more metadata

    # Task routing
    task_routes={
        "src.tasks.analysis_tasks.*": {"queue": "analysis"},
    },

    # Monitoring
    task_send_sent_event=True,
    worker_send_task_events=True,
)

# Log configuration on startup
logger.info(
    "celery_app_configured",
    broker=REDIS_URL,
    backend=REDIS_URL,
    task_time_limit=celery_app.conf.task_time_limit
)


# Celery signals for logging
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery configuration"""
    logger.info(
        "celery_debug_task",
        task_id=self.request.id,
        task_name=self.name
    )
    return f"Request: {self.request!r}"


__all__ = ["celery_app"]
