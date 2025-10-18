"""
Shared logging utilities for Sentrix project
Utilidades de logging compartidas para el proyecto Sentrix

Unified logging configuration and utilities used by both backend and yolo-service
Configuración de logging unificada y utilidades usadas por backend y yolo-service
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


# Default logging configuration
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Log levels mapping
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}


def setup_logger(
    name: str,
    level: str = 'INFO',
    log_file: Optional[Path] = None,
    console_output: bool = True,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Setup a logger with consistent configuration
    Configurar un logger con configuración consistente

    Args:
        name: Logger name (usually __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for file logging
        console_output: Whether to output to console
        format_string: Custom format string

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Set level
    log_level = LOG_LEVELS.get(level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        format_string or DEFAULT_LOG_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT
    )

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_service_logger(service_name: str, log_level: str = 'INFO') -> logging.Logger:
    """
    Get a logger configured for a specific service
    Obtener un logger configurado para un servicio específico

    Args:
        service_name: Name of the service (backend, yolo-service, etc.)
        log_level: Log level

    Returns:
        Configured logger for the service
    """
    # Create logs directory
    logs_dir = Path('logs')
    log_file = logs_dir / f'{service_name}.log'

    return setup_logger(
        name=f'sentrix.{service_name}',
        level=log_level,
        log_file=log_file,
        console_output=True
    )


def get_module_logger(module_name: str, service_name: str = 'app') -> logging.Logger:
    """
    Get a logger for a specific module within a service
    Obtener un logger para un módulo específico dentro de un servicio

    Args:
        module_name: Name of the module (usually __name__)
        service_name: Name of the parent service

    Returns:
        Configured logger for the module
    """
    return logging.getLogger(f'sentrix.{service_name}.{module_name}')


def log_function_call(logger: logging.Logger, func_name: str, **kwargs):
    """
    Log function call with parameters
    Registrar llamada a función con parámetros
    """
    params = ', '.join(f'{k}={v}' for k, v in kwargs.items())
    logger.debug(f'Calling {func_name}({params})')


def log_performance(logger: logging.Logger, operation: str, duration_ms: float, **context):
    """
    Log performance metrics
    Registrar métricas de rendimiento
    """
    context_str = ', '.join(f'{k}={v}' for k, v in context.items()) if context else ''
    logger.info(f'Performance: {operation} took {duration_ms:.2f}ms ({context_str})')


def log_error_with_context(logger: logging.Logger, error: Exception, context: Dict[str, Any]):
    """
    Log error with additional context
    Registrar error con contexto adicional
    """
    context_str = ', '.join(f'{k}={v}' for k, v in context.items())
    logger.error(f'Error: {str(error)} | Context: {context_str}', exc_info=True)


def log_detection_result(logger: logging.Logger, image_path: str, detections_count: int, processing_time_ms: float):
    """
    Log detection result in a standardized format
    Registrar resultado de detección en formato estandarizado
    """
    logger.info(f'Detection completed: {image_path} | Detections: {detections_count} | Time: {processing_time_ms:.2f}ms')


def log_batch_progress(logger: logging.Logger, current: int, total: int, operation: str):
    """
    Log batch processing progress
    Registrar progreso de procesamiento en lotes
    """
    percentage = (current / total) * 100 if total > 0 else 0
    logger.info(f'{operation} progress: {current}/{total} ({percentage:.1f}%)')


def log_system_info(logger: logging.Logger, service_name: str, version: str):
    """
    Log system startup information
    Registrar información de inicio del sistema
    """
    logger.info(f'Starting {service_name} v{version}')
    logger.info(f'Python version: {sys.version}')
    logger.info(f'Working directory: {Path.cwd()}')


def log_config_loaded(logger: logging.Logger, config_file: str, config_keys: list):
    """
    Log configuration loading
    Registrar carga de configuración
    """
    logger.info(f'Configuration loaded from: {config_file}')
    logger.debug(f'Configuration keys: {", ".join(config_keys)}')


def log_model_info(logger: logging.Logger, model_path: str, model_size_mb: float):
    """
    Log model loading information
    Registrar información de carga de modelo
    """
    logger.info(f'Model loaded: {model_path} ({model_size_mb:.1f}MB)')


def log_api_request(logger: logging.Logger, method: str, endpoint: str, status_code: int, duration_ms: float):
    """
    Log API request in standardized format
    Registrar petición API en formato estandarizado
    """
    logger.info(f'API {method} {endpoint} - {status_code} - {duration_ms:.2f}ms')


# Convenience functions for common logging patterns
def setup_backend_logging(log_level: str = 'INFO') -> logging.Logger:
    """Setup logging for backend service"""
    return get_service_logger('backend', log_level)


def setup_yolo_logging(log_level: str = 'INFO') -> logging.Logger:
    """Setup logging for YOLO service"""
    return get_service_logger('yolo-service', log_level)


def setup_shared_logging(log_level: str = 'INFO') -> logging.Logger:
    """Setup logging for shared libraries"""
    return get_service_logger('shared', log_level)


class ProgressLogger:
    """
    Context manager for logging progress of long-running operations
    Gestor de contexto para registrar progreso de operaciones de larga duración
    """

    def __init__(self, logger: logging.Logger, operation: str, total_items: int):
        self.logger = logger
        self.operation = operation
        self.total_items = total_items
        self.current_item = 0
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f'Starting {self.operation} ({self.total_items} items)')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        if exc_type is None:
            self.logger.info(f'Completed {self.operation} in {duration:.2f}s')
        else:
            self.logger.error(f'Failed {self.operation} after {duration:.2f}s: {exc_val}')

    def update(self, increment: int = 1):
        """Update progress counter"""
        self.current_item += increment
        if self.current_item % max(1, self.total_items // 10) == 0:  # Log every 10%
            log_batch_progress(self.logger, self.current_item, self.total_items, self.operation)