"""
Import utilities for Sentrix project
Utilidades de importación para el proyecto Sentrix

Optimized import management and dependency resolution
Gestión optimizada de imports y resolución de dependencias
"""

import sys
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
import importlib.util


class ImportManager:
    """
    Manages imports and Python path for Sentrix services
    Gestiona imports y el path de Python para servicios Sentrix
    """

    def __init__(self, service_root: Optional[Path] = None):
        self.service_root = Path(service_root) if service_root else Path.cwd()
        self.project_root = self._find_project_root()
        self._paths_added = set()

    def _find_project_root(self) -> Path:
        """Find the project root directory (contains 'shared' folder)"""
        current = self.service_root
        while current.parent != current:
            if (current / 'shared').exists():
                return current
            current = current.parent

        # If not found, assume current directory's parent
        return self.service_root.parent

    def setup_paths(self, service_name: Optional[str] = None) -> None:
        """
        Setup Python paths for optimal imports
        Configurar paths de Python para imports óptimos
        """
        paths_to_add = [
            self.project_root,          # Project root (for shared)
            self.service_root,          # Service root
            self.service_root / 'src',  # Service src directory
        ]

        # Add shared directory explicitly
        shared_dir = self.project_root / 'shared'
        if shared_dir.exists():
            paths_to_add.append(shared_dir)

        # Add paths to sys.path if not already present
        for path in paths_to_add:
            path_str = str(path.resolve())
            if path_str not in sys.path and path_str not in self._paths_added:
                sys.path.insert(0, path_str)
                self._paths_added.add(path_str)

    def import_shared_module(self, module_name: str, from_items: Optional[List[str]] = None):
        """
        Import shared module with error handling
        Importar módulo compartido con manejo de errores
        """
        try:
            shared_module_path = f"shared.{module_name}"
            module = importlib.import_module(shared_module_path)

            if from_items:
                result = {}
                for item in from_items:
                    if hasattr(module, item):
                        result[item] = getattr(module, item)
                    else:
                        raise ImportError(f"Cannot import '{item}' from '{shared_module_path}'")
                return result
            else:
                return module

        except ImportError as e:
            raise ImportError(f"Failed to import shared module '{module_name}': {e}")

    def check_dependencies(self) -> Dict[str, bool]:
        """
        Check if all required dependencies are available
        Verificar si todas las dependencias requeridas están disponibles
        """
        required_modules = [
            'fastapi',
            'uvicorn',
            'pydantic',
            'sqlalchemy',
            'alembic',
            'psycopg2',
            'pillow',
            'httpx',
            'pytest'
        ]

        optional_modules = [
            'ultralytics',  # For YOLO service
            'torch',        # For YOLO service
            'opencv-python' # For YOLO service
        ]

        results = {}

        # Check required modules
        for module in required_modules:
            try:
                importlib.import_module(module.replace('-', '_'))
                results[module] = True
            except ImportError:
                results[module] = False

        # Check optional modules
        for module in optional_modules:
            try:
                importlib.import_module(module.replace('-', '_'))
                results[f"{module} (optional)"] = True
            except ImportError:
                results[f"{module} (optional)"] = False

        return results

    def get_import_template(self, service_name: str) -> str:
        """
        Get optimized import template for service
        Obtener template de imports optimizado para el servicio
        """
        if service_name == 'backend':
            return '''
# Standard imports
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Database imports
from sqlalchemy.orm import Session
import asyncpg

# Shared library imports
from shared import (
    assess_dengue_risk,
    DetectionRiskEnum,
    BreedingSiteTypeEnum,
    validate_image_file,
    extract_gps_from_exif,
    setup_backend_logging,
    SentrixError,
    ValidationError,
    load_service_config
)

# Local imports
from .models import Base, Analysis, Detection
from .schemas import AnalysisResponse, AnalysisRequest
from .services import analysis_service
'''

        elif service_name == 'yolo-service':
            return '''
# Standard imports
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# FastAPI imports
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ML/AI imports
from ultralytics import YOLO
import torch
import cv2
from PIL import Image

# Shared library imports
from shared import (
    assess_dengue_risk,
    DetectionRiskEnum,
    BreedingSiteTypeEnum,
    validate_image_file,
    extract_gps_from_exif,
    setup_yolo_logging,
    SentrixError,
    ImageProcessingError,
    load_service_config
)

# Local imports
from .core import detect_breeding_sites, assess_dengue_risk
from .utils import validate_model_file, log_section_header
'''

        else:
            return '''
# Standard imports
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Shared library imports
from shared import (
    setup_shared_logging,
    SentrixError,
    load_service_config
)
'''


def setup_service_imports(service_name: str, service_root: Optional[Path] = None) -> ImportManager:
    """
    Setup optimized imports for a Sentrix service
    Configurar imports optimizados para un servicio Sentrix
    """
    manager = ImportManager(service_root)
    manager.setup_paths(service_name)
    return manager


def safe_import(module_name: str, from_items: Optional[List[str]] = None, fallback=None):
    """
    Safely import module with fallback
    Importar módulo de forma segura con fallback
    """
    try:
        module = importlib.import_module(module_name)

        if from_items:
            result = {}
            for item in from_items:
                result[item] = getattr(module, item, fallback)
            return result
        else:
            return module

    except ImportError:
        if from_items and fallback is not None:
            return {item: fallback for item in from_items}
        return fallback


def lazy_import(module_name: str):
    """
    Lazy import decorator for optional dependencies
    Decorador de importación lazy para dependencias opcionales
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                module = importlib.import_module(module_name)
                return func(module, *args, **kwargs)
            except ImportError as e:
                raise ImportError(f"Required module '{module_name}' not available: {e}")
        return wrapper
    return decorator


def get_available_backends() -> Dict[str, bool]:
    """
    Check which ML/AI backends are available
    Verificar qué backends de ML/AI están disponibles
    """
    backends = {
        'torch': False,
        'ultralytics': False,
        'opencv': False,
        'pillow': False,
        'numpy': False
    }

    for backend in backends:
        try:
            module_map = {
                'opencv': 'cv2',
                'pillow': 'PIL'
            }
            module_name = module_map.get(backend, backend)
            importlib.import_module(module_name)
            backends[backend] = True
        except ImportError:
            pass

    return backends


def validate_service_dependencies(service_name: str) -> Dict[str, Any]:
    """
    Validate that service has all required dependencies
    Validar que el servicio tenga todas las dependencias requeridas
    """
    dependency_requirements = {
        'backend': {
            'required': ['fastapi', 'uvicorn', 'sqlalchemy', 'psycopg2', 'httpx'],
            'optional': ['redis', 'celery']
        },
        'yolo-service': {
            'required': ['fastapi', 'uvicorn', 'ultralytics', 'torch', 'pillow'],
            'optional': ['opencv-python', 'matplotlib']
        },
        'shared': {
            'required': ['pydantic', 'pyyaml'],
            'optional': ['pytest']
        }
    }

    requirements = dependency_requirements.get(service_name, {'required': [], 'optional': []})
    results = {
        'service': service_name,
        'all_required_available': True,
        'missing_required': [],
        'missing_optional': [],
        'available_modules': []
    }

    # Check required dependencies
    for module in requirements['required']:
        try:
            importlib.import_module(module.replace('-', '_'))
            results['available_modules'].append(module)
        except ImportError:
            results['missing_required'].append(module)
            results['all_required_available'] = False

    # Check optional dependencies
    for module in requirements['optional']:
        try:
            importlib.import_module(module.replace('-', '_'))
            results['available_modules'].append(f"{module} (optional)")
        except ImportError:
            results['missing_optional'].append(module)

    return results


def create_requirements_file(service_name: str, output_path: Optional[Path] = None) -> str:
    """
    Create optimized requirements.txt for service
    Crear requirements.txt optimizado para el servicio
    """
    requirements = {
        'backend': [
            '# Backend Service Requirements',
            'fastapi==0.104.1',
            'uvicorn[standard]==0.24.0',
            'sqlalchemy==2.0.23',
            'alembic==1.12.1',
            'asyncpg==0.29.0',
            'psycopg2-binary==2.9.9',
            'httpx==0.25.2',
            'python-multipart==0.0.6',
            'pydantic-settings==2.0.3',
            'python-dotenv==1.0.0',
            'pillow==10.1.0',
            'pyyaml>=6.0',
            '',
            '# Testing',
            'pytest==7.4.3',
            'pytest-asyncio==0.21.1',
            'pytest-cov==4.1.0'
        ],
        'yolo-service': [
            '# YOLO Service Requirements',
            'fastapi==0.104.1',
            'uvicorn[standard]==0.24.0',
            'ultralytics>=8.3.0',
            'torch>=2.0.0',
            'torchvision>=0.15.0',
            'pillow>=9.0.0',
            'opencv-python-headless>=4.8.0',
            'numpy>=1.21.0',
            'pyyaml>=6.0',
            'python-multipart>=0.0.6',
            '',
            '# Testing',
            'pytest>=7.4.0'
        ],
        'shared': [
            '# Shared Library Requirements',
            'pydantic>=2.0.0',
            'pyyaml>=6.0',
            'pillow>=9.0.0',
            '',
            '# Testing',
            'pytest>=7.4.0'
        ]
    }

    content = '\n'.join(requirements.get(service_name, []))

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding='utf-8')

    return content


# Global import manager instance
_import_managers: Dict[str, ImportManager] = {}


def get_import_manager(service_name: str, service_root: Optional[Path] = None) -> ImportManager:
    """Get or create import manager for service"""
    if service_name not in _import_managers:
        _import_managers[service_name] = ImportManager(service_root)
        _import_managers[service_name].setup_paths(service_name)
    return _import_managers[service_name]