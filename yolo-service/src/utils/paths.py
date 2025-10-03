"""
Path utilities for YOLO Dengue Detection
Utilidades de paths para hacer el proyecto portable entre diferentes PCs
"""

import os
from pathlib import Path


def get_project_root():
    """Obtiene la raíz del proyecto de forma dinámica"""
    # Busca desde el archivo actual hacia arriba hasta encontrar el directorio yolo-service
    current_file = Path(__file__).resolve()

    # Desde src/utils/paths.py, subir 2 niveles para llegar a la raíz del proyecto
    project_root = current_file.parent.parent.parent

    return project_root


def get_data_dir():
    """Directorio de datos del proyecto"""
    return get_project_root() / "data"


def get_models_dir():
    """Directorio de modelos del proyecto"""
    return get_project_root() / "models"


def get_configs_dir():
    """Directorio de configuraciones del proyecto"""
    return get_project_root() / "configs"


def get_predictions_dir():
    """Directorio de predicciones del proyecto"""
    return get_project_root() / "predictions"


def get_results_dir():
    """Directorio de resultados del proyecto"""
    return get_project_root() / "results"


def get_test_images_dir():
    """Directorio de imágenes de prueba"""
    return get_project_root() / "test_images"


def ensure_project_directories():
    """Asegura que todos los directorios del proyecto existen"""
    dirs_to_create = [
        get_data_dir(),
        get_models_dir(),
        get_configs_dir(),
        get_predictions_dir(),
        get_results_dir(),
        get_test_images_dir()
    ]

    for directory in dirs_to_create:
        directory.mkdir(parents=True, exist_ok=True)

    return dirs_to_create


def get_default_dataset_config():
    """Path por defecto del archivo de configuración del dataset"""
    return get_configs_dir() / "dataset.yaml"


def get_default_model_paths():
    """Lista de paths de modelos por defecto a buscar"""
    models_dir = get_models_dir()

    return [
        models_dir / "best.pt",           # Modelo entrenado
        models_dir / "yolo11n-seg.pt",    # Modelo base de segmentación
        models_dir / "yolo11s-seg.pt",    # Modelo small de segmentación
        models_dir / "yolo11m-seg.pt",    # Modelo medium de segmentación
        get_project_root() / "yolo11n-seg.pt",  # Fallback en raíz
    ]


def resolve_path(path_str):
    """
    Resuelve un path que puede ser relativo o absoluto
    Si es relativo, lo resuelve desde la raíz del proyecto
    """
    path = Path(path_str)

    if path.is_absolute():
        return path
    else:
        # Path relativo - resolverlo desde la raíz del proyecto
        return get_project_root() / path


def resolve_model_path(model_path_str):
    """
    Resuelve un path de modelo buscando primero en el directorio de modelos
    Esto evita que YOLO descargue modelos cuando ya existen localmente
    """
    # Si es un path absoluto y existe, usarlo directamente
    if Path(model_path_str).is_absolute():
        if Path(model_path_str).exists():
            return Path(model_path_str)
        else:
            raise FileNotFoundError(f"Modelo no encontrado: {model_path_str}")

    # Para paths relativos, buscar en orden de prioridad:
    models_dir = get_models_dir()
    project_root = get_project_root()

    # 1. Buscar en directorio de modelos
    model_in_models_dir = models_dir / model_path_str
    if model_in_models_dir.exists():
        return model_in_models_dir

    # 2. Buscar en raíz del proyecto
    model_in_root = project_root / model_path_str
    if model_in_root.exists():
        return model_in_root

    # 3. Si no existe localmente, permitir que YOLO lo descargue
    # pero retornar el path donde debería estar en models/
    print(f"[WARN] Modelo {model_path_str} no encontrado localmente.")
    print(f"       YOLO lo descargará automáticamente.")
    print(f"       Recomendación: Mover el modelo descargado a {models_dir}/")

    return project_root / model_path_str  # Dejar que YOLO lo descargue en raíz


def get_home_directory():
    """Obtiene el directorio home del usuario actual (portable)"""
    return Path.home()


def get_user_documents():
    """Obtiene el directorio de documentos del usuario (portable)"""
    home = get_home_directory()

    # En Windows: Documents, en Linux/Mac: Documents (si existe) o home
    documents_dir = home / "Documents"
    if documents_dir.exists():
        return documents_dir
    else:
        return home


# Variables de entorno para configuración
PROJECT_ROOT = get_project_root()
DATA_DIR = get_data_dir()
MODELS_DIR = get_models_dir()
CONFIGS_DIR = get_configs_dir()
PREDICTIONS_DIR = get_predictions_dir()
RESULTS_DIR = get_results_dir()