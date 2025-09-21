"""
Shared GPS utilities for Sentrix project
Utilidades GPS compartidas para el proyecto Sentrix

Common GPS metadata extraction, validation, and processing functions
Funciones comunes de extracción, validación y procesamiento de metadatos GPS
"""

import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Union, Any
from datetime import datetime


def extract_gps_from_exif(image_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Extract GPS coordinates from image EXIF data
    Extraer coordenadas GPS de datos EXIF de imagen
    """
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS, GPSTAGS
    except ImportError:
        return {'has_gps': False, 'error': 'PIL library not available'}

    result = {
        'has_gps': False,
        'latitude': None,
        'longitude': None,
        'altitude': None,
        'gps_date': None,
        'gps_timestamp': None,
        'location_source': 'EXIF_GPS'
    }

    try:
        image = Image.open(image_path)
        exif_data = image._getexif()

        if not exif_data:
            result['error'] = 'No EXIF data found'
            return result

        # Find GPS info
        gps_info = None
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == 'GPSInfo':
                gps_info = value
                break

        if not gps_info:
            result['error'] = 'No GPS data in EXIF'
            return result

        # Extract GPS coordinates
        gps_data = {}
        for key, value in gps_info.items():
            tag_name = GPSTAGS.get(key, key)
            gps_data[tag_name] = value

        # Convert coordinates
        lat = _convert_gps_coordinate(
            gps_data.get('GPSLatitude'),
            gps_data.get('GPSLatitudeRef')
        )
        lon = _convert_gps_coordinate(
            gps_data.get('GPSLongitude'),
            gps_data.get('GPSLongitudeRef')
        )

        if lat is not None and lon is not None:
            result['has_gps'] = True
            result['latitude'] = lat
            result['longitude'] = lon

            # Extract altitude if available
            if 'GPSAltitude' in gps_data:
                altitude = gps_data['GPSAltitude']
                if isinstance(altitude, tuple) and len(altitude) == 2:
                    result['altitude'] = float(altitude[0]) / float(altitude[1])

            # Extract GPS timestamp
            if 'GPSDateStamp' in gps_data and 'GPSTimeStamp' in gps_data:
                try:
                    date_stamp = gps_data['GPSDateStamp']
                    time_stamp = gps_data['GPSTimeStamp']

                    result['gps_date'] = date_stamp
                    if isinstance(time_stamp, tuple) and len(time_stamp) >= 3:
                        hours = float(time_stamp[0])
                        minutes = float(time_stamp[1])
                        seconds = float(time_stamp[2]) if len(time_stamp) > 2 else 0
                        result['gps_timestamp'] = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
                except Exception:
                    pass

        else:
            result['error'] = 'Invalid GPS coordinates'

    except Exception as e:
        result['error'] = f'Error extracting GPS: {str(e)}'

    return result


def _convert_gps_coordinate(coordinate: Optional[tuple], direction: Optional[str]) -> Optional[float]:
    """
    Convert GPS coordinate from DMS to decimal degrees
    Convertir coordenada GPS de DMS a grados decimales
    """
    if not coordinate or not direction:
        return None

    try:
        if len(coordinate) != 3:
            return None

        degrees = float(coordinate[0])
        minutes = float(coordinate[1])
        seconds = float(coordinate[2])

        decimal_degrees = degrees + (minutes / 60.0) + (seconds / 3600.0)

        # Apply direction
        if direction in ['S', 'W']:
            decimal_degrees = -decimal_degrees

        return decimal_degrees

    except (ValueError, TypeError, ZeroDivisionError):
        return None


def extract_camera_info_from_exif(image_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Extract camera information from EXIF data
    Extraer información de cámara de datos EXIF
    """
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
    except ImportError:
        return {'error': 'PIL library not available'}

    result = {
        'camera_make': None,
        'camera_model': None,
        'datetime_original': None,
        'software': None
    }

    try:
        image = Image.open(image_path)
        exif_data = image._getexif()

        if not exif_data:
            result['error'] = 'No EXIF data found'
            return result

        # Extract camera info
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)

            if tag_name == 'Make':
                result['camera_make'] = str(value).strip()
            elif tag_name == 'Model':
                result['camera_model'] = str(value).strip()
            elif tag_name == 'DateTime':
                result['datetime_original'] = str(value).strip()
            elif tag_name == 'Software':
                result['software'] = str(value).strip()

    except Exception as e:
        result['error'] = f'Error extracting camera info: {str(e)}'

    return result


def validate_gps_coordinates(latitude: Optional[float], longitude: Optional[float]) -> Dict[str, Any]:
    """
    Validate GPS coordinates are within valid ranges
    Validar que las coordenadas GPS estén dentro de rangos válidos
    """
    result = {
        'is_valid': False,
        'latitude': latitude,
        'longitude': longitude,
        'errors': []
    }

    if latitude is None or longitude is None:
        result['errors'].append('Coordinates cannot be None')
        return result

    # Validate latitude range (-90 to 90)
    if not -90 <= latitude <= 90:
        result['errors'].append(f'Invalid latitude: {latitude} (must be between -90 and 90)')

    # Validate longitude range (-180 to 180)
    if not -180 <= longitude <= 180:
        result['errors'].append(f'Invalid longitude: {longitude} (must be between -180 and 180)')

    # Check for obviously invalid coordinates (0,0 is suspicious unless in Gulf of Guinea)
    if latitude == 0 and longitude == 0:
        result['errors'].append('Coordinates (0,0) are suspicious - likely invalid')

    if not result['errors']:
        result['is_valid'] = True

    return result


def generate_maps_urls(latitude: float, longitude: float) -> Dict[str, str]:
    """
    Generate map URLs for verification
    Generar URLs de mapas para verificación
    """
    urls = {}

    if latitude is None or longitude is None:
        return urls

    try:
        # Google Maps URL
        urls['google_maps'] = f"https://www.google.com/maps?q={latitude},{longitude}"

        # Google Earth URL
        urls['google_earth'] = f"https://earth.google.com/web/@{latitude},{longitude},1000a,1000d,35y,0h,0t,0r"

        # OpenStreetMap URL
        urls['openstreetmap'] = f"https://www.openstreetmap.org/?mlat={latitude}&mlon={longitude}&zoom=16"

    except Exception:
        pass

    return urls


def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two GPS points in kilometers using Haversine formula
    Calcular distancia entre dos puntos GPS en kilómetros usando fórmula de Haversine
    """
    import math

    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)

    c = 2 * math.asin(math.sqrt(a))

    # Earth's radius in kilometers
    earth_radius_km = 6371.0

    return earth_radius_km * c


def extract_complete_image_metadata(image_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Extract complete metadata from image including GPS and camera info
    Extraer metadatos completos de imagen incluyendo GPS e info de cámara
    """
    result = {
        'source_file': str(image_path),
        'file_info': {},
        'gps_data': {},
        'camera_info': {},
        'processing_timestamp': datetime.now().isoformat()
    }

    # File info
    try:
        path = Path(image_path)
        if path.exists():
            stat = path.stat()
            result['file_info'] = {
                'filename': path.name,
                'size_bytes': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
    except Exception as e:
        result['file_info']['error'] = str(e)

    # GPS data
    result['gps_data'] = extract_gps_from_exif(image_path)

    # Camera info
    result['camera_info'] = extract_camera_info_from_exif(image_path)

    # Generate maps URLs if GPS available
    if result['gps_data'].get('has_gps'):
        lat = result['gps_data']['latitude']
        lon = result['gps_data']['longitude']

        if lat is not None and lon is not None:
            result['maps_urls'] = generate_maps_urls(lat, lon)

            # Validate coordinates
            validation = validate_gps_coordinates(lat, lon)
            result['gps_validation'] = validation

    return result


def format_gps_for_frontend(gps_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format GPS data for frontend consumption
    Formatear datos GPS para consumo del frontend
    """
    if not gps_data.get('has_gps'):
        return {
            'hasLocation': False,
            'latitude': None,
            'longitude': None,
            'accuracy': None,
            'source': None
        }

    return {
        'hasLocation': True,
        'latitude': gps_data.get('latitude'),
        'longitude': gps_data.get('longitude'),
        'altitude': gps_data.get('altitude'),
        'accuracy': None,  # EXIF doesn't provide accuracy
        'source': gps_data.get('location_source', 'EXIF_GPS'),
        'timestamp': gps_data.get('gps_timestamp'),
        'date': gps_data.get('gps_date'),
        'mapsUrls': gps_data.get('maps_urls', {})
    }