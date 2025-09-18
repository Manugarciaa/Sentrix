"""
File operation utilities for YOLO Dengue Detection
Utilidades de operaciones de archivo para detección de criaderos de dengue
"""

import os


def validate_file_exists(file_path, file_type="archivo"):
    """Valida que un archivo existe"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_type} no encontrado: {file_path}")
    return True


def validate_model_file(model_path):
    """Valida que el archivo del modelo existe y es valido"""
    if not model_path.endswith('.pt'):
        raise ValueError(f"El modelo debe ser un archivo .pt: {model_path}")
    validate_file_exists(model_path, "Modelo")
    return True


def ensure_directory(directory_path):
    """Asegura que un directorio existe"""
    os.makedirs(directory_path, exist_ok=True)
    return directory_path


def get_image_extensions():
    """Retorna extensiones de imagen soportadas"""
    return ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.webp']


def print_section_header(title):
    """Imprime encabezado de seccion formateado"""
    print(f"\n{'='*3} {title.upper()} {'='*3}")