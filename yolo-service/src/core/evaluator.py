"""
Risk evaluation module for YOLO Dengue Detection
Módulo de evaluación de riesgo para detección de criaderos de dengue

Now uses shared risk assessment library for consistency
Ahora usa la librería compartida de evaluación de riesgo para consistencia
"""

import sys
import os
from pathlib import Path

# Use sentrix_shared package
from sentrix_shared.risk_assessment import assess_dengue_risk as shared_assess_dengue_risk
from sentrix_shared.image_formats import is_format_supported, convert_heic_to_jpeg


def assess_dengue_risk(detections):
    """
    Evalúa riesgo epidemiológico basado en detecciones
    Uses shared library for consistent risk assessment across services
    """
    # Use the unified shared function
    return shared_assess_dengue_risk(detections)


def validate_image_file(image_path):
    """Simple image validation"""
    from pathlib import Path

    result = {'is_valid': False, 'errors': [], 'format_info': {}}

    if not os.path.exists(image_path):
        result['errors'].append('File does not exist')
        return result

    ext = Path(image_path).suffix.lower()
    if not is_format_supported(ext):
        result['errors'].append(f'Unsupported format: {ext}')
        return result

    result['is_valid'] = True
    result['format_info'] = {'extension': ext}
    return result


def process_image_with_conversion(image_path, target_dir=None):
    """Process image with HEIC conversion if needed"""
    result = {
        'success': False,
        'processed_path': None,
        'conversion_performed': False,
        'errors': []
    }

    try:
        ext = Path(image_path).suffix.lower()

        # If HEIC, convert to JPEG
        if ext in ['.heic', '.heif']:
            if target_dir:
                output_path = os.path.join(target_dir, Path(image_path).stem + '.jpg')
            else:
                output_path = str(Path(image_path).with_suffix('.jpg'))

            success = convert_heic_to_jpeg(image_path, output_path)
            if success:
                result['success'] = True
                result['processed_path'] = output_path
                result['conversion_performed'] = True
            else:
                result['errors'].append('HEIC conversion failed')
        else:
            # No conversion needed
            result['success'] = True
            result['processed_path'] = image_path
            result['conversion_performed'] = False

    except Exception as e:
        result['errors'].append(f'Conversion error: {str(e)}')

    return result


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