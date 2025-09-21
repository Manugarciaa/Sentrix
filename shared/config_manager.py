"""
Shared configuration management for Sentrix project
Gestión de configuración compartida para el proyecto Sentrix

Unified configuration loading, validation, and management
Carga, validación y gestión de configuración unificada
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field
from enum import Enum

from .error_handling import ValidationError, FileProcessingError
from .logging_utils import get_module_logger

logger = get_module_logger(__name__, 'shared')


class Environment(str, Enum):
    """Application environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str
    max_connections: int = 10
    timeout_seconds: int = 30
    retry_attempts: int = 3
    enable_logging: bool = False

    def validate(self):
        """Validate database configuration"""
        if not self.url:
            raise ValidationError("Database URL is required")
        if self.max_connections <= 0:
            raise ValidationError("Max connections must be positive")


@dataclass
class YoloServiceConfig:
    """YOLO service configuration"""
    url: str = "http://localhost:8002"
    timeout_seconds: float = 60.0
    max_retries: int = 3
    model_path: str = "models/best.pt"
    confidence_threshold: float = 0.5
    batch_size: int = 10

    def validate(self):
        """Validate YOLO service configuration"""
        if not self.url:
            raise ValidationError("YOLO service URL is required")
        if not 0.1 <= self.confidence_threshold <= 1.0:
            raise ValidationError("Confidence threshold must be between 0.1 and 1.0")


@dataclass
class CorsConfig:
    """CORS configuration"""
    allowed_origins: List[str] = field(default_factory=lambda: [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ])
    allow_credentials: bool = True
    allowed_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    allowed_headers: List[str] = field(default_factory=lambda: ["Content-Type", "Authorization"])

    def validate(self):
        """Validate CORS configuration"""
        if not self.allowed_origins:
            raise ValidationError("At least one allowed origin is required")


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_logging: bool = True
    console_logging: bool = True
    max_file_size_mb: int = 10
    backup_count: int = 5

    def validate(self):
        """Validate logging configuration"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level.upper() not in valid_levels:
            raise ValidationError(f"Invalid log level. Must be one of: {valid_levels}")


@dataclass
class SecurityConfig:
    """Security configuration"""
    jwt_secret_key: str = "development-secret-key"
    jwt_expiration_hours: int = 24
    max_file_size_mb: int = 50
    allowed_file_types: List[str] = field(default_factory=lambda: [
        ".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".heic"
    ])
    rate_limit_per_minute: int = 60

    def validate(self):
        """Validate security configuration"""
        if len(self.jwt_secret_key) < 16:
            raise ValidationError("JWT secret key must be at least 16 characters")
        if self.max_file_size_mb <= 0:
            raise ValidationError("Max file size must be positive")


@dataclass
class SentrixConfig:
    """Main Sentrix configuration"""
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    service_name: str = "sentrix"
    version: str = "1.0.0"

    # Service configurations
    database: Optional[DatabaseConfig] = None
    yolo_service: Optional[YoloServiceConfig] = None
    cors: CorsConfig = field(default_factory=CorsConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)

    # Service-specific settings
    extra_config: Dict[str, Any] = field(default_factory=dict)

    def validate(self):
        """Validate complete configuration"""
        if self.cors:
            self.cors.validate()
        if self.logging:
            self.logging.validate()
        if self.security:
            self.security.validate()
        if self.database:
            self.database.validate()
        if self.yolo_service:
            self.yolo_service.validate()

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == Environment.DEVELOPMENT


class ConfigManager:
    """
    Configuration manager for Sentrix services
    Gestor de configuración para servicios Sentrix
    """

    def __init__(self, service_name: str, config_dir: Optional[Path] = None):
        self.service_name = service_name
        self.config_dir = config_dir or Path("configs")
        self._config: Optional[SentrixConfig] = None

    def load_config(
        self,
        config_file: Optional[str] = None,
        environment: Optional[str] = None
    ) -> SentrixConfig:
        """
        Load configuration from file and environment
        Cargar configuración desde archivo y entorno
        """
        # Determine config file
        if not config_file:
            config_file = f"{self.service_name}.yaml"

        config_path = self.config_dir / config_file

        # Load base configuration
        config_data = self._load_yaml_config(config_path)

        # Override with environment variables
        config_data = self._apply_environment_overrides(config_data)

        # Set environment
        env = environment or os.getenv("SENTRIX_ENV", "development")
        config_data["environment"] = env

        # Create configuration object
        self._config = self._create_config_object(config_data)

        # Validate configuration
        self._config.validate()

        logger.info(f"Configuration loaded for {self.service_name} ({env})")
        return self._config

    def _load_yaml_config(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}. Using defaults.")
            return {}

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f) or {}
                logger.debug(f"Loaded config from: {config_path}")
                return config_data
        except Exception as e:
            raise FileProcessingError(
                f"Error loading config file: {config_path}",
                file_path=str(config_path)
            ) from e

    def _apply_environment_overrides(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides"""
        env_mappings = {
            # Database
            "SENTRIX_DATABASE_URL": "database.url",
            "SENTRIX_DATABASE_MAX_CONNECTIONS": "database.max_connections",

            # YOLO Service
            "SENTRIX_YOLO_SERVICE_URL": "yolo_service.url",
            "SENTRIX_YOLO_MODEL_PATH": "yolo_service.model_path",
            "SENTRIX_YOLO_CONFIDENCE": "yolo_service.confidence_threshold",

            # Security
            "SENTRIX_JWT_SECRET": "security.jwt_secret_key",
            "SENTRIX_MAX_FILE_SIZE": "security.max_file_size_mb",

            # CORS
            "SENTRIX_ALLOWED_ORIGINS": "cors.allowed_origins",

            # Logging
            "SENTRIX_LOG_LEVEL": "logging.level",

            # General
            "SENTRIX_DEBUG": "debug",
            "SENTRIX_SERVICE_NAME": "service_name"
        }

        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                self._set_nested_value(config_data, config_path, env_value)

        return config_data

    def _set_nested_value(self, data: Dict[str, Any], path: str, value: str):
        """Set nested dictionary value from dot notation path"""
        keys = path.split('.')
        current = data

        # Navigate to parent
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set final value with type conversion
        final_key = keys[-1]
        current[final_key] = self._convert_env_value(value)

    def _convert_env_value(self, value: str) -> Union[str, int, float, bool, List[str]]:
        """Convert environment variable value to appropriate type"""
        # Boolean conversion
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'

        # List conversion (comma-separated)
        if ',' in value:
            return [item.strip() for item in value.split(',')]

        # Number conversion
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass

        # Return as string
        return value

    def _create_config_object(self, config_data: Dict[str, Any]) -> SentrixConfig:
        """Create SentrixConfig object from dictionary"""
        config = SentrixConfig()

        # Set basic attributes
        if "environment" in config_data:
            config.environment = Environment(config_data["environment"])
        if "debug" in config_data:
            config.debug = config_data["debug"]
        if "service_name" in config_data:
            config.service_name = config_data["service_name"]
        if "version" in config_data:
            config.version = config_data["version"]

        # Set nested configurations
        if "database" in config_data:
            config.database = DatabaseConfig(**config_data["database"])

        if "yolo_service" in config_data:
            config.yolo_service = YoloServiceConfig(**config_data["yolo_service"])

        if "cors" in config_data:
            config.cors = CorsConfig(**config_data["cors"])

        if "logging" in config_data:
            config.logging = LoggingConfig(**config_data["logging"])

        if "security" in config_data:
            config.security = SecurityConfig(**config_data["security"])

        # Store extra configuration
        excluded_keys = {"environment", "debug", "service_name", "version",
                        "database", "yolo_service", "cors", "logging", "security"}
        config.extra_config = {
            k: v for k, v in config_data.items()
            if k not in excluded_keys
        }

        return config

    def get_config(self) -> SentrixConfig:
        """Get current configuration"""
        if self._config is None:
            raise RuntimeError("Configuration not loaded. Call load_config() first.")
        return self._config

    def reload_config(self) -> SentrixConfig:
        """Reload configuration from files"""
        logger.info(f"Reloading configuration for {self.service_name}")
        return self.load_config()

    def save_config(self, config_file: Optional[str] = None):
        """Save current configuration to file"""
        if self._config is None:
            raise RuntimeError("No configuration to save")

        if not config_file:
            config_file = f"{self.service_name}.yaml"

        config_path = self.config_dir / config_file

        # Convert config to dictionary
        config_dict = self._config_to_dict(self._config)

        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Save to YAML
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            logger.info(f"Configuration saved to: {config_path}")
        except Exception as e:
            raise FileProcessingError(
                f"Error saving config file: {config_path}",
                file_path=str(config_path)
            ) from e

    def _config_to_dict(self, config: SentrixConfig) -> Dict[str, Any]:
        """Convert SentrixConfig to dictionary"""
        result = {
            "environment": config.environment.value,
            "debug": config.debug,
            "service_name": config.service_name,
            "version": config.version
        }

        if config.database:
            result["database"] = {
                "url": config.database.url,
                "max_connections": config.database.max_connections,
                "timeout_seconds": config.database.timeout_seconds,
                "retry_attempts": config.database.retry_attempts,
                "enable_logging": config.database.enable_logging
            }

        if config.yolo_service:
            result["yolo_service"] = {
                "url": config.yolo_service.url,
                "timeout_seconds": config.yolo_service.timeout_seconds,
                "max_retries": config.yolo_service.max_retries,
                "model_path": config.yolo_service.model_path,
                "confidence_threshold": config.yolo_service.confidence_threshold,
                "batch_size": config.yolo_service.batch_size
            }

        # Add other configurations
        result.update(config.extra_config)

        return result


# Global configuration managers
_config_managers: Dict[str, ConfigManager] = {}


def get_config_manager(service_name: str) -> ConfigManager:
    """Get or create config manager for service"""
    if service_name not in _config_managers:
        _config_managers[service_name] = ConfigManager(service_name)
    return _config_managers[service_name]


def load_service_config(service_name: str, config_file: Optional[str] = None) -> SentrixConfig:
    """Load configuration for a service"""
    manager = get_config_manager(service_name)
    return manager.load_config(config_file)


def get_service_config(service_name: str) -> SentrixConfig:
    """Get configuration for a service"""
    manager = get_config_manager(service_name)
    return manager.get_config()