"""
Device detection utilities for YOLO Dengue Detection
Utilidades de detección de dispositivo para detección de criaderos de dengue
"""

import sys
import torch


def detect_device():
    """Detecta automaticamente GPU/CPU y advierte si es necesario"""
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        memory_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"GPU detectada: {device_name} ({memory_gb:.1f}GB)")
        return 'cuda'
    else:
        print("GPU no disponible - usando CPU")
        print("ADVERTENCIA: Entrenamiento sera significativamente mas lento")
        print("Para GPU: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
        return 'cpu'


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