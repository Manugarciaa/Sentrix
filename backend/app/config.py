"""
Configuration compatibility layer for app
"""

from config.settings import get_settings as _get_settings

# Re-export for compatibility
def get_settings():
    """Get application settings - compatibility wrapper"""
    return _get_settings()

# Export the main settings class for convenience
from config.settings import Settings

__all__ = ["get_settings", "Settings"]
