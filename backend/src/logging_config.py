"""
Structured Logging Configuration for Sentrix Backend
Provides JSON logging with correlation IDs for tracing requests across services
"""

import os
import logging
import structlog
from contextvars import ContextVar
from typing import Optional

# Context variable for request ID (thread-safe across async contexts)
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


def setup_logging(log_level: str = "INFO") -> structlog.BoundLogger:
    """
    Configure structured JSON logging for the application

    Features:
    - JSON output for easy parsing by log aggregators
    - Automatic timestamp in ISO format
    - Context variables (request_id, user_id) automatically included
    - Log level filtering
    - Exception info rendering

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured structlog logger instance
    """

    # Determine if we're in development mode
    environment = os.getenv("ENVIRONMENT", "development")
    is_development = environment == "development"

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper()),
        force=True,
    )

    # Silence noisy loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.dialects").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.orm").setLevel(logging.WARNING)

    # Choose processors based on environment
    if is_development:
        # Development: Use console-friendly output with colors
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        # Production: Use JSON output for log aggregators
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logger = structlog.get_logger()

    if is_development:
        logger.info(
            "Structured logging configured",
            environment=environment,
            log_level=log_level,
            output_format="console"
        )
    else:
        logger.info(
            "Structured logging configured",
            environment=environment,
            log_level=log_level,
            output_format="json"
        )

    return logger


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """
    Get a logger instance with the given name

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured structlog logger
    """
    if name:
        return structlog.get_logger(name)
    return structlog.get_logger()


def bind_contextvars(request_id: Optional[str] = None, user_id: Optional[str] = None):
    """
    Bind context variables to be included in all log messages

    Args:
        request_id: Unique request ID for tracing
        user_id: Authenticated user ID
    """
    if request_id:
        request_id_var.set(request_id)
        structlog.contextvars.bind_contextvars(request_id=request_id)

    if user_id:
        user_id_var.set(user_id)
        structlog.contextvars.bind_contextvars(user_id=user_id)


def clear_contextvars():
    """Clear all context variables"""
    structlog.contextvars.clear_contextvars()
    request_id_var.set(None)
    user_id_var.set(None)


def get_request_id() -> Optional[str]:
    """Get current request ID from context"""
    return request_id_var.get()


def get_user_id() -> Optional[str]:
    """Get current user ID from context"""
    return user_id_var.get()


__all__ = [
    "setup_logging",
    "get_logger",
    "bind_contextvars",
    "clear_contextvars",
    "get_request_id",
    "get_user_id",
    "request_id_var",
    "user_id_var",
]
