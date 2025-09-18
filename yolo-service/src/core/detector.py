"""
Detection module for YOLO Dengue Detection
Módulo de detección para criaderos de dengue
"""

import os
from ultralytics import YOLO

from configs.classes import DENGUE_CLASSES, RISK_LEVEL_BY_ID
from ..utils import validate_model_file, validate_file_exists, cleanup_unwanted_downloads, extract_image_gps, get_image_camera_info


def detect_breeding_sites(model_path, source, conf_threshold=0.5, include_gps=True):
    """
    Detecta sitios de cría en imágenes usando modelo entrenado

    Args:
        model_path (str): Ruta al modelo YOLO entrenado
        source (str): Ruta a la imagen o directorio
        conf_threshold (float): Umbral de confianza para detecciones
        include_gps (bool): Incluir información GPS en cada detección

    Returns:
        list: Lista de detecciones con información GPS (si está disponible)
    """
    validate_model_file(model_path)
    validate_file_exists(source, "Imagen/directorio")

    try:
        os.environ['YOLO_VERBOSE'] = 'False'
        model = YOLO(model_path)
        results = model(source, conf=conf_threshold, task='segment')

        # Extraer información GPS una sola vez por imagen
        gps_data = None
        camera_info = None
        if include_gps and os.path.isfile(source):  # Solo para imágenes individuales
            gps_data = extract_image_gps(source)
            camera_info = get_image_camera_info(source)

        detections = []
        for result in results:
            if result.masks is not None:
                for i, mask in enumerate(result.masks):
                    class_id = int(result.boxes.cls[i])
                    polygon_coords = mask.xy[0].tolist()

                    # Crear detección básica
                    detection = {
                        'class': DENGUE_CLASSES.get(class_id, f"Clase_{class_id}"),
                        'class_id': class_id,
                        'confidence': float(result.boxes.conf[i]),
                        'polygon': polygon_coords,
                        'mask_area': float(mask.data.sum()),
                        'risk_level': RISK_LEVEL_BY_ID.get(class_id, 'BAJO')
                    }

                    # Agregar información GPS si está disponible
                    if include_gps and gps_data:
                        detection['location'] = _create_detection_location(gps_data, camera_info, detection)
                    elif include_gps:
                        detection['location'] = {
                            'has_location': False,
                            'reason': 'No GPS data available in image'
                        }

                    # Agregar metadata de imagen
                    if include_gps:
                        detection['image_metadata'] = {
                            'source_file': os.path.basename(source) if os.path.isfile(source) else 'multiple_files',
                            'detection_timestamp': None,  # Se puede agregar en el futuro
                            'camera_info': camera_info
                        }

                    detections.append(detection)

        return detections

    except Exception as e:
        print(f"Error durante la detección: {e}")
        raise
    finally:
        # Limpiar descargas no deseadas
        cleanup_unwanted_downloads()

def _create_detection_location(gps_data, camera_info, detection):
    """
    Crea información de ubicación específica para una detección individual

    Args:
        gps_data (dict): Datos GPS de la imagen
        camera_info (dict): Información de la cámara
        detection (dict): Datos de la detección específica

    Returns:
        dict: Información de ubicación para la detección
    """
    if not gps_data or not gps_data.get('has_gps', False):
        return {
            'has_location': False,
            'reason': 'No GPS coordinates in image EXIF'
        }

    # Crear ubicación específica para esta detección
    location = {
        'has_location': True,
        'latitude': gps_data['latitude'],
        'longitude': gps_data['longitude'],
        'coordinates': gps_data['coordinates'],
        'altitude_meters': gps_data.get('altitude'),
        'gps_date': gps_data.get('gps_date'),
        'location_source': gps_data['location_source'],

        # Información específica para backend
        'backend_integration': {
            'geo_point': f"POINT({gps_data['longitude']} {gps_data['latitude']})",
            'risk_level': detection['risk_level'],
            'breeding_site_type': detection['class'],
            'confidence_score': detection['confidence'],
            'area_square_pixels': detection['mask_area'],
            'requires_verification': True,
            'detection_id': None,  # Se puede generar UUID en el backend

            # URLs útiles para verificación
            'verification_urls': {
                'google_maps': f"https://maps.google.com/?q={gps_data['latitude']},{gps_data['longitude']}",
                'google_earth': f"https://earth.google.com/web/search/{gps_data['latitude']},{gps_data['longitude']}",
                'coordinates_string': gps_data['coordinates']
            }
        }
    }

    return location