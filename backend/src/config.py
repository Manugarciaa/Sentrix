"""
Configuration for Sentrix Backend
"""

import os
from typing import Dict, Any

class Settings:
    def __init__(self):
        self.yolo_service_url = os.getenv("YOLO_SERVICE_URL", "http://localhost:8001")
        self.backend_host = os.getenv("BACKEND_HOST", "0.0.0.0")
        self.backend_port = int(os.getenv("BACKEND_PORT", "8000"))
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")

        # Supabase settings (if used)
        self.supabase_url = os.getenv("SUPABASE_URL", "")
        self.supabase_key = os.getenv("SUPABASE_KEY", "")

        # Security settings
        self.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

def _get_settings():
    return Settings()

# Re-export for compatibility
def get_settings():
    """Get application settings - compatibility wrapper"""
    return _get_settings()

__all__ = ["get_settings", "Settings"]
