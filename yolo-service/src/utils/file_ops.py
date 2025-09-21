"""
File operation utilities for YOLO Dengue Detection
Utilidades de operaciones de archivo para detección de criaderos de dengue

Now uses shared file utilities and logging for consistency
Ahora usa utilidades de archivos compartidas y logging para consistencia
"""

import os
import sys
# Import shared utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from shared.file_utils import (
    validate_image_file,
    ensure_directory_exists,
    SUPPORTED_IMAGE_EXTENSIONS
)
from shared.logging_utils import get_module_logger

# Setup module logger
logger = get_module_logger(__name__, 'yolo-service')


def validate_file_exists(file_path, file_type="archivo"):
    """Valida que un archivo existe"""
    if not os.path.exists(file_path):
        logger.error(f"{file_type} no encontrado: {file_path}")
        raise FileNotFoundError(f"{file_type} no encontrado: {file_path}")
    logger.debug(f"{file_type} encontrado: {file_path}")
    return True


def validate_model_file(model_path):
    """Valida que el archivo del modelo existe y es valido"""
    if not model_path.endswith('.pt'):
        logger.error(f"Formato de modelo inválido: {model_path}")
        raise ValueError(f"El modelo debe ser un archivo .pt: {model_path}")

    validate_file_exists(model_path, "Modelo")
    logger.info(f"Modelo validado: {model_path}")
    return True


def ensure_directory(directory_path):
    """Asegura que un directorio existe"""
    result = ensure_directory_exists(directory_path)
    logger.debug(f"Directorio asegurado: {result}")
    return str(result)


def get_image_extensions():
    """Retorna extensiones de imagen soportadas"""
    # Use shared supported extensions
    extensions = [f'*{ext}' for ext in SUPPORTED_IMAGE_EXTENSIONS]
    logger.debug(f"Extensiones de imagen soportadas: {extensions}")
    return extensions


def log_section_header(title):
    """Log section header instead of printing"""
    logger.info(f"=== {title.upper()} ===")


# Backward compatibility alias
def print_section_header(title):
    """Deprecated: Use log_section_header instead"""
    logger.warning("print_section_header is deprecated, use log_section_header")
    log_section_header(title)