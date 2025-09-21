"""
Shared file utilities for Sentrix project
Utilidades de archivos compartidas para el proyecto Sentrix

Common file validation, processing, and metadata extraction functions
Funciones comunes de validación, procesamiento y extracción de metadatos de archivos
"""

import os
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from .image_formats import ImageFormatConverter, SUPPORTED_IMAGE_FORMATS


# Get supported extensions and MIME types from image formats module
SUPPORTED_IMAGE_EXTENSIONS = set(SUPPORTED_IMAGE_FORMATS.keys())
IMAGE_MIME_TYPES = {ext: format_info['mime_type'] for ext, format_info in SUPPORTED_IMAGE_FORMATS.items()}

# Maximum file sizes (in bytes)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_BATCH_SIZE = 100  # Maximum files in batch


def validate_file_extension(filename: str) -> bool:
    """
    Validate if file has supported image extension
    Validar si el archivo tiene una extensión de imagen soportada
    """
    if not filename:
        return False

    extension = Path(filename).suffix.lower()
    return extension in SUPPORTED_IMAGE_EXTENSIONS


def get_file_mime_type(filename: str) -> Optional[str]:
    """
    Get MIME type for file based on extension
    Obtener tipo MIME del archivo basado en la extensión
    """
    if not filename:
        return None

    extension = Path(filename).suffix.lower()
    return IMAGE_MIME_TYPES.get(extension)


def validate_file_size(file_path: Union[str, Path], max_size: int = MAX_FILE_SIZE) -> bool:
    """
    Validate file size is within limits
    Validar que el tamaño del archivo esté dentro de los límites
    """
    try:
        file_size = Path(file_path).stat().st_size
        return file_size <= max_size
    except (OSError, FileNotFoundError):
        return False


def validate_image_file(file_path: Union[str, Path]) -> Dict[str, any]:
    """
    Comprehensive image file validation with format conversion support
    Validación integral de archivo de imagen con soporte de conversión de formato
    """
    path = Path(file_path)
    converter = ImageFormatConverter()

    validation_result = {
        'is_valid': False,
        'filename': path.name,
        'extension': path.suffix.lower(),
        'errors': [],
        'format_info': None,
        'conversion_needed': False
    }

    # Check if file exists
    if not path.exists():
        validation_result['errors'].append('File does not exist')
        return validation_result

    # Check extension and get format info
    extension = path.suffix.lower()
    if extension not in SUPPORTED_IMAGE_FORMATS:
        validation_result['errors'].append(f'Unsupported extension: {path.suffix}')
    else:
        format_info = SUPPORTED_IMAGE_FORMATS[extension]
        validation_result['format_info'] = format_info
        validation_result['conversion_needed'] = format_info.get('conversion_needed', False)

        # Check if conversion dependencies are available
        if validation_result['conversion_needed']:
            dependencies_check = converter.check_dependencies()
            missing_deps = [dep for dep, available in dependencies_check.items() if not available]
            if missing_deps:
                validation_result['errors'].append(f'Missing dependencies for {extension} conversion: {missing_deps}')

    # Check file size
    if not validate_file_size(path):
        file_size_mb = path.stat().st_size / (1024 * 1024)
        validation_result['errors'].append(f'File too large: {file_size_mb:.1f}MB (max: {MAX_FILE_SIZE / (1024 * 1024)}MB)')

    # If no errors, file is valid
    if not validation_result['errors']:
        validation_result['is_valid'] = True
        validation_result['mime_type'] = get_file_mime_type(str(path))
        validation_result['size_bytes'] = path.stat().st_size

    return validation_result


def normalize_filename(filename: str, add_extension: bool = True) -> str:
    """
    Normalize filename for processing
    Normalizar nombre de archivo para procesamiento
    """
    if not filename:
        return "image.jpg"

    # Remove path components
    filename = Path(filename).name

    # Add extension if missing and requested
    if add_extension and not Path(filename).suffix:
        filename += '.jpg'

    return filename


def extract_filename_from_url(url: str) -> str:
    """
    Extract filename from URL
    Extraer nombre de archivo de URL
    """
    try:
        # Get the last part of URL path
        path = Path(url.split('?')[0])  # Remove query parameters
        filename = path.name

        # Ensure it has an image extension
        if not validate_file_extension(filename):
            filename += '.jpg'

        return filename
    except Exception:
        return "image.jpg"


def get_file_info(file_path: Union[str, Path]) -> Dict[str, any]:
    """
    Get comprehensive file information
    Obtener información integral del archivo
    """
    path = Path(file_path)

    try:
        stat = path.stat()
        return {
            'filename': path.name,
            'extension': path.suffix.lower(),
            'size_bytes': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'mime_type': get_file_mime_type(str(path)),
            'created_time': stat.st_ctime,
            'modified_time': stat.st_mtime,
            'is_valid_image': validate_file_extension(str(path))
        }
    except (OSError, FileNotFoundError):
        return {
            'filename': path.name,
            'extension': path.suffix.lower(),
            'error': 'File not accessible',
            'is_valid_image': False
        }


def find_images_in_directory(directory: Union[str, Path], recursive: bool = False) -> List[Path]:
    """
    Find all image files in directory
    Encontrar todos los archivos de imagen en el directorio
    """
    directory = Path(directory)

    if not directory.exists() or not directory.is_dir():
        return []

    image_files = []

    if recursive:
        pattern = "**/*"
    else:
        pattern = "*"

    for file_path in directory.glob(pattern):
        if file_path.is_file() and validate_file_extension(str(file_path)):
            image_files.append(file_path)

    return sorted(image_files)


def validate_batch_files(file_paths: List[Union[str, Path]], max_batch_size: int = MAX_BATCH_SIZE) -> Dict[str, any]:
    """
    Validate a batch of files
    Validar un lote de archivos
    """
    result = {
        'is_valid': True,
        'total_files': len(file_paths),
        'valid_files': [],
        'invalid_files': [],
        'errors': []
    }

    # Check batch size
    if len(file_paths) > max_batch_size:
        result['is_valid'] = False
        result['errors'].append(f'Batch too large: {len(file_paths)} files (max: {max_batch_size})')
        return result

    # Validate each file
    for file_path in file_paths:
        validation = validate_image_file(file_path)

        if validation['is_valid']:
            result['valid_files'].append(str(file_path))
        else:
            result['invalid_files'].append({
                'file': str(file_path),
                'errors': validation['errors']
            })

    # Overall validation
    if result['invalid_files']:
        result['is_valid'] = False
        result['errors'].append(f'{len(result["invalid_files"])} invalid files found')

    return result


def ensure_directory_exists(directory_path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if needed
    Asegurar que el directorio existe, crear si es necesario
    """
    directory = Path(directory_path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def safe_filename(filename: str, max_length: int = 255) -> str:
    """
    Create safe filename by removing invalid characters
    Crear nombre de archivo seguro removiendo caracteres inválidos
    """
    import re

    # Remove/replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Limit length
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        max_name_length = max_length - len(ext)
        filename = name[:max_name_length] + ext

    return filename


def get_temp_filepath(filename: str, temp_dir: Optional[Union[str, Path]] = None) -> Path:
    """
    Generate temporary file path
    Generar ruta de archivo temporal
    """
    import tempfile
    import uuid

    if temp_dir:
        temp_dir = Path(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)
    else:
        temp_dir = Path(tempfile.gettempdir())

    # Add unique identifier to avoid conflicts
    name, ext = os.path.splitext(filename)
    unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"

    return temp_dir / safe_filename(unique_filename)


def process_image_with_conversion(file_path: Union[str, Path], target_dir: Optional[Union[str, Path]] = None) -> Dict[str, any]:
    """
    Process image with automatic format conversion if needed
    Procesar imagen con conversión automática de formato si es necesario
    """
    path = Path(file_path)
    converter = ImageFormatConverter()

    result = {
        'success': False,
        'original_path': str(path),
        'processed_path': None,
        'conversion_performed': False,
        'format_info': None,
        'errors': []
    }

    # Validate the image first
    validation = validate_image_file(path)
    if not validation['is_valid']:
        result['errors'] = validation['errors']
        return result

    result['format_info'] = validation['format_info']

    # Check if conversion is needed
    if validation['conversion_needed']:
        try:
            # Set target directory
            if target_dir:
                target_directory = Path(target_dir)
            else:
                target_directory = path.parent

            # Convert the image
            converted_path = converter.convert_image(path, target_directory)

            result['processed_path'] = str(converted_path)
            result['conversion_performed'] = True
            result['success'] = True

        except Exception as e:
            result['errors'].append(f'Conversion failed: {str(e)}')
            return result
    else:
        # No conversion needed, use original file
        result['processed_path'] = str(path)
        result['success'] = True

    return result