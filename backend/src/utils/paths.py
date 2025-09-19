"""
Path utilities for Sentrix Backend - Portable across different systems
Utilidades de paths para Sentrix Backend - Portables entre sistemas

Following yolo-service pattern for automatic path resolution
Siguiendo el patrón de yolo-service para resolución automática de paths
"""

import os
from pathlib import Path


def get_project_root():
    """
    Get the project root directory automatically
    Obtener el directorio raíz del proyecto automáticamente
    """
    return Path(__file__).parent.parent.parent


def get_src_dir():
    """Get src directory path"""
    return get_project_root() / "src"


def get_configs_dir():
    """Get configs directory path"""
    return get_project_root() / "configs"


def get_logs_dir():
    """Get logs directory path"""
    logs_dir = get_project_root() / "logs"
    logs_dir.mkdir(exist_ok=True)
    return logs_dir


def get_app_dir():
    """Get app directory path (for legacy compatibility)"""
    return get_project_root() / "app"


def get_tests_dir():
    """Get tests directory path"""
    return get_project_root() / "tests"


def get_scripts_dir():
    """Get scripts directory path"""
    return get_project_root() / "scripts"


def get_alembic_dir():
    """Get alembic directory path"""
    return get_project_root() / "alembic"


def ensure_directory_exists(directory_path):
    """
    Ensure a directory exists, create if it doesn't
    Asegurar que un directorio existe, crear si no existe
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)
    return directory_path


def get_default_config_file():
    """Get default configuration file path"""
    return get_configs_dir() / "settings.yaml"


# For backwards compatibility with existing imports
def get_database_url_from_env():
    """Get database URL from environment variables"""
    return os.getenv("DATABASE_URL", "postgresql://localhost:5432/sentrix")