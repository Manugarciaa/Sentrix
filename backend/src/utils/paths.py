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


def get_configs_dir():
    """Get configs directory path"""
    return get_project_root() / "configs"


def get_logs_dir():
    """Get logs directory path"""
    logs_dir = get_project_root() / "logs"
    logs_dir.mkdir(exist_ok=True)
    return logs_dir


# For backwards compatibility with existing imports
def get_database_url_from_env():
    """Get database URL from environment variables"""
    return os.getenv("DATABASE_URL", "postgresql://localhost:5432/sentrix")