"""
Detection module for YOLO Dengue Detection
Módulo de detección para criaderos de dengue
"""

import os
from ultralytics import YOLO

from configs.classes import DENGUE_CLASSES
from ..utils import validate_model_file, validate_file_exists, cleanup_unwanted_downloads


def detect_breeding_sites(model_path, source, conf_threshold=0.5):
    """Detecta sitios de cría en imágenes usando modelo entrenado"""
    validate_model_file(model_path)
    validate_file_exists(source, "Imagen/directorio")

    try:
        os.environ['YOLO_VERBOSE'] = 'False'
        model = YOLO(model_path)
        results = model(source, conf=conf_threshold, task='segment')

        detections = []
        for result in results:
            if result.masks is not None:
                for i, mask in enumerate(result.masks):
                    class_id = int(result.boxes.cls[i])
                    polygon_coords = mask.xy[0].tolist()
                    detections.append({
                        'class': DENGUE_CLASSES.get(class_id, f"Clase_{class_id}"),
                        'class_id': class_id,
                        'confidence': float(result.boxes.conf[i]),
                        'polygon': polygon_coords,
                        'mask_area': float(mask.data.sum())
                    })
        return detections
    except Exception as e:
        print(f"Error durante la detección: {e}")
        raise
    finally:
        # Limpiar descargas no deseadas
        cleanup_unwanted_downloads()