"""
Report generation module for YOLO Dengue Detection
Módulo de generación de reportes para detección de criaderos de dengue
"""

import os
import json
from datetime import datetime

from ..core.evaluator import assess_dengue_risk
from ..utils.file_ops import ensure_directory
from ..utils import resolve_path, get_results_dir


def generate_report(source, detections):
    """Genera reporte JSON con detecciones y evaluación de riesgo"""
    risk_assessment = assess_dengue_risk(detections)

    report = {
        'source': os.path.basename(source),
        'total_detections': len(detections),
        'timestamp': datetime.now().isoformat(),
        'detections': detections,
        'risk_assessment': risk_assessment
    }

    return report


def save_report(report, output_path=None):
    """Guarda reporte en archivo JSON"""
    if output_path is None:
        output_path = get_results_dir() / 'detection_report.json'
    else:
        output_path = resolve_path(output_path)

    ensure_directory(os.path.dirname(str(output_path)))
    with open(str(output_path), 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)