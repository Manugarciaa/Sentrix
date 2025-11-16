"""
Sentrix Shared Library

Shared utilities and common code for the Sentrix platform.
"""

__version__ = "1.0.0"

# Re-export commonly used modules for convenience
from . import risk_assessment
from . import image_formats
from . import gps_utils
from . import data_models

# Re-export commonly used functions and constants
from .image_formats import (
    is_format_supported,
    SUPPORTED_IMAGE_FORMATS,
    LEGACY_IMAGE_FORMATS,
    get_format_info,
    needs_conversion,
    ImageFormatConverter,
    validate_and_convert_image,
)

__all__ = [
    "risk_assessment",
    "image_formats",
    "gps_utils",
    "data_models",
    # Image format utilities
    "is_format_supported",
    "SUPPORTED_IMAGE_FORMATS",
    "LEGACY_IMAGE_FORMATS",
    "get_format_info",
    "needs_conversion",
    "ImageFormatConverter",
    "validate_and_convert_image",
]
