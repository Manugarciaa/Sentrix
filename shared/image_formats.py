"""
Advanced image format support for Sentrix project
Soporte avanzado de formatos de imagen para el proyecto Sentrix

Comprehensive support for modern image formats including HEIC/HEIF, WebP, AVIF, and more
Soporte integral para formatos de imagen modernos incluyendo HEIC/HEIF, WebP, AVIF, y más
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from io import BytesIO
import logging

from .logging_utils import get_module_logger
from .error_handling import ImageProcessingError, ValidationError

logger = get_module_logger(__name__, 'shared')


# Comprehensive image format support
SUPPORTED_IMAGE_FORMATS = {
    # Standard formats
    '.jpg': {
        'mime_type': 'image/jpeg',
        'description': 'JPEG image',
        'conversion_needed': False,
        'quality_lossy': True,
        'supports_exif': True,
        'common_source': 'Most cameras and devices'
    },
    '.jpeg': {
        'mime_type': 'image/jpeg',
        'description': 'JPEG image',
        'conversion_needed': False,
        'quality_lossy': True,
        'supports_exif': True,
        'common_source': 'Most cameras and devices'
    },
    '.png': {
        'mime_type': 'image/png',
        'description': 'PNG image',
        'conversion_needed': False,
        'quality_lossy': False,
        'supports_exif': False,
        'common_source': 'Screenshots, graphics'
    },
    '.tiff': {
        'mime_type': 'image/tiff',
        'description': 'TIFF image',
        'conversion_needed': False,
        'quality_lossy': False,
        'supports_exif': True,
        'common_source': 'Professional cameras, scanners'
    },
    '.tif': {
        'mime_type': 'image/tiff',
        'description': 'TIFF image',
        'conversion_needed': False,
        'quality_lossy': False,
        'supports_exif': True,
        'common_source': 'Professional cameras, scanners'
    },
    '.bmp': {
        'mime_type': 'image/bmp',
        'description': 'Bitmap image',
        'conversion_needed': False,
        'quality_lossy': False,
        'supports_exif': False,
        'common_source': 'Windows systems'
    },

    # Apple formats (iPhone/iPad)
    '.heic': {
        'mime_type': 'image/heic',
        'description': 'High Efficiency Image Container (Apple)',
        'conversion_needed': True,
        'quality_lossy': True,
        'supports_exif': True,
        'common_source': 'iPhone, iPad (iOS 11+)',
        'conversion_target': '.jpg'
    },
    '.heif': {
        'mime_type': 'image/heif',
        'description': 'High Efficiency Image Format',
        'conversion_needed': True,
        'quality_lossy': True,
        'supports_exif': True,
        'common_source': 'iPhone, iPad, some Android',
        'conversion_target': '.jpg'
    },

    # Modern web formats
    '.webp': {
        'mime_type': 'image/webp',
        'description': 'WebP image (Google)',
        'conversion_needed': True,
        'quality_lossy': True,  # Can be lossless too
        'supports_exif': True,
        'common_source': 'Web, Google services',
        'conversion_target': '.jpg'
    },
    '.avif': {
        'mime_type': 'image/avif',
        'description': 'AV1 Image File Format',
        'conversion_needed': True,
        'quality_lossy': True,
        'supports_exif': True,
        'common_source': 'Modern browsers, next-gen web',
        'conversion_target': '.jpg'
    },

    # Raw formats (from professional cameras)
    '.dng': {
        'mime_type': 'image/x-adobe-dng',
        'description': 'Digital Negative (Adobe)',
        'conversion_needed': True,
        'quality_lossy': False,
        'supports_exif': True,
        'common_source': 'Professional cameras, Adobe',
        'conversion_target': '.jpg'
    },
    '.raw': {
        'mime_type': 'image/x-raw',
        'description': 'Camera RAW image',
        'conversion_needed': True,
        'quality_lossy': False,
        'supports_exif': True,
        'common_source': 'Professional cameras',
        'conversion_target': '.jpg'
    }
}

# Legacy/less common formats
LEGACY_IMAGE_FORMATS = {
    '.gif': {
        'mime_type': 'image/gif',
        'description': 'Graphics Interchange Format',
        'conversion_needed': False,
        'quality_lossy': True,
        'supports_exif': False,
        'common_source': 'Web, animations'
    },
    '.ico': {
        'mime_type': 'image/x-icon',
        'description': 'Icon file',
        'conversion_needed': True,
        'quality_lossy': True,
        'supports_exif': False,
        'common_source': 'Windows icons',
        'conversion_target': '.png'
    },
    '.svg': {
        'mime_type': 'image/svg+xml',
        'description': 'Scalable Vector Graphics',
        'conversion_needed': True,
        'quality_lossy': False,
        'supports_exif': False,
        'common_source': 'Web graphics, vector art',
        'conversion_target': '.png'
    }
}


class ImageFormatConverter:
    """
    Handles conversion between different image formats
    Maneja conversión entre diferentes formatos de imagen
    """

    def __init__(self):
        self._check_dependencies()

    def _check_dependencies(self):
        """Check for required libraries"""
        self.pillow_available = self._check_pillow()
        self.pillow_heif_available = self._check_pillow_heif()
        self.opencv_available = self._check_opencv()

    def _check_pillow(self) -> bool:
        try:
            from PIL import Image
            return True
        except ImportError:
            logger.warning("PIL/Pillow not available - basic image processing limited")
            return False

    def _check_pillow_heif(self) -> bool:
        try:
            import pillow_heif
            pillow_heif.register_heif_opener()
            return True
        except ImportError:
            logger.warning("pillow-heif not available - HEIC/HEIF support limited")
            return False

    def _check_opencv(self) -> bool:
        try:
            import cv2
            return True
        except ImportError:
            logger.debug("OpenCV not available - advanced processing limited")
            return False

    def can_convert(self, source_format: str, target_format: str = '.jpg') -> bool:
        """
        Check if conversion is possible
        Verificar si la conversión es posible
        """
        source_ext = source_format.lower() if source_format.startswith('.') else f'.{source_format.lower()}'
        target_ext = target_format.lower() if target_format.startswith('.') else f'.{target_format.lower()}'

        # Check if source format is supported
        if source_ext not in SUPPORTED_IMAGE_FORMATS and source_ext not in LEGACY_IMAGE_FORMATS:
            return False

        # Check if we have required dependencies
        if source_ext in ['.heic', '.heif'] and not self.pillow_heif_available:
            return False

        if source_ext in ['.webp', '.avif'] and not self.pillow_available:
            return False

        return True

    def convert_image(
        self,
        source_path: Union[str, Path, BytesIO],
        target_format: str = '.jpg',
        quality: int = 95,
        preserve_exif: bool = True
    ) -> BytesIO:
        """
        Convert image to target format
        Convertir imagen al formato objetivo
        """
        if not self.pillow_available:
            raise ImageProcessingError("PIL/Pillow required for image conversion")

        try:
            from PIL import Image, ExifTags

            # Open source image
            if isinstance(source_path, BytesIO):
                image = Image.open(source_path)
                source_format = self._detect_format_from_image(image)
            else:
                source_path = Path(source_path)
                source_format = source_path.suffix.lower()
                image = Image.open(source_path)

            logger.info(f"Converting image from {source_format} to {target_format}")

            # Store original EXIF data if needed
            exif_data = None
            if preserve_exif and hasattr(image, '_getexif'):
                try:
                    exif_data = image._getexif()
                except Exception as e:
                    logger.warning(f"Could not extract EXIF data: {e}")

            # Convert to RGB if necessary (for JPEG output)
            if target_format.lower() in ['.jpg', '.jpeg'] and image.mode in ['RGBA', 'P', 'LA']:
                # Create white background for transparent images
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = rgb_image

            # Prepare output
            output = BytesIO()

            # Save with appropriate parameters
            save_kwargs = {'format': self._get_pil_format(target_format)}

            if target_format.lower() in ['.jpg', '.jpeg']:
                save_kwargs.update({
                    'quality': quality,
                    'optimize': True,
                    'progressive': True
                })
                # Preserve EXIF for JPEG
                if exif_data and preserve_exif:
                    save_kwargs['exif'] = image.info.get('exif', b'')

            elif target_format.lower() == '.png':
                save_kwargs.update({
                    'optimize': True,
                    'compress_level': 6
                })

            elif target_format.lower() in ['.webp']:
                save_kwargs.update({
                    'quality': quality,
                    'method': 6  # Best compression
                })

            image.save(output, **save_kwargs)
            output.seek(0)

            logger.info(f"Successfully converted image to {target_format}")
            return output

        except Exception as e:
            raise ImageProcessingError(
                f"Failed to convert image from {source_format} to {target_format}: {str(e)}",
                operation="format_conversion"
            ) from e

    def _detect_format_from_image(self, image) -> str:
        """Detect format from PIL Image object"""
        format_map = {
            'JPEG': '.jpg',
            'PNG': '.png',
            'TIFF': '.tiff',
            'BMP': '.bmp',
            'WEBP': '.webp',
            'HEIC': '.heic',
            'HEIF': '.heif'
        }
        return format_map.get(image.format, '.unknown')

    def _get_pil_format(self, extension: str) -> str:
        """Get PIL format string from extension"""
        format_map = {
            '.jpg': 'JPEG',
            '.jpeg': 'JPEG',
            '.png': 'PNG',
            '.tiff': 'TIFF',
            '.tif': 'TIFF',
            '.bmp': 'BMP',
            '.webp': 'WEBP'
        }
        return format_map.get(extension.lower(), 'JPEG')

    def get_conversion_info(self, source_format: str) -> Dict[str, Any]:
        """
        Get information about format conversion requirements
        Obtener información sobre requisitos de conversión de formato
        """
        source_ext = source_format.lower() if source_format.startswith('.') else f'.{source_format.lower()}'

        info = SUPPORTED_IMAGE_FORMATS.get(source_ext, LEGACY_IMAGE_FORMATS.get(source_ext))
        if not info:
            return {'supported': False, 'reason': 'Unknown format'}

        result = {
            'supported': True,
            'format_info': info,
            'conversion_needed': info.get('conversion_needed', False),
            'can_convert': self.can_convert(source_ext),
            'recommended_target': info.get('conversion_target', '.jpg')
        }

        # Add specific requirements/warnings
        warnings = []
        if source_ext in ['.heic', '.heif'] and not self.pillow_heif_available:
            warnings.append("pillow-heif library required for HEIC/HEIF support")

        if source_ext in ['.raw', '.dng']:
            warnings.append("RAW format support requires additional processing")

        if source_ext == '.svg':
            warnings.append("SVG conversion may lose vector quality")

        result['warnings'] = warnings
        return result


def detect_image_format(file_path: Union[str, Path, BytesIO]) -> Dict[str, Any]:
    """
    Detect image format and provide detailed information
    Detectar formato de imagen y proporcionar información detallada
    """
    try:
        if isinstance(file_path, BytesIO):
            # For BytesIO, try to detect from content
            from PIL import Image
            file_path.seek(0)
            image = Image.open(file_path)
            format_detected = image.format.lower() if image.format else 'unknown'
            extension = f'.{format_detected}' if format_detected != 'unknown' else '.unknown'
            file_path.seek(0)  # Reset position
        else:
            # For file paths, use extension
            path = Path(file_path)
            extension = path.suffix.lower()

        # Get format information
        format_info = SUPPORTED_IMAGE_FORMATS.get(extension, LEGACY_IMAGE_FORMATS.get(extension))

        if not format_info:
            return {
                'extension': extension,
                'supported': False,
                'reason': 'Unknown or unsupported format'
            }

        return {
            'extension': extension,
            'supported': True,
            'format_info': format_info,
            'mime_type': format_info['mime_type'],
            'description': format_info['description'],
            'needs_conversion': format_info.get('conversion_needed', False),
            'supports_exif': format_info.get('supports_exif', False),
            'common_source': format_info.get('common_source', 'Unknown')
        }

    except Exception as e:
        logger.error(f"Error detecting image format: {e}")
        return {
            'supported': False,
            'error': str(e)
        }


def validate_and_convert_image(
    file_path: Union[str, Path],
    target_format: str = '.jpg',
    max_size_mb: int = 50
) -> Dict[str, Any]:
    """
    Validate image and convert if necessary
    Validar imagen y convertir si es necesario
    """
    path = Path(file_path)

    # Check file size
    file_size = path.stat().st_size
    file_size_mb = file_size / (1024 * 1024)

    if file_size_mb > max_size_mb:
        raise ValidationError(
            f"File too large: {file_size_mb:.1f}MB (max: {max_size_mb}MB)",
            field="file_size"
        )

    # Detect format
    format_info = detect_image_format(file_path)

    if not format_info.get('supported'):
        raise ValidationError(
            f"Unsupported image format: {format_info.get('extension', 'unknown')}",
            field="file_format"
        )

    result = {
        'original_format': format_info['extension'],
        'format_info': format_info,
        'conversion_performed': False,
        'output_path': str(file_path),
        'warnings': []
    }

    # Convert if necessary
    if format_info.get('needs_conversion'):
        converter = ImageFormatConverter()

        if not converter.can_convert(format_info['extension'], target_format):
            missing_deps = []
            if format_info['extension'] in ['.heic', '.heif'] and not converter.pillow_heif_available:
                missing_deps.append('pillow-heif')

            raise ImageProcessingError(
                f"Cannot convert {format_info['extension']} - missing dependencies: {missing_deps}",
                operation="format_validation"
            )

        # Perform conversion
        try:
            converted_data = converter.convert_image(
                file_path,
                target_format=target_format,
                preserve_exif=True
            )

            # Save converted file
            output_path = path.with_suffix(target_format)
            with open(output_path, 'wb') as f:
                f.write(converted_data.getvalue())

            result.update({
                'conversion_performed': True,
                'output_path': str(output_path),
                'target_format': target_format,
                'original_size_mb': file_size_mb,
                'converted_size_mb': output_path.stat().st_size / (1024 * 1024)
            })

            logger.info(f"Converted {format_info['extension']} to {target_format}: {output_path}")

        except Exception as e:
            raise ImageProcessingError(
                f"Conversion failed: {str(e)}",
                image_path=str(file_path),
                operation="format_conversion"
            ) from e

    return result


def get_recommended_libraries() -> Dict[str, Any]:
    """
    Get recommended libraries for comprehensive image support
    Obtener librerías recomendadas para soporte integral de imágenes
    """
    return {
        'required': {
            'Pillow': {
                'package': 'Pillow>=10.0.0',
                'purpose': 'Basic image processing and conversion',
                'formats': ['JPEG', 'PNG', 'TIFF', 'BMP', 'WebP']
            }
        },
        'optional': {
            'pillow-heif': {
                'package': 'pillow-heif>=0.10.0',
                'purpose': 'HEIC/HEIF support (iPhone images)',
                'formats': ['HEIC', 'HEIF'],
                'note': 'Essential for iPhone compatibility'
            },
            'opencv-python': {
                'package': 'opencv-python-headless>=4.8.0',
                'purpose': 'Advanced image processing',
                'formats': ['All standard formats'],
                'note': 'For advanced image analysis'
            },
            'rawpy': {
                'package': 'rawpy>=0.18.0',
                'purpose': 'RAW image format support',
                'formats': ['RAW', 'DNG', 'CR2', 'NEF'],
                'note': 'For professional camera RAW files'
            }
        },
        'installation_commands': {
            'basic': 'pip install Pillow>=10.0.0',
            'heic_support': 'pip install pillow-heif>=0.10.0',
            'full_support': 'pip install Pillow>=10.0.0 pillow-heif>=0.10.0 opencv-python-headless>=4.8.0'
        }
    }


# Global converter instance
_image_converter = None


def get_image_converter() -> ImageFormatConverter:
    """Get or create global image converter instance"""
    global _image_converter
    if _image_converter is None:
        _image_converter = ImageFormatConverter()
    return _image_converter


# Convenience functions for external use
def is_format_supported(file_extension: str) -> bool:
    """
    Check if image format is supported
    Verificar si el formato de imagen está soportado
    """
    ext = file_extension.lower() if file_extension.startswith('.') else f'.{file_extension.lower()}'
    return ext in SUPPORTED_IMAGE_FORMATS or ext in LEGACY_IMAGE_FORMATS


def get_format_info(file_extension: str) -> Optional[Dict[str, Any]]:
    """
    Get format information for file extension
    Obtener información del formato para la extensión de archivo
    """
    ext = file_extension.lower() if file_extension.startswith('.') else f'.{file_extension.lower()}'
    return SUPPORTED_IMAGE_FORMATS.get(ext) or LEGACY_IMAGE_FORMATS.get(ext)


def needs_conversion(file_extension: str) -> bool:
    """
    Check if format needs conversion before processing
    Verificar si el formato necesita conversión antes del procesamiento
    """
    format_info = get_format_info(file_extension)
    return format_info.get('conversion_needed', False) if format_info else False


def convert_heic_to_jpeg(source_path: str, target_dir: str) -> Path:
    """
    Convert HEIC file to JPEG format (compatibility function)
    Convertir archivo HEIC a formato JPEG (función de compatibilidad)
    """
    converter = ImageFormatConverter()
    return converter.convert_image(source_path, target_dir)