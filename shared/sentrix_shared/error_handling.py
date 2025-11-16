"""
Shared error handling utilities for Sentrix project
Utilidades de manejo de errores compartidas para el proyecto Sentrix

Unified exception classes and error handling patterns
Clases de excepción unificadas y patrones de manejo de errores
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import traceback
from enum import Enum


class ErrorCode(str, Enum):
    """Standard error codes for Sentrix services"""

    # General errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"

    # File processing errors
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_FILE_FORMAT = "INVALID_FILE_FORMAT"
    FILE_PROCESSING_ERROR = "FILE_PROCESSING_ERROR"

    # Image processing errors
    IMAGE_PROCESSING_ERROR = "IMAGE_PROCESSING_ERROR"
    GPS_EXTRACTION_ERROR = "GPS_EXTRACTION_ERROR"
    INVALID_IMAGE_FORMAT = "INVALID_IMAGE_FORMAT"

    # Model errors
    MODEL_NOT_FOUND = "MODEL_NOT_FOUND"
    MODEL_LOADING_ERROR = "MODEL_LOADING_ERROR"
    INFERENCE_ERROR = "INFERENCE_ERROR"

    # Database errors
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_QUERY_ERROR = "DATABASE_QUERY_ERROR"
    RECORD_NOT_FOUND = "RECORD_NOT_FOUND"
    DUPLICATE_RECORD = "DUPLICATE_RECORD"

    # Service communication errors
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    SERVICE_TIMEOUT = "SERVICE_TIMEOUT"
    EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"

    # Business logic errors
    RISK_ASSESSMENT_ERROR = "RISK_ASSESSMENT_ERROR"
    DETECTION_ERROR = "DETECTION_ERROR"
    VALIDATION_FAILED = "VALIDATION_FAILED"


class SentrixError(Exception):
    """
    Base exception class for Sentrix services
    Clase base de excepción para servicios Sentrix
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.original_exception = original_exception
        self.timestamp = datetime.now().isoformat()
        self.traceback = traceback.format_exc() if original_exception else None

        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            'error': True,
            'error_code': self.error_code.value,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp
        }

    def __str__(self) -> str:
        return f"[{self.error_code.value}] {self.message}"


class ValidationError(SentrixError):
    """Validation error exception"""

    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        details = {}
        if field:
            details['field'] = field
        if value is not None:
            details['value'] = str(value)

        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            details=details
        )


class FileProcessingError(SentrixError):
    """File processing error exception"""

    def __init__(self, message: str, file_path: Optional[str] = None, file_size: Optional[int] = None):
        details = {}
        if file_path:
            details['file_path'] = file_path
        if file_size:
            details['file_size'] = file_size

        super().__init__(
            message=message,
            error_code=ErrorCode.FILE_PROCESSING_ERROR,
            details=details
        )


class ImageProcessingError(SentrixError):
    """Image processing error exception"""

    def __init__(self, message: str, image_path: Optional[str] = None, operation: Optional[str] = None):
        details = {}
        if image_path:
            details['image_path'] = image_path
        if operation:
            details['operation'] = operation

        super().__init__(
            message=message,
            error_code=ErrorCode.IMAGE_PROCESSING_ERROR,
            details=details
        )


class ModelError(SentrixError):
    """Model-related error exception"""

    def __init__(self, message: str, model_path: Optional[str] = None, model_type: Optional[str] = None):
        details = {}
        if model_path:
            details['model_path'] = model_path
        if model_type:
            details['model_type'] = model_type

        super().__init__(
            message=message,
            error_code=ErrorCode.MODEL_LOADING_ERROR,
            details=details
        )


class DatabaseError(SentrixError):
    """Database-related error exception"""

    def __init__(self, message: str, query: Optional[str] = None, table: Optional[str] = None):
        details = {}
        if query:
            details['query'] = query
        if table:
            details['table'] = table

        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_QUERY_ERROR,
            details=details
        )


class ServiceError(SentrixError):
    """Service communication error exception"""

    def __init__(self, message: str, service_name: Optional[str] = None, endpoint: Optional[str] = None):
        details = {}
        if service_name:
            details['service_name'] = service_name
        if endpoint:
            details['endpoint'] = endpoint

        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_UNAVAILABLE,
            details=details
        )


def handle_exception(
    exception: Exception,
    logger,
    context: Optional[Dict[str, Any]] = None,
    reraise: bool = True
) -> Optional[SentrixError]:
    """
    Unified exception handler
    Manejador unificado de excepciones

    Args:
        exception: Exception to handle
        logger: Logger instance
        context: Additional context information
        reraise: Whether to reraise the exception

    Returns:
        SentrixError instance if not reraising
    """
    context = context or {}

    # Convert known exceptions to SentrixError
    if isinstance(exception, SentrixError):
        sentrix_error = exception
    else:
        # Map common exceptions
        error_mapping = {
            FileNotFoundError: (ErrorCode.FILE_NOT_FOUND, "File not found"),
            PermissionError: (ErrorCode.FORBIDDEN, "Permission denied"),
            ValueError: (ErrorCode.VALIDATION_ERROR, "Invalid value"),
            ConnectionError: (ErrorCode.SERVICE_UNAVAILABLE, "Connection failed"),
            TimeoutError: (ErrorCode.SERVICE_TIMEOUT, "Operation timed out")
        }

        error_code, default_message = error_mapping.get(
            type(exception),
            (ErrorCode.INTERNAL_ERROR, "Internal error")
        )

        sentrix_error = SentrixError(
            message=str(exception) or default_message,
            error_code=error_code,
            details=context,
            original_exception=exception
        )

    # Log the error
    log_message = f"Error occurred: {sentrix_error}"
    if context:
        log_message += f" | Context: {context}"

    logger.error(log_message, exc_info=True)

    if reraise:
        raise sentrix_error
    else:
        return sentrix_error


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """
    Validate that required fields are present
    Validar que los campos requeridos estén presentes
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]

    if missing_fields:
        raise ValidationError(
            message=f"Missing required fields: {', '.join(missing_fields)}",
            details={'missing_fields': missing_fields}
        )


def validate_file_size(file_size: int, max_size: int, filename: Optional[str] = None) -> None:
    """
    Validate file size
    Validar tamaño de archivo
    """
    if file_size > max_size:
        raise FileProcessingError(
            message=f"File too large: {file_size} bytes (max: {max_size} bytes)",
            file_path=filename,
            file_size=file_size
        )


def validate_image_format(filename: str, allowed_extensions: List[str]) -> None:
    """
    Validate image format
    Validar formato de imagen
    """
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        raise ValidationError(
            message=f"Invalid file format. Allowed: {', '.join(allowed_extensions)}",
            field="filename",
            value=filename
        )


def safe_execute(
    operation,
    logger,
    operation_name: str,
    context: Optional[Dict[str, Any]] = None,
    default_return=None
):
    """
    Safely execute an operation with error handling
    Ejecutar una operación de forma segura con manejo de errores
    """
    try:
        return operation()
    except Exception as e:
        error_context = {'operation': operation_name}
        if context:
            error_context.update(context)

        handle_exception(e, logger, error_context, reraise=False)
        return default_return


class ErrorRecorder:
    """
    Record and track errors for analysis
    Registrar y rastrear errores para análisis
    """

    def __init__(self):
        self.errors: List[Dict[str, Any]] = []

    def record_error(self, error: SentrixError, context: Optional[Dict[str, Any]] = None):
        """Record an error for tracking"""
        error_record = error.to_dict()
        if context:
            error_record['context'] = context

        self.errors.append(error_record)

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recorded errors"""
        if not self.errors:
            return {'total_errors': 0, 'error_codes': {}}

        error_codes = {}
        for error in self.errors:
            code = error['error_code']
            error_codes[code] = error_codes.get(code, 0) + 1

        return {
            'total_errors': len(self.errors),
            'error_codes': error_codes,
            'latest_error': self.errors[-1] if self.errors else None
        }

    def clear_errors(self):
        """Clear recorded errors"""
        self.errors.clear()


# Global error recorder instance
error_recorder = ErrorRecorder()


def create_error_response(error: SentrixError, include_details: bool = True) -> Dict[str, Any]:
    """
    Create standardized error response for APIs
    Crear respuesta de error estandarizada para APIs
    """
    response = {
        'success': False,
        'error': {
            'code': error.error_code.value,
            'message': error.message,
            'timestamp': error.timestamp
        }
    }

    if include_details and error.details:
        response['error']['details'] = error.details

    return response