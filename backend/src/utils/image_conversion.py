"""
Image conversion utilities for handling different formats including HEIC
Utilidades de conversión de imágenes para manejar diferentes formatos incluyendo HEIC
"""

import io
from typing import Optional, Tuple
from PIL import Image
import logging

try:
    import pillow_heif
    HEIF_AVAILABLE = True
    # Register HEIF plugin to allow PIL to read HEIC files
    pillow_heif.register_heif_opener()
except ImportError:
    HEIF_AVAILABLE = False

logger = logging.getLogger(__name__)


def is_heic_format(filename: str) -> bool:
    """Check if file is HEIC format based on extension"""
    return filename.lower().endswith(('.heic', '.heif'))


def convert_heic_to_jpeg(image_data: bytes, quality: int = 95) -> Tuple[bytes, str]:
    """
    Convert HEIC image to JPEG format

    Args:
        image_data: Raw HEIC image bytes
        quality: JPEG quality (1-100)

    Returns:
        Tuple of (converted_jpeg_bytes, new_filename)

    Raises:
        ImportError: If pillow-heif is not available
        Exception: If conversion fails
    """
    if not HEIF_AVAILABLE:
        raise ImportError("pillow-heif not available. Install with: pip install pillow-heif")

    try:
        # Open HEIC image using PIL (with pillow-heif plugin)
        image = Image.open(io.BytesIO(image_data))

        # Convert to RGB if necessary (HEIC might be in different color space)
        if image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')

        # Save as JPEG
        jpeg_buffer = io.BytesIO()
        image.save(jpeg_buffer, format='JPEG', quality=quality, optimize=True)

        jpeg_data = jpeg_buffer.getvalue()

        logger.info(f"HEIC converted to JPEG: {len(image_data)} -> {len(jpeg_data)} bytes")

        return jpeg_data, "converted_image.jpg"

    except Exception as e:
        logger.error(f"HEIC conversion failed: {e}")
        raise Exception(f"Failed to convert HEIC to JPEG: {e}")


def prepare_image_for_processing(image_data: bytes, filename: str) -> Tuple[bytes, str]:
    """
    Prepare image for processing, converting HEIC to JPEG if needed

    Args:
        image_data: Raw image bytes
        filename: Original filename

    Returns:
        Tuple of (processed_image_bytes, processed_filename)
    """
    if is_heic_format(filename):
        logger.info(f"Converting HEIC image: {filename}")
        return convert_heic_to_jpeg(image_data)

    # Return as-is for other formats
    return image_data, filename


def get_supported_formats() -> list:
    """Get list of supported image formats"""
    formats = ['.jpg', '.jpeg', '.png', '.tiff', '.tif']

    if HEIF_AVAILABLE:
        formats.extend(['.heic', '.heif'])

    return formats