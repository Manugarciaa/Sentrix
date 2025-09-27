"""
Settings for Sentrix Backend
Configuración para Sentrix Backend
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

        # Redis settings (if used)
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

        # Security settings
        self.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

        # Development settings
        self.debug = os.getenv("DEBUG", "false").lower() == "true"

def get_settings() -> Settings:
    """Get application settings"""
    return Settings()

# Instance for easy access
settings = get_settings()
