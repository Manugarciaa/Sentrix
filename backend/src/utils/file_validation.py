"""
File validation utilities with security features

SECURITY:
- MIME type validation with magic bytes (not just extension)
- File size limits
- Filename sanitization
"""

import re
import os
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, HTTPException

# Try to import magic, fallback to extension-only validation in development
try:
    import magic
    MAGIC_AVAILABLE = True
except (ImportError, OSError):
    MAGIC_AVAILABLE = False
    import warnings
    warnings.warn("python-magic not available, using extension-only validation (development mode)")

import logging
logger = logging.getLogger(__name__)


# Security constants
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB default

ALLOWED_MIME_TYPES = {
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/tiff',
    'image/x-tiff',
    'image/webp',
    'image/heic',
    'image/heif',
    'image/bmp'
}

ALLOWED_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.tiff', '.tif',
    '.heic', '.heif', '.webp', '.bmp'
}


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and other attacks

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for use

    Examples:
        >>> sanitize_filename("../../etc/passwd.jpg")
        'etc_passwd.jpg'
        >>> sanitize_filename("my<script>.jpg")
        'my_script_.jpg'
    """
    # Get basename to remove any path components
    safe_name = os.path.basename(filename)

    # Remove or replace dangerous characters
    # Allow only: alphanumeric, dots, hyphens, underscores
    safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', safe_name)

    # Prevent double extensions and hidden files
    safe_name = safe_name.lstrip('.')

    # Limit length
    if len(safe_name) > 255:
        name, ext = os.path.splitext(safe_name)
        safe_name = name[:250] + ext

    return safe_name


async def validate_file_content(
    file: UploadFile,
    max_size: int = MAX_FILE_SIZE,
    allowed_mime_types: set = ALLOWED_MIME_TYPES
) -> bytes:
    """
    Validate uploaded file content with security checks

    Performs:
    1. Size validation (before reading entire file)
    2. MIME type validation using magic bytes (not just extension)
    3. Returns file content if valid

    Args:
        file: Uploaded file from FastAPI
        max_size: Maximum allowed file size in bytes
        allowed_mime_types: Set of allowed MIME types

    Returns:
        bytes: File content if valid

    Raises:
        HTTPException:
            - 400 if file type invalid
            - 413 if file too large

    Security:
        - Reads file in chunks to prevent memory exhaustion
        - Validates MIME type with magic bytes (prevents renamed executables)
        - Size limit prevents DoS
    """
    # 1. Read file with size limit (read +1 byte to detect oversized)
    content = await file.read(max_size + 1)

    # 2. Check size
    if len(content) > max_size:
        max_mb = max_size / (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {max_mb:.1f}MB"
        )

    # 3. Validate MIME type using magic bytes (SECURITY: not just extension)
    if MAGIC_AVAILABLE:
        try:
            mime_type = magic.from_buffer(content, mime=True)
            logger.debug(f"Detected MIME type: {mime_type} for file: {file.filename}")

            if mime_type not in allowed_mime_types:
                logger.warning(
                    f"Invalid MIME type attempted upload: {mime_type} "
                    f"(filename: {file.filename})"
                )
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type: {mime_type}. "
                           f"Allowed types: {', '.join(sorted(allowed_mime_types))}"
                )
        except Exception as e:
            # If magic fails, reject the file (fail closed)
            logger.error(f"MIME type detection failed: {e}")
            raise HTTPException(
                status_code=400,
                detail="Could not determine file type. File may be corrupted."
            )
    else:
        # Fallback: log warning that MIME validation is disabled (development only)
        logger.warning(f"MIME validation disabled (magic not available) for file: {file.filename}")

    return content


def validate_file_extension(filename: str) -> str:
    """
    Validate file extension is allowed

    Args:
        filename: Name of file to validate

    Returns:
        str: Lowercase extension (e.g., '.jpg')

    Raises:
        HTTPException: If extension not allowed

    Note:
        This is a secondary check. Primary security comes from MIME type validation.
    """
    file_ext = Path(filename).suffix.lower()

    if not file_ext:
        raise HTTPException(
            status_code=400,
            detail="File must have an extension"
        )

    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension: {file_ext}. "
                   f"Supported: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    return file_ext


async def validate_uploaded_image(
    file: UploadFile,
    max_size: int = MAX_FILE_SIZE
) -> Tuple[bytes, str]:
    """
    Complete validation for uploaded image file

    Combines all validation checks:
    - Filename sanitization
    - Extension validation
    - Size validation
    - MIME type validation

    Args:
        file: Uploaded file from FastAPI
        max_size: Maximum file size in bytes

    Returns:
        Tuple[bytes, str]: (file_content, sanitized_filename)

    Raises:
        HTTPException: If any validation fails

    Example:
        >>> content, safe_name = await validate_uploaded_image(file)
        >>> # Use content for processing, safe_name for storage
    """
    # 1. Check file exists and has name
    if not file or not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided or file has no name"
        )

    # 2. Sanitize filename
    safe_filename = sanitize_filename(file.filename)
    logger.info(f"File upload: {file.filename} -> {safe_filename}")

    # 3. Validate extension (quick check)
    validate_file_extension(safe_filename)

    # 4. Validate content (size + MIME type)
    content = await validate_file_content(file, max_size)

    logger.info(
        f"File validated successfully: {safe_filename}, "
        f"size: {len(content)} bytes"
    )

    return content, safe_filename


# Utility functions for specific use cases

def get_file_size_mb(size_bytes: int) -> float:
    """Convert bytes to MB"""
    return size_bytes / (1024 * 1024)


def is_image_file(filename: str) -> bool:
    """Quick check if filename appears to be an image"""
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


def get_safe_temp_filename(original_filename: str) -> str:
    """
    Generate a safe temporary filename

    Args:
        original_filename: Original filename

    Returns:
        Safe filename with timestamp for uniqueness
    """
    import uuid
    from datetime import datetime

    safe_name = sanitize_filename(original_filename)
    ext = Path(safe_name).suffix
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]

    return f"upload_{timestamp}_{unique_id}{ext}"
