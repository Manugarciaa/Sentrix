"""
Custom exceptions for Sentrix Backend

Domain-specific exceptions that provide better error handling,
clearer error messages, and proper HTTP status code mapping.
"""

from typing import Optional, Dict, Any


class SentrixException(Exception):
    """Base exception for all Sentrix-specific errors"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# ============================================
# Validation Exceptions (4xx errors)
# ============================================

class ValidationException(SentrixException):
    """Raised when input validation fails"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class FileValidationException(ValidationException):
    """Raised when file validation fails"""
    pass


class CoordinateValidationException(ValidationException):
    """Raised when GPS coordinate validation fails"""
    pass


class ThresholdValidationException(ValidationException):
    """Raised when threshold parameter is invalid"""
    pass


# ============================================
# Resource Exceptions (404, 409 errors)
# ============================================

class ResourceNotFoundException(SentrixException):
    """Raised when a requested resource is not found"""

    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with ID '{resource_id}' not found"
        super().__init__(message, status_code=404, details={
            "resource_type": resource_type,
            "resource_id": resource_id
        })


class AnalysisNotFoundException(ResourceNotFoundException):
    """Raised when analysis is not found"""

    def __init__(self, analysis_id: str):
        super().__init__("Analysis", analysis_id)


class UserNotFoundException(ResourceNotFoundException):
    """Raised when user is not found"""

    def __init__(self, user_id: str):
        super().__init__("User", user_id)


class DuplicateResourceException(SentrixException):
    """Raised when attempting to create a duplicate resource"""

    def __init__(self, resource_type: str, identifier: str):
        message = f"{resource_type} with identifier '{identifier}' already exists"
        super().__init__(message, status_code=409, details={
            "resource_type": resource_type,
            "identifier": identifier
        })


# ============================================
# External Service Exceptions (502, 503, 504 errors)
# ============================================

class ExternalServiceException(SentrixException):
    """Base exception for external service errors"""

    def __init__(self, service_name: str, message: str, status_code: int = 502):
        super().__init__(
            f"{service_name} error: {message}",
            status_code=status_code,
            details={"service": service_name}
        )


class YOLOServiceException(ExternalServiceException):
    """Raised when YOLO service fails"""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__("YOLO Service", message, status_code)


class YOLOTimeoutException(YOLOServiceException):
    """Raised when YOLO service request times out"""

    def __init__(self, timeout_seconds: float):
        super().__init__(
            f"YOLO service timed out after {timeout_seconds}s",
            status_code=504
        )


class DatabaseException(ExternalServiceException):
    """Raised when database operation fails"""

    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__("Database", message, status_code=503)
        if operation:
            self.details["operation"] = operation


class CacheException(ExternalServiceException):
    """Raised when cache operation fails"""

    def __init__(self, message: str):
        super().__init__("Cache", message, status_code=503)


# ============================================
# Processing Exceptions (422, 500 errors)
# ============================================

class ProcessingException(SentrixException):
    """Raised when image processing fails"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)


class ImageProcessingException(ProcessingException):
    """Raised when image processing/conversion fails"""
    pass


class DetectionException(ProcessingException):
    """Raised when object detection fails"""
    pass


class GPSExtractionException(ProcessingException):
    """Raised when GPS metadata extraction fails"""
    pass


# ============================================
# Business Logic Exceptions
# ============================================

class RiskAssessmentException(SentrixException):
    """Raised when risk assessment calculation fails"""

    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class BatchProcessingException(SentrixException):
    """Raised when batch processing fails"""

    def __init__(self, message: str, failed_count: int, total_count: int):
        super().__init__(message, status_code=207, details={
            "failed_count": failed_count,
            "total_count": total_count
        })


# ============================================
# Configuration Exceptions
# ============================================

class ConfigurationException(SentrixException):
    """Raised when configuration is invalid or missing"""

    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message, status_code=500)
        if config_key:
            self.details["config_key"] = config_key


# ============================================
# Helper Functions
# ============================================

def to_http_exception(exc: SentrixException):
    """
    Convert a SentrixException to a FastAPI HTTPException

    Args:
        exc: SentrixException instance

    Returns:
        HTTPException with appropriate status code and detail
    """
    from fastapi import HTTPException

    detail = {
        "message": exc.message,
        "details": exc.details
    } if exc.details else exc.message

    return HTTPException(
        status_code=exc.status_code,
        detail=detail
    )
