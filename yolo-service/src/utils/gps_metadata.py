"""
GPS metadata extraction utilities for Sentrix YOLO Service
Utilidades de extracción de metadata GPS para el Servicio YOLO Sentrix

Now uses shared GPS utilities for consistency across services
Ahora usa utilidades GPS compartidas para consistencia entre servicios
"""

import os
import sys
# Import shared GPS utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from shared.gps_utils import (
    extract_gps_from_exif as shared_extract_gps,
    extract_camera_info_from_exif as shared_extract_camera,
    extract_complete_image_metadata as shared_extract_metadata,
    validate_gps_coordinates as shared_validate_gps,
    generate_maps_urls as shared_generate_maps_urls
)


def extract_image_gps(image_path):
    """
    Extrae datos GPS de una imagen si están disponibles
    Uses shared GPS utilities for consistency

    Args:
        image_path (str): Ruta a la imagen

    Returns:
        dict: Datos GPS o información de que no está disponible
    """
    # Use shared GPS extraction function
    return shared_extract_gps(image_path)


def get_image_camera_info(image_path):
    """
    Extrae información de la cámara que tomó la imagen
    Uses shared camera info extraction

    Args:
        image_path (str): Ruta a la imagen

    Returns:
        dict: Información de la cámara
    """
    # Use shared camera info extraction function
    return shared_extract_camera(image_path)


def validate_gps_coordinates(latitude, longitude):
    """
    Valida que las coordenadas GPS sean válidas
    Uses shared GPS validation

    Args:
        latitude (float): Latitud
        longitude (float): Longitud

    Returns:
        dict: Resultado de validación
    """
    # Use shared GPS validation function
    return shared_validate_gps(latitude, longitude)


def generate_verification_urls(latitude, longitude):
    """
    Genera URLs de verificación para las coordenadas GPS
    Uses shared URL generation

    Args:
        latitude (float): Latitud
        longitude (float): Longitud

    Returns:
        dict: URLs de verificación
    """
    # Use shared URL generation function
    return shared_generate_maps_urls(latitude, longitude)


def get_complete_image_metadata(image_path):
    """
    Extrae metadatos completos de imagen incluyendo GPS e info de cámara
    Uses shared complete metadata extraction

    Args:
        image_path (str): Ruta a la imagen

    Returns:
        dict: Metadatos completos
    """
    # Use shared complete metadata extraction function
    return shared_extract_metadata(image_path)


# Backward compatibility aliases
def extract_complete_metadata(image_path):
    """Alias for backward compatibility"""
    return get_complete_image_metadata(image_path)


def get_gps_verification_urls(latitude, longitude):
    """Alias for backward compatibility"""
    return generate_verification_urls(latitude, longitude)


def format_gps_for_maps(gps_data):
    """
    Formats GPS data for maps integration
    Formatea datos GPS para integración con mapas

    Args:
        gps_data (dict): GPS data from extract_image_gps

    Returns:
        dict: Formatted GPS data with maps URLs
    """
    if not gps_data or not gps_data.get('has_gps'):
        return {'has_gps': False, 'maps_urls': {}}

    # Use shared maps URL generation
    maps_urls = shared_generate_maps_urls(
        gps_data['latitude'],
        gps_data['longitude']
    )

    return {
        'has_gps': True,
        'latitude': gps_data['latitude'],
        'longitude': gps_data['longitude'],
        'maps_urls': maps_urls
    }