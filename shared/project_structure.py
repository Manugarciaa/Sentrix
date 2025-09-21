"""
Shared project structure configuration for Sentrix
Configuración de estructura de proyecto compartida para Sentrix

Defines standard directory layouts and utilities for both services
Define layouts de directorios estándar y utilidades para ambos servicios
"""

from pathlib import Path
from typing import Dict, List, Optional
import os


class ProjectStructure:
    """
    Standard project structure for Sentrix services
    Estructura de proyecto estándar para servicios Sentrix
    """

    def __init__(self, service_root: Path):
        self.service_root = Path(service_root)
        self.project_root = self.service_root.parent

    @property
    def shared_dir(self) -> Path:
        """Shared libraries directory"""
        return self.project_root / "shared"

    @property
    def src_dir(self) -> Path:
        """Source code directory"""
        return self.service_root / "src"

    @property
    def configs_dir(self) -> Path:
        """Configuration files directory"""
        return self.service_root / "configs"

    @property
    def tests_dir(self) -> Path:
        """Tests directory"""
        return self.service_root / "tests"

    @property
    def scripts_dir(self) -> Path:
        """Scripts directory"""
        return self.service_root / "scripts"

    @property
    def logs_dir(self) -> Path:
        """Logs directory"""
        return self.service_root / "logs"

    @property
    def data_dir(self) -> Path:
        """Data directory (for yolo-service)"""
        return self.service_root / "data"

    @property
    def models_dir(self) -> Path:
        """Models directory (for yolo-service)"""
        return self.service_root / "models"

    @property
    def results_dir(self) -> Path:
        """Results directory"""
        return self.service_root / "results"

    def ensure_standard_directories(self) -> Dict[str, Path]:
        """
        Create standard directories if they don't exist
        Crear directorios estándar si no existen
        """
        directories = {
            'src': self.src_dir,
            'configs': self.configs_dir,
            'tests': self.tests_dir,
            'scripts': self.scripts_dir,
            'logs': self.logs_dir,
            'results': self.results_dir
        }

        # Add service-specific directories
        service_name = self.service_root.name
        if service_name == 'yolo-service':
            directories.update({
                'data': self.data_dir,
                'models': self.models_dir
            })

        # Create directories
        for name, path in directories.items():
            path.mkdir(parents=True, exist_ok=True)

        return directories

    def get_module_path(self, module_parts: List[str]) -> Path:
        """
        Get path for a module within src directory
        Obtener ruta para un módulo dentro del directorio src
        """
        return self.src_dir.joinpath(*module_parts)

    def get_config_path(self, config_name: str) -> Path:
        """Get path for a configuration file"""
        return self.configs_dir / config_name

    def get_log_path(self, log_name: str) -> Path:
        """Get path for a log file"""
        return self.logs_dir / log_name

    def add_to_python_path(self):
        """Add directories to Python path for imports"""
        import sys

        paths_to_add = [
            str(self.service_root),
            str(self.src_dir),
            str(self.shared_dir)
        ]

        for path in paths_to_add:
            if path not in sys.path:
                sys.path.insert(0, path)


# Standard directory structures
BACKEND_STRUCTURE = {
    'src': {
        'core': ['analysis_processor.py', 'api_manager.py', 'detection_validator.py'],
        'database': {
            'models': ['__init__.py', 'enums.py', 'models.py'],
            'migrations': []
        },
        'utils': ['auth_utils.py', 'database_utils.py', 'paths.py'],
        'schemas': ['analyses.py']
    },
    'app': {
        'api': {
            'v1': ['analyses.py', 'health.py']
        },
        'models': ['enums.py'],
        'schemas': ['analyses.py'],
        'services': [],
        'utils': ['yolo_integration.py']
    },
    'configs': ['settings.py', 'alembic.ini'],
    'tests': [],
    'scripts': [],
    'logs': []
}

YOLO_SERVICE_STRUCTURE = {
    'src': {
        'core': ['detector.py', 'evaluator.py', 'trainer.py'],
        'utils': ['device.py', 'file_ops.py', 'gps_metadata.py', 'model_utils.py', 'paths.py'],
        'reports': ['generator.py']
    },
    'configs': ['classes.py', 'dataset.yaml'],
    'data': {
        'images': ['train', 'val', 'test'],
        'labels': ['train', 'val', 'test']
    },
    'models': [],
    'tests': [],
    'scripts': [],
    'results': [],
    'logs': []
}


def get_backend_structure() -> ProjectStructure:
    """Get backend project structure"""
    backend_root = Path(__file__).parent.parent / "backend"
    return ProjectStructure(backend_root)


def get_yolo_structure() -> ProjectStructure:
    """Get YOLO service project structure"""
    yolo_root = Path(__file__).parent.parent / "yolo-service"
    return ProjectStructure(yolo_root)


def setup_service_structure(service_name: str) -> ProjectStructure:
    """
    Setup standard structure for a service
    Configurar estructura estándar para un servicio
    """
    if service_name == 'backend':
        structure = get_backend_structure()
    elif service_name == 'yolo-service':
        structure = get_yolo_structure()
    else:
        raise ValueError(f"Unknown service: {service_name}")

    # Ensure directories exist
    structure.ensure_standard_directories()

    # Add to Python path
    structure.add_to_python_path()

    return structure


def normalize_import_path(from_service: str, to_module: str) -> str:
    """
    Normalize import path between services
    Normalizar ruta de importación entre servicios
    """
    # Map common import patterns
    import_patterns = {
        'shared': 'shared',
        'backend.src': 'src',
        'backend.app': 'app',
        'yolo.src': 'src',
        'yolo.configs': 'configs'
    }

    for pattern, replacement in import_patterns.items():
        if to_module.startswith(pattern):
            return to_module.replace(pattern, replacement, 1)

    return to_module


def validate_service_structure(service_name: str) -> Dict[str, bool]:
    """
    Validate that service follows standard structure
    Validar que el servicio sigue la estructura estándar
    """
    structure = setup_service_structure(service_name)
    validation_results = {}

    # Check standard directories
    standard_dirs = ['src', 'configs', 'tests', 'scripts', 'logs']
    if service_name == 'yolo-service':
        standard_dirs.extend(['data', 'models', 'results'])

    for dir_name in standard_dirs:
        dir_path = getattr(structure, f'{dir_name}_dir')
        validation_results[f'{dir_name}_exists'] = dir_path.exists()

    # Check critical files
    critical_files = {
        'backend': [
            'main.py',
            'app/main.py',
            'configs/settings.py'
        ],
        'yolo-service': [
            'main.py',
            'server.py',
            'configs/classes.py'
        ]
    }

    for file_path in critical_files.get(service_name, []):
        full_path = structure.service_root / file_path
        validation_results[f'{file_path}_exists'] = full_path.exists()

    return validation_results


def get_recommended_file_locations() -> Dict[str, Dict[str, str]]:
    """
    Get recommended locations for different types of files
    Obtener ubicaciones recomendadas para diferentes tipos de archivos
    """
    return {
        'backend': {
            'API endpoints': 'app/api/v1/',
            'Business logic': 'src/core/',
            'Database models': 'src/database/models/',
            'Schemas': 'src/schemas/',
            'Utilities': 'src/utils/',
            'Tests': 'tests/',
            'Scripts': 'scripts/',
            'Configuration': 'configs/'
        },
        'yolo-service': {
            'Core ML logic': 'src/core/',
            'Utilities': 'src/utils/',
            'Reports': 'src/reports/',
            'Configuration': 'configs/',
            'Tests': 'tests/',
            'Scripts': 'scripts/',
            'Models': 'models/',
            'Data': 'data/',
            'Results': 'results/'
        },
        'shared': {
            'Risk assessment': 'risk_assessment.py',
            'Data models': 'data_models.py',
            'File utilities': 'file_utils.py',
            'GPS utilities': 'gps_utils.py',
            'Logging utilities': 'logging_utils.py',
            'Project structure': 'project_structure.py'
        }
    }