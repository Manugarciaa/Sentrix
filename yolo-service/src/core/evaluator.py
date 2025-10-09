"""
Risk evaluation module for YOLO Dengue Detection
Módulo de evaluación de riesgo para detección de criaderos de dengue

Now uses shared risk assessment library for consistency
Ahora usa la librería compartida de evaluación de riesgo para consistencia
"""

import sys
import os
from pathlib import Path

# Add shared library to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from shared import (
    assess_dengue_risk as shared_assess_dengue_risk,
    process_image_with_conversion,
    validate_image_file
)


def assess_dengue_risk(detections):
    """
    Evalúa riesgo epidemiológico basado en detecciones
    Uses shared library for consistent risk assessment across services
    """
    # Use the unified shared function
    return shared_assess_dengue_risk(detections)


def process_image_for_detection(image_path, target_dir=None):
    """
    Process image with automatic format conversion before YOLO detection
    Procesar imagen con conversión automática antes de la detección YOLO
    """
    result = {
        'success': False,
        'processed_path': None,
        'conversion_performed': False,
        'original_format': None,
        'errors': []
    }

    try:
        # First validate the image
        validation = validate_image_file(image_path)
        if not validation['is_valid']:
            result['errors'] = validation['errors']
            return result

        result['original_format'] = validation.get('format_info', {})

        # Process with conversion if needed
        conversion_result = process_image_with_conversion(image_path, target_dir)

        if conversion_result['success']:
            result['success'] = True
            result['processed_path'] = conversion_result['processed_path']
            result['conversion_performed'] = conversion_result['conversion_performed']
        else:
            result['errors'] = conversion_result['errors']

    except Exception as e:
        result['errors'].append(f'Image processing failed: {str(e)}')

    return result