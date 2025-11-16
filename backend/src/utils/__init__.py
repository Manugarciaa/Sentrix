"""
Utility functions for Sentrix Backend
Funciones de utilidad para el backend Sentrix
"""

from .paths import get_project_root, get_configs_dir, get_logs_dir
from .database_utils import get_db_context
# Auth utilities are in auth.py (AuthService class)

# Simple validation function
def validate_connection():
    """Simple connection validation"""
    try:
        from ..database.connection import test_connection
        return test_connection()
    except Exception:
        return False

__all__ = [
    'get_project_root',
    'get_configs_dir',
    'get_logs_dir',
    'get_db_context',
    'validate_connection'
]