"""
Utilities for integrating with YOLO service responses
Utilidades para integrar con las respuestas del servicio YOLO
"""

from typing import Dict, List, Any, Optional
from shared.data_models import DetectionRiskEnum, BreedingSiteTypeEnum


# Mapeo de class_id del YOLO service a enum de backend
CLASS_ID_TO_BREEDING_SITE = {
    0: BreedingSiteTypeEnum.BASURA,
    1: BreedingSiteTypeEnum.CALLES_MAL_HECHAS,
    2: BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA,
    3: BreedingSiteTypeEnum.HUECOS,
}

# Mapeo de nombres de clase del YOLO service a enum de backend
CLASS_NAME_TO_BREEDING_SITE = {
    "Basura": BreedingSiteTypeEnum.BASURA,
    "Calles mal hechas": BreedingSiteTypeEnum.CALLES_MAL_HECHAS,
    "Charcos/Cumulo de agua": BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA,
    "Huecos": BreedingSiteTypeEnum.HUECOS,
}

# Mapeo de niveles de riesgo del YOLO service a enum de backend
YOLO_RISK_TO_DETECTION_RISK = {
    "ALTO": DetectionRiskEnum.ALTO,
    "MEDIO": DetectionRiskEnum.MEDIO,
    "BAJO": DetectionRiskEnum.BAJO,
}


def parse_yolo_detection(yolo_detection: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convierte una detección del YOLO service al formato del backend

    Args:
        yolo_detection: Detección en formato del YOLO service

    Returns:
        Dict con datos formateados para el backend
    """
    # Extraer información básica
    class_id = yolo_detection.get('class_id')
    class_name = yolo_detection.get('class')
    confidence = yolo_detection.get('confidence')
    risk_level = yolo_detection.get('risk_level')

    # Mapear enums
    breeding_site_type = None
    if class_id is not None:
        breeding_site_type = CLASS_ID_TO_BREEDING_SITE.get(class_id)
    elif class_name:
        breeding_site_type = CLASS_NAME_TO_BREEDING_SITE.get(class_name)

    detection_risk = YOLO_RISK_TO_DETECTION_RISK.get(risk_level)

    # Extraer datos de ubicación
    location_data = yolo_detection.get('location', {})
    has_location = location_data.get('has_location', False)

    # Preparar datos para el backend
    backend_detection = {
        'class_id': class_id,
        'class_name': class_name,
        'confidence': confidence,
        'risk_level': detection_risk,
        'breeding_site_type': breeding_site_type,
        'polygon': yolo_detection.get('polygon'),
        'mask_area': yolo_detection.get('mask_area'),
        'area_square_pixels': yolo_detection.get('mask_area'),  # Alias
        'requires_verification': True,
    }

    # Agregar datos GPS si están disponibles
    if has_location:
        backend_detection.update({
            'has_location': True,
            'detection_latitude': location_data.get('latitude'),
            'detection_longitude': location_data.get('longitude'),
            'detection_altitude_meters': location_data.get('altitude_meters'),
        })

        # Extraer URLs de verificación
        backend_integration = location_data.get('backend_integration', {})
        verification_urls = backend_integration.get('verification_urls', {})

        backend_detection.update({
            'google_maps_url': verification_urls.get('google_maps'),
            'google_earth_url': verification_urls.get('google_earth'),
        })
    else:
        backend_detection['has_location'] = False

    # Agregar metadata de imagen
    image_metadata = yolo_detection.get('image_metadata', {})
    camera_info = image_metadata.get('camera_info', {})

    backend_detection.update({
        'source_filename': image_metadata.get('source_file'),
        'camera_make': camera_info.get('camera_make'),
        'camera_model': camera_info.get('camera_model'),
        'image_datetime': camera_info.get('datetime_original'),
    })

    return backend_detection


def parse_yolo_report(yolo_report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convierte un reporte completo del YOLO service al formato del backend

    Args:
        yolo_report: Reporte en formato del YOLO service

    Returns:
        Dict con datos formateados para crear análisis en el backend
    """
    # Extraer información básica del análisis
    analysis_data = {
        'image_filename': yolo_report.get('source'),
        'total_detections': yolo_report.get('total_detections', 0),
        'processing_time_ms': yolo_report.get('processing_time_ms'),
        'model_used': yolo_report.get('model_version'),
        'yolo_service_version': yolo_report.get('version', '2.0.0'),
    }

    # Extraer información de ubicación del análisis
    location_data = yolo_report.get('location', {})
    if location_data.get('has_location', False):
        analysis_data.update({
            'has_gps_data': True,
            'gps_altitude_meters': location_data.get('altitude_meters'),
            'gps_date': location_data.get('gps_date'),
            'gps_timestamp': location_data.get('gps_timestamp'),
            'location_source': location_data.get('location_source'),
            'google_maps_url': location_data.get('maps', {}).get('google_maps_url'),
            'google_earth_url': location_data.get('maps', {}).get('google_earth_url'),
        })
    else:
        analysis_data['has_gps_data'] = False

    # Extraer información de cámara
    camera_info = yolo_report.get('camera_info', {})
    analysis_data.update({
        'camera_make': camera_info.get('camera_make'),
        'camera_model': camera_info.get('camera_model'),
        'camera_datetime': camera_info.get('datetime_original'),
        'camera_software': camera_info.get('software'),
    })

    # Procesar evaluación de riesgo
    risk_assessment = yolo_report.get('risk_assessment', {})
    risk_level_map = {
        'ALTO': 'HIGH',
        'MEDIO': 'MEDIUM',
        'BAJO': 'LOW',
        'MÍNIMO': 'MINIMAL'
    }

    analysis_data.update({
        'risk_level': risk_level_map.get(risk_assessment.get('level')),
        'high_risk_count': risk_assessment.get('high_risk_sites', 0),
        'medium_risk_count': risk_assessment.get('medium_risk_sites', 0),
        'recommendations': risk_assessment.get('recommendations', []),
    })

    # Procesar detecciones individuales
    detections = []
    for yolo_detection in yolo_report.get('detections', []):
        backend_detection = parse_yolo_detection(yolo_detection)
        detections.append(backend_detection)

    return {
        'analysis': analysis_data,
        'detections': detections
    }


def validate_yolo_response(yolo_response: Dict[str, Any]) -> bool:
    """
    Valida que la respuesta del YOLO service tenga el formato esperado

    Args:
        yolo_response: Respuesta del YOLO service

    Returns:
        bool: True si la respuesta es válida
    """
    required_fields = ['success', 'detections']

    for field in required_fields:
        if field not in yolo_response:
            return False

    if not yolo_response['success']:
        return False

    # Validar que las detecciones tengan los campos mínimos
    for detection in yolo_response.get('detections', []):
        if not all(field in detection for field in ['class', 'confidence', 'risk_level']):
            return False

    return True