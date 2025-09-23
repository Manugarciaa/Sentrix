"""
Report generation module for YOLO Dengue Detection
Módulo de generación de reportes para detección de criaderos de dengue
"""

import os
import json
from datetime import datetime

from ..core.evaluator import assess_dengue_risk
from ..utils.file_ops import ensure_directory
from ..utils import resolve_path, get_results_dir, extract_image_gps, get_image_camera_info


def generate_report(source, detections, include_gps=True):
    """
    Genera reporte JSON con detecciones, evaluación de riesgo y metadata GPS

    Args:
        source (str): Ruta de la imagen analizada
        detections (list): Lista de detecciones encontradas
        include_gps (bool): Incluir información GPS si está disponible

    Returns:
        dict: Reporte completo en formato JSON
    """
    risk_assessment = assess_dengue_risk(detections)

    # Datos básicos del reporte
    report = {
        'source': os.path.basename(source),
        'source_path': str(source),
        'total_detections': len(detections),
        'timestamp': datetime.now().isoformat(),
        'detections': detections,
        'risk_assessment': risk_assessment
    }

    # Agregar información GPS si está solicitada
    if include_gps and os.path.exists(source):
        gps_data = extract_image_gps(source)
        camera_info = get_image_camera_info(source)

        # Información de cámara
        report['camera_info'] = camera_info

        # Información de ubicación
        if gps_data.get('has_gps', False):
            # Datos GPS directos
            report['location'] = {
                'has_location': True,
                'latitude': gps_data['latitude'],
                'longitude': gps_data['longitude'],
                'coordinates': gps_data['coordinates'],
                'altitude_meters': gps_data.get('altitude'),
                'gps_date': gps_data.get('gps_date'),
                'gps_timestamp': gps_data.get('gps_timestamp'),
                'location_source': gps_data['location_source']
            }

            # Datos formateados para mapas
            maps_data = format_gps_for_maps(gps_data)
            if maps_data:
                report['location']['maps'] = maps_data

            # Enriquecer datos para integración Sentrix
            report['location']['sentrix_integration'] = {
                'geo_point': f"POINT({gps_data['longitude']} {gps_data['latitude']})",
                'zoom_level': 18,  # Nivel de zoom recomendado para criaderos
                'marker_color': _get_risk_color(risk_assessment['level']),
                'requires_field_verification': True
            }
        else:
            report['location'] = {
                'has_location': False,
                'reason': gps_data.get('reason', 'Unknown'),
                'location_source': None,
                'sentrix_integration': {
                    'requires_manual_geocoding': True,
                    'marker_color': _get_risk_color(risk_assessment['level'])
                }
            }

    return report

def _get_risk_color(risk_level):
    """
    Retorna color de marcador según nivel de riesgo para mapas

    Args:
        risk_level (str): Nivel de riesgo (ALTO, MEDIO, BAJO, MÍNIMO)

    Returns:
        str: Color en formato hex para marcadores
    """
    colors = {
        'ALTO': '#FF0000',      # Rojo
        'MEDIO': '#FF6600',     # Naranja
        'BAJO': '#FFFF00',      # Amarillo
        'MÍNIMO': '#00FF00'     # Verde
    }
    return colors.get(risk_level, '#808080')  # Gris por defecto


def save_report(report, output_path=None):
    """Guarda reporte en archivo JSON"""
    if output_path is None:
        output_path = get_results_dir() / 'detection_report.json'
    else:
        output_path = resolve_path(output_path)

    ensure_directory(os.path.dirname(str(output_path)))
    with open(str(output_path), 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)