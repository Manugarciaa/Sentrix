#!/usr/bin/env python3
"""
YOLO Service System Diagnostic
Diagnóstico del Sistema YOLO Service

Proporciona información sobre hardware, modelos disponibles y rendimiento.
"""

import os
import sys
import psutil
import platform
from pathlib import Path

# Add src to path for imports
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None

try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False

from src.utils.device import detect_device, get_system_info


def print_header(title):
    """Print section header"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print('='*50)


def get_system_info():
    """Get basic system information"""
    return {
        'platform': platform.system(),
        'platform_version': platform.version(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'cpu_count': psutil.cpu_count(),
        'memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
        'disk_free_gb': round(psutil.disk_usage('.').free / (1024**3), 2)
    }


def check_gpu_info():
    """Check GPU information"""
    gpu_info = {
        'cuda_available': False,
        'cuda_version': None,
        'gpu_count': 0,
        'gpu_names': [],
        'gpu_memory': []
    }

    if TORCH_AVAILABLE and torch.cuda.is_available():
        gpu_info['cuda_available'] = True
        gpu_info['cuda_version'] = torch.version.cuda
        gpu_info['gpu_count'] = torch.cuda.device_count()

        for i in range(gpu_info['gpu_count']):
            gpu_info['gpu_names'].append(torch.cuda.get_device_name(i))
            memory_gb = torch.cuda.get_device_properties(i).total_memory / (1024**3)
            gpu_info['gpu_memory'].append(round(memory_gb, 1))

    return gpu_info


def check_models():
    """Check available models"""
    models_dir = Path("models")
    models = {
        'models_directory_exists': models_dir.exists(),
        'available_models': [],
        'total_size_mb': 0
    }

    if models_dir.exists():
        for model_file in models_dir.glob("*.pt"):
            size_mb = model_file.stat().st_size / (1024**2)
            models['available_models'].append({
                'name': model_file.name,
                'size_mb': round(size_mb, 1),
                'path': str(model_file)
            })
            models['total_size_mb'] += size_mb

        models['total_size_mb'] = round(models['total_size_mb'], 1)

    return models


def get_recommended_model(gpu_memory_gb=0, cpu_cores=4):
    """Get recommended model based on hardware"""
    if gpu_memory_gb >= 8:
        return "yolo11l-seg.pt (Large - Mejor precisión)"
    elif gpu_memory_gb >= 6:
        return "yolo11m-seg.pt (Medium - Balanceado)"
    elif gpu_memory_gb >= 4:
        return "yolo11s-seg.pt (Small - GPU básica)"
    elif cpu_cores >= 8:
        return "yolo11s-seg.pt (Small - CPU potente)"
    else:
        return "yolo11n-seg.pt (Nano - Hardware limitado)"


def check_dependencies():
    """Check critical dependencies"""
    deps = {
        'torch': TORCH_AVAILABLE,
        'ultralytics': ULTRALYTICS_AVAILABLE,
        'versions': {}
    }

    if TORCH_AVAILABLE:
        deps['versions']['torch'] = torch.__version__

    try:
        import cv2
        deps['opencv'] = True
        deps['versions']['opencv'] = cv2.__version__
    except ImportError:
        deps['opencv'] = False

    try:
        import PIL
        deps['pillow'] = True
        deps['versions']['pillow'] = PIL.__version__
    except ImportError:
        deps['pillow'] = False

    return deps


def run_diagnostic():
    """Run complete diagnostic"""
    print_header("YOLO SERVICE DIAGNOSTIC")

    # System Information
    print_header("System Information")
    sys_info = get_system_info()
    print(f"Platform: {sys_info['platform']} {sys_info['architecture']}")
    print(f"Python: {sys_info['python_version']}")
    print(f"CPU Cores: {sys_info['cpu_count']}")
    print(f"Memory: {sys_info['memory_gb']} GB")
    print(f"Free Disk: {sys_info['disk_free_gb']} GB")

    # GPU Information
    print_header("GPU Information")
    gpu_info = check_gpu_info()
    if gpu_info['cuda_available']:
        print(f"CUDA Available: Yes (v{gpu_info['cuda_version']})")
        print(f"GPU Count: {gpu_info['gpu_count']}")
        for i, (name, memory) in enumerate(zip(gpu_info['gpu_names'], gpu_info['gpu_memory'])):
            print(f"  GPU {i}: {name} ({memory} GB)")
    else:
        print("CUDA Available: No")
        print("Recommendation: CPU inference only")

    # Device Detection
    print_header("Device Detection")
    try:
        device = detect_device()
        device_info = get_system_info()
        print(f"Detected Device: {device}")
        print("System Info:")
        for key, value in device_info.items():
            if key == 'gpus' and isinstance(value, list):
                for i, gpu in enumerate(value):
                    print(f"  GPU {i}: {gpu['name']} ({gpu['memory_gb']:.1f}GB)")
            elif key not in ['python_version']:  # Skip verbose python version
                print(f"  {key}: {value}")
    except Exception as e:
        print(f"Device detection failed: {e}")

    # Models
    print_header("Available Models")
    models = check_models()
    if models['models_directory_exists']:
        if models['available_models']:
            print(f"Models found: {len(models['available_models'])}")
            print(f"Total size: {models['total_size_mb']} MB")
            for model in models['available_models']:
                print(f"  - {model['name']} ({model['size_mb']} MB)")
        else:
            print("No models found in models/ directory")
    else:
        print("Models directory does not exist")

    # Recommendation
    print_header("Model Recommendation")
    max_gpu_memory = max(gpu_info['gpu_memory']) if gpu_info['gpu_memory'] else 0
    recommended = get_recommended_model(max_gpu_memory, sys_info['cpu_count'])
    print(f"Recommended model: {recommended}")

    # Dependencies
    print_header("Dependencies")
    deps = check_dependencies()
    status_ok = "OK"
    status_missing = "MISSING"

    print(f"PyTorch: {status_ok if deps['torch'] else status_missing}")
    print(f"Ultralytics: {status_ok if deps['ultralytics'] else status_missing}")
    print(f"OpenCV: {status_ok if deps['opencv'] else status_missing}")
    print(f"Pillow: {status_ok if deps['pillow'] else status_missing}")

    if deps['versions']:
        print("\nVersions:")
        for name, version in deps['versions'].items():
            print(f"  {name}: {version}")

    # Summary
    print_header("Summary")
    if gpu_info['cuda_available']:
        print("Status: GPU acceleration available")
        print("Performance: High")
    else:
        print("Status: CPU only")
        print("Performance: Moderate")

    critical_deps = deps['torch'] and deps['ultralytics'] and deps['opencv']
    print(f"Dependencies: {'Complete' if critical_deps else 'Incomplete'}")

    if models['available_models']:
        current_model = next((m for m in models['available_models'] if m['name'] == 'best.pt'), None)
        if current_model:
            print(f"Current model: {current_model['name']} ({current_model['size_mb']} MB)")
        else:
            print(f"Available models: {len(models['available_models'])}")
    else:
        print("Status: No models available - download required")


if __name__ == "__main__":
    try:
        run_diagnostic()
    except KeyboardInterrupt:
        print("\nDiagnostic interrupted")
    except Exception as e:
        print(f"\nError during diagnostic: {e}")