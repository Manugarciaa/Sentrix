"""
Configuration settings for Sentrix Backend
Configuraciones para Sentrix Backend

Following yolo-service pattern for automatic configuration loading
Siguiendo el patrón de yolo-service para carga automática de configuración
"""

import os
import yaml
from typing import List, Optional, Dict, Any
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


def get_configs_dir():
    """Get configs directory path"""
    return Path(__file__).parent


class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/sentrix"
    )
    pool_size: int = 10
    max_overflow: int = 20
    pool_pre_ping: bool = True
    pool_recycle: int = 300
    enable_postgis: bool = True

    class Config:
        extra = "ignore"


class APISettings(BaseSettings):
    """API configuration settings"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    reload: bool = False

    title: str = "Sentrix API"
    description: str = "Sistema de Detección de Criaderos de Aedes aegypti"
    version: str = "1.0.0"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"

    class Config:
        extra = "ignore"  # Ignore extra fields


class ExternalServicesSettings(BaseSettings):
    """External services configuration"""
    yolo_service_url: str = os.getenv("YOLO_SERVICE_URL", "http://localhost:8002")
    yolo_service_timeout: int = 30

    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_ttl: int = 3600

    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    supabase_jwt_secret: str = os.getenv("SUPABASE_JWT_SECRET", "")

    class Config:
        extra = "ignore"


class SecuritySettings(BaseSettings):
    """Security configuration"""
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "development-secret-key")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    secret_key: str = os.getenv("SECRET_KEY", "development-secret-key")

    class Config:
        extra = "ignore"


class FileHandlingSettings(BaseSettings):
    """File handling configuration"""
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 50
    allowed_extensions: List[str] = ["jpg", "jpeg", "png", "tiff"]
    cleanup_temp_files: bool = True
    temp_file_retention_hours: int = 24

    class Config:
        extra = "ignore"


class Settings(BaseSettings):
    """Main settings class combining all configurations"""

    # Sub-configurations
    database: DatabaseSettings = DatabaseSettings()
    api: APISettings = APISettings()
    external_services: ExternalServicesSettings = ExternalServicesSettings()
    security: SecuritySettings = SecuritySettings()
    file_handling: FileHandlingSettings = FileHandlingSettings()

    # CORS
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://app.sentrix.com",
        "https://admin.sentrix.com"
    ]

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv("LOG_FORMAT", "detailed")
    log_file: str = os.getenv("LOG_FILE", "./logs/backend.log")

    # Legacy compatibility
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/sentrix")
    secret_key: str = os.getenv("SECRET_KEY", "development-secret-key")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    supabase_service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    yolo_service_url: str = os.getenv("YOLO_SERVICE_URL", "http://localhost:8002")
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: str = ".jpg,.jpeg,.png,.tiff,.bmp"

    class Config:
        env_file = ".env"

    @classmethod
    def load_from_yaml(cls, config_file: Optional[str] = None) -> "Settings":
        """
        Load settings from YAML configuration file
        Cargar configuraciones desde archivo YAML
        """
        if not config_file:
            config_file = get_configs_dir() / "api.yaml"

        if not Path(config_file).exists():
            return cls()

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)

            # Create settings with YAML data
            settings = cls()

            # Update API settings
            if 'api' in config_data:
                api_data = config_data['api']
                settings.api = APISettings(**api_data)

                # Update CORS if present
                if 'cors' in api_data:
                    settings.allowed_origins = api_data['cors'].get('allow_origins', settings.allowed_origins)

            # Update external services
            if 'external_services' in config_data:
                ext_data = config_data['external_services']

                # YOLO Service
                if 'yolo_service' in ext_data:
                    yolo_config = ext_data['yolo_service']
                    settings.external_services.yolo_service_url = yolo_config.get('url', settings.external_services.yolo_service_url)
                    settings.external_services.yolo_service_timeout = yolo_config.get('timeout', settings.external_services.yolo_service_timeout)

                # Redis
                if 'redis' in ext_data:
                    redis_config = ext_data['redis']
                    settings.external_services.redis_url = redis_config.get('url', settings.external_services.redis_url)
                    settings.external_services.redis_ttl = redis_config.get('ttl', settings.external_services.redis_ttl)

                # Supabase
                if 'supabase' in ext_data:
                    supabase_config = ext_data['supabase']
                    settings.external_services.supabase_url = supabase_config.get('url', settings.external_services.supabase_url)
                    settings.external_services.supabase_key = supabase_config.get('anon_key', settings.external_services.supabase_key)
                    settings.external_services.supabase_jwt_secret = supabase_config.get('jwt_secret', settings.external_services.supabase_jwt_secret)

            # Update file handling
            if 'file_handling' in config_data:
                file_data = config_data['file_handling']
                settings.file_handling = FileHandlingSettings(**file_data)

            # Update security
            if 'security' in config_data:
                security_data = config_data['security']
                if 'jwt' in security_data:
                    jwt_config = security_data['jwt']
                    settings.security.jwt_secret_key = jwt_config.get('secret_key', settings.security.jwt_secret_key)
                    settings.security.jwt_algorithm = jwt_config.get('algorithm', settings.security.jwt_algorithm)
                    settings.security.jwt_expiration_hours = jwt_config.get('expiration_hours', settings.security.jwt_expiration_hours)

            # Update logging
            if 'logging' in config_data:
                logging_data = config_data['logging']
                settings.log_level = logging_data.get('level', settings.log_level)
                settings.log_format = logging_data.get('format', settings.log_format)
                settings.log_file = logging_data.get('file', settings.log_file)

            return settings

        except Exception as e:
            print(f"ERROR: Error loading YAML configuration: {e}")
            return cls()

    def load_database_config(self) -> DatabaseSettings:
        """
        Load database configuration from database.yaml
        Cargar configuración de base de datos desde database.yaml
        """
        config_file = get_configs_dir() / "database.yaml"

        if not config_file.exists():
            return self.database

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)

            if 'database' in config_data:
                db_config = config_data['database']

                # Build database URL if individual components are provided
                if all(key in db_config for key in ['host', 'port', 'name', 'user', 'password']):
                    db_url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['name']}"
                    db_config['url'] = db_url

                return DatabaseSettings(**db_config)

        except Exception as e:
            print(f"ERROR: Error loading database configuration: {e}")

        return self.database


# Global settings instance
_settings: Optional[Settings] = None


@lru_cache()
def get_settings(reload: bool = False) -> Settings:
    """
    Get application settings with automatic YAML loading
    Obtener configuraciones de la aplicación con carga automática de YAML
    """
    global _settings

    if _settings is None or reload:
        # Try to load from YAML first, fallback to environment variables
        _settings = Settings.load_from_yaml()

        # Update database settings from database.yaml
        _settings.database = _settings.load_database_config()

    return _settings


def get_database_settings() -> DatabaseSettings:
    """Get database settings"""
    return get_settings().database


def get_api_settings() -> APISettings:
    """Get API settings"""
    return get_settings().api


def get_external_services_settings() -> ExternalServicesSettings:
    """Get external services settings"""
    return get_settings().external_services