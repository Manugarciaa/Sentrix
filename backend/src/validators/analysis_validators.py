"""
Input validators for analysis endpoints

Validates user input before processing, raising appropriate exceptions
for invalid data. Keeps validation logic separate from API layer.
"""

from typing import Optional, Tuple
from fastapi import HTTPException, UploadFile
from sentrix_shared.image_formats import is_format_supported, SUPPORTED_IMAGE_FORMATS

from ..config import get_settings
from ..exceptions import (
    FileValidationException,
    CoordinateValidationException,
    ThresholdValidationException
)

settings = get_settings()


def validate_upload_file(file: Optional[UploadFile]) -> None:
    """
    Validate uploaded file exists and has valid name.

    Args:
        file: FastAPI UploadFile object

    Raises:
        HTTPException: If file is missing or invalid
    """
    if not file:
        raise HTTPException(
            status_code=400,
            detail="Se requiere un archivo de imagen"
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="El archivo debe tener un nombre valido"
        )


def validate_file_extension(filename: str) -> str:
    """
    Validate file has supported image extension.

    Args:
        filename: Name of uploaded file

    Returns:
        str: Lowercased file extension (e.g., '.jpg')

    Raises:
        HTTPException: If extension is not supported
    """
    file_ext = '.' + filename.split('.')[-1].lower()

    if not is_format_supported(file_ext):
        supported_formats = list(SUPPORTED_IMAGE_FORMATS.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado: {file_ext}. Formatos soportados: {', '.join(supported_formats)}"
        )

    return file_ext


def validate_file_size(image_data: bytes, max_size: Optional[int] = None) -> None:
    """
    Validate file size is within allowed limits.

    Args:
        image_data: Raw image bytes
        max_size: Maximum size in bytes (defaults to settings.max_file_size)

    Raises:
        HTTPException: If file exceeds maximum size
    """
    max_size = max_size or settings.max_file_size

    if len(image_data) > max_size:
        max_mb = max_size // (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"El archivo es demasiado grande. Maximo {max_mb}MB"
        )


def validate_coordinates(
    latitude: Optional[float],
    longitude: Optional[float]
) -> None:
    """
    Validate GPS coordinates are both provided or both missing.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Raises:
        HTTPException: If only one coordinate is provided
    """
    if (latitude is not None and longitude is None) or (longitude is not None and latitude is None):
        raise HTTPException(
            status_code=400,
            detail="Si proporciona coordenadas, tanto latitud como longitud son requeridas"
        )


def validate_confidence_threshold(threshold: float) -> None:
    """
    Validate confidence threshold is in valid range [0.1, 1.0].

    Args:
        threshold: Confidence threshold value

    Raises:
        HTTPException: If threshold is outside valid range
    """
    if not 0.1 <= threshold <= 1.0:
        raise HTTPException(
            status_code=400,
            detail="confidence_threshold debe estar entre 0.1 y 1.0"
        )


def validate_batch_size(size: int, max_size: int = 50) -> None:
    """
    Validate batch request size.

    Args:
        size: Number of items in batch
        max_size: Maximum allowed batch size

    Raises:
        HTTPException: If batch size exceeds limit
    """
    if size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {max_size} images per batch"
        )


def validate_analysis_request(
    file: Optional[UploadFile],
    latitude: Optional[float],
    longitude: Optional[float],
    confidence_threshold: float,
    image_data: Optional[bytes] = None
) -> None:
    """
    Validate complete analysis request.

    Runs all validations for image upload analysis endpoint.

    Args:
        file: Uploaded file
        latitude: Optional latitude
        longitude: Optional longitude
        confidence_threshold: Detection threshold
        image_data: Optional pre-read image data for size validation

    Raises:
        HTTPException: If any validation fails
    """
    # Validate file
    validate_upload_file(file)
    validate_file_extension(file.filename)

    # Validate coordinates
    validate_coordinates(latitude, longitude)

    # Validate threshold
    validate_confidence_threshold(confidence_threshold)

    # Validate size if data provided
    if image_data:
        validate_file_size(image_data)
