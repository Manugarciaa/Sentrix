"""
Training module for YOLO Dengue Detection
Módulo de entrenamiento para detección de criaderos de dengue
"""

import os
from datetime import datetime
from ultralytics import YOLO

from ..utils import (
    detect_device, validate_file_exists, validate_model_file, cleanup_unwanted_downloads,
    get_models_dir, get_default_dataset_config, resolve_path, resolve_model_path, ensure_project_directories
)


def train_dengue_model(model_path='yolo11n-seg.pt',
                      data_config=None,
                      epochs=100,
                      experiment_name=None):
    """Entrena modelo YOLOv11-seg para detección de criaderos"""
    # Asegurar que los directorios del proyecto existen
    ensure_project_directories()

    # Usar dataset config por defecto si no se especifica
    if data_config is None:
        data_config = str(get_default_dataset_config())

    # Resolver paths de forma portable
    model_path = str(resolve_model_path(model_path))  # Busca primero en models/
    data_config = str(resolve_path(data_config))

    # Validar archivos usando funciones utilitarias
    if os.path.exists(model_path):
        validate_model_file(model_path)
    validate_file_exists(data_config, "Configuración de dataset")

    # Detectar dispositivo automáticamente
    device = detect_device()

    # Generar nombre del experimento
    if experiment_name is None:
        model_size = 'unknown'
        model_name = os.path.basename(model_path).lower()

        for size in ['n', 's', 'm', 'l', 'x']:
            if f'{size}-seg' in model_name:
                model_size = size
                break

        # Usar solo fecha sin hora para evitar múltiples carpetas por día
        date_str = datetime.now().strftime("%Y%m%d")
        base_name = f"dengue_seg_{model_size}_{epochs}ep_{date_str}"

        # Siempre usar el mismo nombre base para evitar múltiples carpetas
        experiment_name = base_name

    try:
        print(f"Iniciando entrenamiento con {model_path}...")
        print(f"Experimento: {experiment_name}")
        # Evitar descargas innecesarias de YOLO
        os.environ['YOLO_VERBOSE'] = 'False'
        os.environ['YOLO_AUTODOWNLOAD'] = 'False'

        model = YOLO(model_path)
        results = model.train(
            data=data_config,
            task='segment',
            epochs=epochs,
            imgsz=640,
            batch=1,
            device=device,
            patience=50,
            project=str(get_models_dir()),
            name=experiment_name,
            exist_ok=True,  # Permite sobrescribir carpeta existente
            lr0=0.001,
            weight_decay=0.001,
            mosaic=0.5,
            copy_paste=0.3,
            amp=False  # Deshabilitar AMP para evitar descargas
        )
        print("Entrenamiento completado exitosamente")
        # Limpiar descargas no deseadas inmediatamente
        cleanup_unwanted_downloads()
        return results
    except Exception as e:
        print(f"Error durante el entrenamiento: {e}")
        raise