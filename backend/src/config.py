"""
Configuration for Sentrix Backend
Type-safe settings with Pydantic validation
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Literal
from pydantic import (
    Field,
    field_validator,
    model_validator,
    HttpUrl,
    PostgresDsn,
    ValidationError
)
from pydantic_settings import BaseSettings, SettingsConfigDict


def find_project_root() -> Path:
    """Find project root by looking for .env file"""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / ".env").exists() or (current / ".env.example").exists():
            return current
        current = current.parent
    # Default to parent of backend/
    return Path(__file__).resolve().parent.parent.parent


PROJECT_ROOT = find_project_root()
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """
    Application settings with Pydantic validation

    Features:
    - Type-safe configuration
    - Automatic environment variable parsing
    - Field validation with custom rules
    - Clear error messages
    - Centralized .env file in project root
    """

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables
        validate_default=True,
        protected_namespaces=()  # Allow fields starting with 'model_'
    )

    # ============================================
    # Environment
    # ============================================

    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment"
    )

    debug: bool = Field(
        default=True,
        description="Enable debug mode"
    )

    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    # ============================================
    # Server Configuration
    # ============================================

    backend_host: str = Field(
        default="0.0.0.0",
        description="Backend server host"
    )

    backend_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Backend server port"
    )

    reload_on_change: bool = Field(
        default=True,
        description="Auto-reload on code changes (development only)"
    )

    # ============================================
    # Security - CRITICAL
    # ============================================

    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        min_length=32,
        description="Secret key for session encryption"
    )

    jwt_secret_key: str = Field(
        default="dev-jwt-secret-key-change-in-production",
        min_length=32,
        description="JWT signing key"
    )

    # ============================================
    # Database
    # ============================================

    database_url: str = Field(
        default="sqlite:///./test.db",
        description="Database connection URL"
    )

    # Supabase (if used)
    supabase_url: Optional[str] = Field(
        default=None,
        description="Supabase project URL"
    )

    supabase_key: Optional[str] = Field(
        default=None,
        description="Supabase anon/public key"
    )

    supabase_service_role_key: Optional[str] = Field(
        default=None,
        description="Supabase service role key (admin access)"
    )

    supabase_storage_bucket: str = Field(
        default="sentrix-images",
        description="Supabase Storage bucket name for original images"
    )

    supabase_processed_bucket: str = Field(
        default="sentrix-processed",
        description="Supabase Storage bucket name for processed images"
    )

    # ============================================
    # External Services
    # ============================================

    yolo_service_url: str = Field(
        default="http://localhost:8001",
        description="YOLO object detection service URL"
    )

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for Celery and caching"
    )

    # ============================================
    # CORS
    # ============================================

    allowed_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002",
            "http://127.0.0.1:3000"
        ],
        description="CORS allowed origins"
    )

    # ============================================
    # File Upload
    # ============================================

    max_file_size: int = Field(
        default=50 * 1024 * 1024,  # 50MB
        ge=1024 * 1024,  # Minimum 1MB
        le=100 * 1024 * 1024,  # Maximum 100MB
        description="Maximum file upload size in bytes"
    )

    allowed_extensions: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".tiff", ".tif", ".heic"],
        description="Allowed file extensions for upload"
    )

    # ============================================
    # YOLO Service Configuration
    # ============================================

    yolo_timeout_seconds: float = Field(
        default=30.0,
        ge=5.0,
        le=300.0,
        description="Timeout for YOLO service requests in seconds"
    )

    yolo_confidence_threshold: float = Field(
        default=0.5,
        ge=0.1,
        le=1.0,
        description="Default confidence threshold for YOLO detections"
    )

    min_confidence_threshold: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Minimum allowed confidence threshold"
    )

    max_confidence_threshold: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Maximum allowed confidence threshold"
    )

    # ============================================
    # API Limits and Performance
    # ============================================

    heatmap_max_limit: int = Field(
        default=1000,
        ge=10,
        le=10000,
        description="Maximum number of points for heatmap data"
    )

    rate_limit_per_minute: int = Field(
        default=10,
        ge=1,
        le=1000,
        description="API rate limit requests per minute"
    )

    default_pagination_limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Default number of items per page for pagination"
    )

    batch_max_images: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of images allowed in batch processing"
    )

    batch_concurrent_limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of concurrent image processing tasks in batch"
    )

    # ============================================
    # Statistics and Metrics
    # ============================================

    model_accuracy_baseline: float = Field(
        default=87.3,
        ge=0.0,
        le=100.0,
        description="Baseline model accuracy percentage"
    )

    area_per_location_km2: float = Field(
        default=1.5,
        ge=0.1,
        le=100.0,
        description="Estimated area in km² per unique GPS location"
    )

    yolo_service_version: str = Field(
        default="2.0.0",
        description="YOLO service version identifier"
    )

    # ============================================
    # Heatmap Configuration
    # ============================================

    heatmap_intensity_high: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Base intensity for high-risk detections on heatmap"
    )

    heatmap_intensity_medium: float = Field(
        default=0.4,
        ge=0.0,
        le=1.0,
        description="Base intensity for medium-risk detections on heatmap"
    )

    heatmap_intensity_low: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Base intensity for low-risk detections on heatmap"
    )

    heatmap_intensity_default: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Default base intensity for unknown risk levels on heatmap"
    )

    heatmap_detection_bonus_high: float = Field(
        default=0.05,
        ge=0.0,
        le=0.5,
        description="Intensity bonus per detection for high/medium risk"
    )

    heatmap_detection_bonus_low: float = Field(
        default=0.03,
        ge=0.0,
        le=0.5,
        description="Intensity bonus per detection for low risk"
    )

    heatmap_max_bonus_high: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Maximum intensity bonus for high/medium risk"
    )

    heatmap_max_bonus_low: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Maximum intensity bonus for low risk"
    )

    # ============================================
    # Celery Configuration
    # ============================================

    celery_broker_url: Optional[str] = Field(
        default=None,
        description="Celery broker URL (defaults to redis_url)"
    )

    celery_result_backend: Optional[str] = Field(
        default=None,
        description="Celery result backend URL (defaults to redis_url)"
    )

    # ============================================
    # Validators
    # ============================================

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v):
        """Parse comma-separated origins from environment"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("allowed_extensions", mode="before")
    @classmethod
    def parse_extensions(cls, v):
        """Parse comma-separated extensions from environment"""
        if isinstance(v, str):
            extensions = [ext.strip() for ext in v.split(",") if ext.strip()]
            # Ensure extensions start with dot
            return [ext if ext.startswith(".") else f".{ext}" for ext in extensions]
        return v

    @field_validator("secret_key", "jwt_secret_key")
    @classmethod
    def validate_secrets(cls, v, info):
        """Validate that secrets are not default values"""
        field_name = info.field_name

        # Check for placeholder patterns
        placeholder_patterns = [
            "change-in-production",
            "your-secret",
            "dev-secret",
            "test-secret",
            "placeholder",
            "example",
            "changeme",
            "replace-this"
        ]

        if any(pattern in v.lower() for pattern in placeholder_patterns):
            # This is a development default
            return v

        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level is valid"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper

    @model_validator(mode="after")
    def validate_production_config(self):
        """Validate production-specific requirements"""
        if self.environment == "production":
            errors = []

            # Check SECRET_KEY
            if self._is_default_secret(self.secret_key):
                errors.append(
                    "SECRET_KEY contains default/placeholder text. "
                    "Generate a secure key with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                )

            # Check JWT_SECRET_KEY
            if self._is_default_secret(self.jwt_secret_key):
                errors.append(
                    "JWT_SECRET_KEY contains default/placeholder text. "
                    "Generate a secure key with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                )

            # Secrets should be different
            if self.secret_key == self.jwt_secret_key and not self._is_default_secret(self.secret_key):
                errors.append("SECRET_KEY and JWT_SECRET_KEY should be different")

            # Check database URL is not default
            if self.database_url == "sqlite:///./test.db":
                errors.append("DATABASE_URL must be configured for production (currently using test database)")

            # Debug should be off in production
            if self.debug:
                errors.append("DEBUG must be False in production environment")

            if errors:
                print("\n" + "=" * 80)
                print("FATAL: Production configuration validation failed")
                print("=" * 80)
                for error in errors:
                    print(f"  ERROR: {error}")
                print("\nProduction deployment blocked for security reasons.")
                print("Please fix the configuration errors above and redeploy.")
                print("=" * 80 + "\n")
                sys.exit(1)

            print("OK: Production configuration validated successfully")

        elif self.environment == "development":
            # Show warnings in development
            warnings = []

            if self._is_default_secret(self.secret_key):
                warnings.append("SECRET_KEY is using default value (OK for development)")

            if self._is_default_secret(self.jwt_secret_key):
                warnings.append("JWT_SECRET_KEY is using default value (OK for development)")

            if warnings:
                print("\nDevelopment mode warnings:")
                for warning in warnings:
                    print(f"  WARNING: {warning}")
                print()

        return self

    @staticmethod
    def _is_default_secret(value: str) -> bool:
        """Check if a value appears to be a default/placeholder secret"""
        if not value or len(value) < 32:
            return True

        placeholder_patterns = [
            "change-in-production",
            "your-secret",
            "dev-secret",
            "test-secret",
            "placeholder",
            "example",
            "changeme",
            "replace-this"
        ]

        value_lower = value.lower()
        return any(pattern in value_lower for pattern in placeholder_patterns)

    # ============================================
    # Computed Properties
    # ============================================

    @property
    def celery_broker(self) -> str:
        """Get Celery broker URL (defaults to Redis URL)"""
        return self.celery_broker_url or self.redis_url

    @property
    def celery_backend(self) -> str:
        """Get Celery result backend URL (defaults to Redis URL)"""
        return self.celery_result_backend or self.redis_url

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"


# ============================================
# Settings Singleton
# ============================================

_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get validated settings singleton

    Creates settings on first call and validates configuration.
    Exits with error code if validation fails in production.

    Returns:
        Settings: Validated application settings
    """
    global _settings

    if _settings is None:
        try:
            _settings = Settings()
        except ValidationError as e:
            print("\n" + "=" * 80)
            print("FATAL: Configuration validation failed")
            print("=" * 80)
            for error in e.errors():
                field = " -> ".join(str(loc) for loc in error["loc"])
                print(f"  ERROR: {field}: {error['msg']}")
            print("\nPlease fix the configuration errors above.")
            print("=" * 80 + "\n")
            sys.exit(1)
        except Exception as e:
            print(f"\nFATAL: Error loading configuration: {e}\n")
            sys.exit(1)

    return _settings


def reset_settings():
    """Reset settings singleton (useful for testing)"""
    global _settings
    _settings = None


__all__ = ["Settings", "get_settings", "reset_settings"]
