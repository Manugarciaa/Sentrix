"""
Utilidades comunes para el proyecto YOLO Dengue Detection
"""
import os
import sys
import logging
import torch
from pathlib import Path

logger = logging.getLogger(__name__)

def setup_project_path():
    """
    Configura el path del proyecto para imports
    DEPRECATED: Use proper package imports instead (e.g., from sentrix_shared import X)
    This function is kept for backward compatibility but should not be used in new code.
    """
    import warnings
    warnings.warn(
        "setup_project_path() is deprecated. Use proper package imports instead.",
        DeprecationWarning,
        stacklevel=2
    )
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))

def detect_device():
    """Detecta automaticamente GPU/CPU y advierte si es necesario"""
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        memory_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
        logger.info(f"GPU detectada: {device_name} ({memory_gb:.1f}GB)")
        return 'cuda'
    else:
        logger.warning("GPU no disponible - usando CPU")
        logger.warning("ADVERTENCIA: Entrenamiento sera significativamente mas lento")
        logger.info("Para GPU: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
        return 'cpu'

def validate_file_exists(file_path, file_type="archivo"):
    """Valida que un archivo existe"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_type} no encontrado: {file_path}")
    return True

def validate_model_file(model_path):
    """Valida que el archivo del modelo existe y es valido"""
    if not model_path.endswith('.pt'):
        raise ValueError(f"El modelo debe ser un archivo .pt: {model_path}")
    validate_file_exists(model_path, "Modelo")
    return True

def get_image_extensions():
    """Retorna extensiones de imagen soportadas"""
    return ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.webp']

def ensure_directory(directory_path):
    """Asegura que un directorio existe"""
    os.makedirs(directory_path, exist_ok=True)
    return directory_path

def print_section_header(title):
    """Imprime encabezado de seccion formateado"""
    logger.info(f"\n{'='*3} {title.upper()} {'='*3}")

def get_system_info():
    """Obtiene informacion del sistema para debugging"""
    info = {
        'python_version': sys.version,
        'pytorch_version': torch.__version__,
        'cuda_available': torch.cuda.is_available(),
        'device_count': torch.cuda.device_count() if torch.cuda.is_available() else 0
    }
    
    if info['cuda_available']:
        info['cuda_version'] = torch.version.cuda
        info['cudnn_version'] = torch.backends.cudnn.version()
        
        # Información de GPUs
        gpus = []
        for i in range(info['device_count']):
            props = torch.cuda.get_device_properties(i)
            gpus.append({
                'name': props.name,
                'memory_gb': props.total_memory / 1024**3,
                'compute_capability': f"{props.major}.{props.minor}"
            })
        info['gpus'] = gpus
    
    return info

def find_available_model():
    """Busca modelos YOLO disponibles en el proyecto"""
    possible_models = [
        'models/best.pt',           # Modelo entrenado
        'models/yolo11n-seg.pt',    # Modelo base de segmentacion
        'models/yolo11s-seg.pt',    # Modelo small de segmentacion
        'models/yolo11m-seg.pt',    # Modelo medium de segmentacion
        'yolo11n-seg.pt',           # Fallback en raiz
    ]
    
    for model_path in possible_models:
        if os.path.exists(model_path):
            return model_path
    
    return None

def find_all_yolo_seg_models():
    """Busca todos los modelos YOLO-seg disponibles en el proyecto"""
    import glob
    
    # Patrones de búsqueda para modelos de segmentación
    patterns = [
        'models/yolo11*-seg.pt',
        'yolo11*-seg.pt',
        'models/yolov8*-seg.pt',
        'yolov8*-seg.pt'
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
                logger.info(f"Eliminado archivo no deseado: {filename}")
            except:
                pass