"""
Shared file utilities for Sentrix project
Utilidades de archivos compartidas para el proyecto Sentrix

Common file validation, processing, and metadata extraction functions
Funciones comunes de validación, procesamiento y extracción de metadatos de archivos
"""

import os
import re
import uuid
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
# Handle both relative and absolute imports
try:
    from .image_formats import ImageFormatConverter, SUPPORTED_IMAGE_FORMATS
except ImportError:
    try:
        from image_formats import ImageFormatConverter, SUPPORTED_IMAGE_FORMATS
    except ImportError:
        # Fallback for minimal functionality without image_formats
        # Only show warning if not in testing mode
        if not os.getenv('TESTING_MODE', 'false').lower() == 'true':
            print("Info: image_formats module not available, using minimal functionality")
        SUPPORTED_IMAGE_FORMATS = {
            '.jpg': {'mime_type': 'image/jpeg', 'conversion_needed': False},
            '.jpeg': {'mime_type': 'image/jpeg', 'conversion_needed': False},
            '.png': {'mime_type': 'image/png', 'conversion_needed': False},
        }
        ImageFormatConverter = None


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


def generate_standardized_filename(
    original_filename: str,
    camera_info: Optional[Dict] = None,
    gps_data: Optional[Dict] = None,
    analysis_timestamp: Optional[datetime] = None
) -> str:
    """
    Generate standardized filename following Sentrix naming convention
    Generar nombre de archivo estandarizado siguiendo la convención de Sentrix

    Format: SENTRIX_YYYYMMDD_HHMMSS_DEVICE_LOCATION_ID.ext
    """
    # Get original extension
    original_ext = Path(original_filename).suffix.lower()
    if not original_ext:
        original_ext = '.jpg'

    # Use current time if not provided
    if analysis_timestamp is None:
        analysis_timestamp = datetime.now()

    # Format timestamp
    timestamp = analysis_timestamp.strftime("%Y%m%d_%H%M%S")

    # Detect device from camera info
    device_code = _detect_device_code(camera_info, original_filename)

    # Format location if available
    location_part = _format_location_code(gps_data)

    # Generate short unique ID
    unique_id = str(uuid.uuid4())[:8]

    # Build filename components
    components = [
        "SENTRIX",
        timestamp,
        device_code,
        location_part,
        unique_id
    ]

    # Filter out empty components
    components = [comp for comp in components if comp]

    # Join with underscores
    filename = "_".join(components) + original_ext

    return filename


def _detect_device_code(camera_info: Optional[Dict], original_filename: str) -> str:
    """
    Detect device type from camera info and filename patterns
    Detectar tipo de dispositivo desde información de cámara y patrones de nombre
    """
    if camera_info:
        make = (camera_info.get('camera_make') or '').upper()
        model = (camera_info.get('camera_model') or '').upper()

        # iPhone detection
        if 'APPLE' in make:
            if 'IPHONE' in model:
                # Extract iPhone model number
                iphone_match = re.search(r'IPHONE\s*(\d+)', model)
                if iphone_match:
                    return f"IPHONE{iphone_match.group(1)}"
                return "IPHONE"
            elif 'IPAD' in model:
                return "IPAD"
            return "APPLE"

        # Samsung detection
        elif 'SAMSUNG' in make:
            if 'GALAXY' in model:
                # Extract Galaxy model
                galaxy_match = re.search(r'(S\d+|NOTE\d+)', model)
                if galaxy_match:
                    return f"GALAXY{galaxy_match.group(1)}"
                return "GALAXY"
            return "SAMSUNG"

        # Canon, Nikon, etc.
        elif make in ['CANON', 'NIKON', 'SONY', 'FUJIFILM', 'OLYMPUS']:
            return make[:6]  # Limit to 6 chars

        # Generic camera
        elif make:
            return make[:8].replace(' ', '')

    # Fallback to filename pattern detection
    filename_upper = original_filename.upper()

    # iPhone patterns
    if any(pattern in filename_upper for pattern in ['IMG_', 'IMG-', 'PHOTO-']):
        return "IPHONE"

    # Screenshot patterns (check before Android to avoid false matches with date patterns)
    elif any(pattern in filename_upper for pattern in ['SCREENSHOT', 'SCREEN', 'CAPTURE']):
        return "SCREEN"

    # WhatsApp patterns
    elif 'WA' in filename_upper:
        return "WHATSAPP"

    # Android patterns (checked after Screenshot to avoid false positives)
    elif any(pattern in filename_upper for pattern in ['20', 'DSC', 'CAM']):
        return "ANDROID"

    return "UNKNOWN"


def _format_location_code(gps_data: Optional[Dict]) -> str:
    """
    Format GPS data into location code
    Formatear datos GPS en código de ubicación
    """
    if not gps_data or not gps_data.get('has_gps', False):
        return "NOLOC"

    lat = gps_data.get('latitude')
    lon = gps_data.get('longitude')

    if lat is None or lon is None:
        return "NOLOC"

    # Format coordinates with 3 decimal places for reasonable precision
    lat_str = f"LAT{lat:.3f}".replace('.', 'p').replace('-', 'n')
    lon_str = f"LON{lon:.3f}".replace('.', 'p').replace('-', 'n')

    return f"{lat_str}_{lon_str}"


def parse_standardized_filename(filename: str) -> Dict[str, any]:
    """
    Parse standardized filename to extract metadata
    Parsear nombre de archivo estandarizado para extraer metadatos
    """
    result = {
        'is_standardized': False,
        'project': None,
        'timestamp': None,
        'device': None,
        'location': None,
        'unique_id': None,
        'extension': None,
        'parsing_errors': []
    }

    try:
        # Remove extension
        name_without_ext = Path(filename).stem
        extension = Path(filename).suffix
        result['extension'] = extension

        # Split by underscores
        parts = name_without_ext.split('_')

        if len(parts) < 3:
            result['parsing_errors'].append("Insufficient parts in filename")
            return result

        # Check if starts with SENTRIX
        if parts[0] != 'SENTRIX':
            result['parsing_errors'].append("Does not start with SENTRIX")
            return result

        result['project'] = parts[0]
        result['is_standardized'] = True

        # Parse timestamp (should be parts[1] and parts[2])
        if len(parts) >= 3:
            try:
                timestamp_str = f"{parts[1]}_{parts[2]}"
                result['timestamp'] = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            except ValueError:
                result['parsing_errors'].append("Invalid timestamp format")

        # Parse device (parts[3])
        if len(parts) >= 4:
            result['device'] = parts[3]

        # Parse location (parts[4] and possibly parts[5])
        if len(parts) >= 5:
            location_part = parts[4]
            if len(parts) >= 6 and parts[5].startswith('LON'):
                location_part += f"_{parts[5]}"
                result['unique_id'] = parts[6] if len(parts) >= 7 else None
            else:
                result['unique_id'] = parts[5] if len(parts) >= 6 else None

            result['location'] = location_part

        # Parse unique ID (last part if not already parsed)
        if result['unique_id'] is None and len(parts) > 0:
            result['unique_id'] = parts[-1]

    except Exception as e:
        result['parsing_errors'].append(f"Parsing error: {str(e)}")

    return result


def create_filename_variations(base_filename: str, camera_info: Optional[Dict] = None, gps_data: Optional[Dict] = None) -> Dict[str, str]:
    """
    Create different filename variations for different use cases
    Crear diferentes variaciones de nombre de archivo para diferentes casos de uso
    """
    timestamp = datetime.now()

    standardized = generate_standardized_filename(base_filename, camera_info, gps_data, timestamp)

    return {
        'original': base_filename,
        'standardized': standardized,
        'processed': standardized.replace('SENTRIX_', 'SENTRIX_PROC_'),
        'thumbnail': standardized.replace(Path(standardized).suffix, '_thumb.jpg'),
        'analysis_id': str(uuid.uuid4()),
        'timestamp': timestamp.isoformat()
    }