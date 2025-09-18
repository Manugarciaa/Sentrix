"""
Model utilities for YOLO Dengue Detection
Utilidades de modelo para detección de criaderos de dengue
"""

import os
import glob
from .paths import get_default_model_paths, get_models_dir, get_project_root


def find_available_model():
    """Busca modelos YOLO disponibles en el proyecto"""
    possible_models = get_default_model_paths()

    for model_path in possible_models:
        if model_path.exists():
            return str(model_path)

    return None


def find_all_yolo_seg_models():
    """Busca todos los modelos YOLO-seg disponibles en el proyecto"""
    models_dir = get_models_dir()
    project_root = get_project_root()

    # Patrones de búsqueda para modelos de segmentación
    patterns = [
        str(models_dir / 'yolo11*-seg.pt'),
        str(project_root / 'yolo11*-seg.pt'),
        str(models_dir / 'yolov8*-seg.pt'),
        str(project_root / 'yolov8*-seg.pt')
    ]

    found_models = []

    for pattern in patterns:
        for model_path in glob.glob(pattern):
            if os.path.isfile(model_path):
                found_models.append(model_path)

    # Eliminar duplicados y ordenar por tamaño (n, s, m, l, x)
    unique_models = list(set(found_models))

    # Ordenar por prioridad: n (nano) -> s (small) -> m (medium) -> l (large) -> x (extra large)
    size_order = {'n': 1, 's': 2, 'm': 3, 'l': 4, 'x': 5}

    def get_model_size_priority(model_path):
        model_name = os.path.basename(model_path).lower()
        for size in size_order:
            if f'{size}-seg' in model_name or f'{size}.pt' in model_name:
                return size_order[size]
        return 999  # Unknown size goes to the end

    unique_models.sort(key=get_model_size_priority)

    return unique_models


def get_yolo_model_specs():
    """Retorna especificaciones de modelos YOLO según tamaño"""
    return {
        'n': {
            'name': 'Nano',
            'speed': 'Muy rápido',
            'accuracy': 'Básica',
            'params': '3.2M',
            'size_mb': '6.2',
            'recommended_for': 'Desarrollo rápido, CPUs débiles'
        },
        's': {
            'name': 'Small',
            'speed': 'Rápido',
            'accuracy': 'Buena',
            'params': '11.2M',
            'size_mb': '22.5',
            'recommended_for': 'Equilibrio velocidad/precisión'
        },
        'm': {
            'name': 'Medium',
            'speed': 'Medio',
            'accuracy': 'Muy buena',
            'params': '25.9M',
            'size_mb': '52.0',
            'recommended_for': 'Producción general'
        },
        'l': {
            'name': 'Large',
            'speed': 'Lento',
            'accuracy': 'Excelente',
            'params': '43.7M',
            'size_mb': '87.7',
            'recommended_for': 'Alta precisión, GPUs potentes'
        },
        'x': {
            'name': 'Extra Large',
            'speed': 'Muy lento',
            'accuracy': 'Máxima',
            'params': '68.2M',
            'size_mb': '136.7',
            'recommended_for': 'Máxima precisión, investigación'
        }
    }


def get_model_info(model_path):
    """Obtiene informacion basica del modelo"""
    if not os.path.exists(model_path):
        return None

    info = {
        'path': model_path,
        'size_mb': os.path.getsize(model_path) / 1024**2,
        'is_segmentation': 'seg' in model_path.lower() or 'best' in model_path.lower(),
        'is_trained': 'best' in model_path.lower()
    }

    return info


def cleanup_unwanted_downloads():
    """Elimina descargas no deseadas de YOLO"""
    unwanted_files = ['yolo11n.pt', 'yolov8n.pt', 'yolov8s.pt']

    for filename in unwanted_files:
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print(f"Eliminado archivo no deseado: {filename}")
            except:
                pass