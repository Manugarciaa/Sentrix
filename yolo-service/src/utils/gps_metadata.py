"""
GPS metadata extraction utilities for Sentrix YOLO Service
Utilidades de extracción de metadata GPS para el Servicio YOLO Sentrix
"""

import os
import exifread

def extract_image_gps(image_path):
    """
    Extrae datos GPS de una imagen si están disponibles

    Args:
        image_path (str): Ruta a la imagen

    Returns:
        dict: Datos GPS o información de que no está disponible
    """
    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)

        # Buscar datos GPS
        if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
            lat = _convert_exif_coords(tags['GPS GPSLatitude'])
            lat_ref = str(tags.get('GPS GPSLatitudeRef', 'N'))

            lon = _convert_exif_coords(tags['GPS GPSLongitude'])
            lon_ref = str(tags.get('GPS GPSLongitudeRef', 'E'))

            # Aplicar referencias cardinales
            if lat_ref == 'S':
                lat = -lat
            if lon_ref == 'W':
                lon = -lon

            # Datos adicionales opcionales
            altitude = None
            if 'GPS GPSAltitude' in tags:
                alt_val = tags['GPS GPSAltitude']
                altitude = float(alt_val.values[0].num) / float(alt_val.values[0].den)

            gps_date = str(tags.get('GPS GPSDate', 'N/A'))
            gps_timestamp = str(tags.get('GPS GPSTimeStamp', 'N/A'))

            return {
                'has_gps': True,
                'latitude': lat,
                'longitude': lon,
                'coordinates': f"{lat:.6f},{lon:.6f}",
                'altitude': altitude,
                'gps_date': gps_date,
                'gps_timestamp': gps_timestamp,
                'location_source': 'EXIF_GPS'
            }

        return {
            'has_gps': False,
            'reason': 'No GPS coordinates in EXIF',
            'location_source': None
        }

    except Exception as e:
        return {
            'has_gps': False,
            'reason': f'Error reading EXIF: {str(e)}',
            'location_source': None
        }

def _convert_exif_coords(coords):
    """
    Convierte coordenadas EXIF en formato DMS a decimal

    Args:
        coords: Objeto coordenada EXIF

    Returns:
        float: Coordenada en formato decimal
    """
    values = coords.values
    degrees = float(values[0].num) / float(values[0].den)
    minutes = float(values[1].num) / float(values[1].den)
    seconds = float(values[2].num) / float(values[2].den)
    return degrees + minutes/60 + seconds/3600

def get_image_camera_info(image_path):
    """
    Extrae información de la cámara que tomó la imagen

    Args:
        image_path (str): Ruta a la imagen

    Returns:
        dict: Información de la cámara
    """
    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)

        return {
            'camera_make': str(tags.get('Image Make', 'Unknown')),
            'camera_model': str(tags.get('Image Model', 'Unknown')),
            'datetime_original': str(tags.get('Image DateTime', 'Unknown')),
            'software': str(tags.get('Image Software', 'Unknown'))
        }
    except:
        return {
            'camera_make': 'Unknown',
            'camera_model': 'Unknown',
            'datetime_original': 'Unknown',
            'software': 'Unknown'
        }

def validate_gps_coordinates(latitude, longitude):
    """
    Valida que las coordenadas GPS sean válidas

    Args:
        latitude (float): Latitud
        longitude (float): Longitud

    Returns:
        bool: True si las coordenadas son válidas
    """
    try:
        lat = float(latitude)
        lon = float(longitude)

        # Validar rangos válidos
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            # Validar que no sean coordenadas nulas (0,0)
            if not (lat == 0 and lon == 0):
                return True

        return False
    except (ValueError, TypeError):
        return False

def format_gps_for_maps(gps_data):
    """
    Formatea datos GPS para integración con sistemas de mapas

    Args:
        gps_data (dict): Datos GPS extraídos

    Returns:
        dict: Datos formateados para mapas o None si no hay GPS
    """
    if not gps_data.get('has_gps', False):
        return None

    # Validar coordenadas
    if not validate_gps_coordinates(gps_data['latitude'], gps_data['longitude']):
        return None

    return {
        'lat': round(gps_data['latitude'], 6),
        'lng': round(gps_data['longitude'], 6),
        'coordinates_string': gps_data['coordinates'],
        'altitude_meters': gps_data.get('altitude'),
        'google_maps_url': f"https://maps.google.com/?q={gps_data['latitude']},{gps_data['longitude']}",
        'precision': 'EXIF_GPS'  # Indica fuente de precisión
    }