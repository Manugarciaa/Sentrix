"""
Utility modules for YOLO Dengue Detection
Módulos utilitarios para detección de criaderos de dengue
"""

from .device import detect_device, get_system_info
from .file_ops import validate_file_exists, validate_model_file, ensure_directory
from .model_utils import (
    find_available_model,
    find_all_yolo_seg_models,
    get_yolo_model_specs,
    get_model_info,
    cleanup_unwanted_downloads
)
from .paths import (
    get_project_root,
    get_models_dir,
    get_configs_dir,
    get_data_dir,
    get_predictions_dir,
    get_results_dir,
    resolve_path,
    resolve_model_path,
    ensure_project_directories,
    get_default_dataset_config,
    get_default_model_paths
)

__all__ = [
    'detect_device',
    'get_system_info',
    'validate_file_exists',
    'validate_model_file',
    'ensure_directory',
    'find_available_model',
    'find_all_yolo_seg_models',
    'get_yolo_model_specs',
    'get_model_info',
    'cleanup_unwanted_downloads',
    'get_project_root',
    'get_models_dir',
    'get_configs_dir',
    'get_data_dir',
    'get_predictions_dir',
    'get_results_dir',
    'resolve_path',
    'resolve_model_path',
    'ensure_project_directories',
    'get_default_dataset_config',
    'get_default_model_paths'
]