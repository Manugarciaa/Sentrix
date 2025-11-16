"""
Configuration and secrets validation for Sentrix Backend
Validación de configuración y secrets para Sentrix Backend
"""

import os
import sys
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of configuration validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    missing_required: List[str]
    weak_secrets: List[str]


class ConfigValidator:
    """Validates environment configuration and secrets"""

    # Required environment variables
    REQUIRED_VARS = [
        "DATABASE_URL",
        "SECRET_KEY",
        "JWT_SECRET_KEY",
    ]

    # Recommended environment variables
    RECOMMENDED_VARS = [
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "YOLO_SERVICE_URL",
        "ALLOWED_ORIGINS",
    ]

    # Weak/default secrets that should not be used in production
    WEAK_SECRETS = [
        "your-secret-key-change-in-production",
        "your-jwt-secret-key-change-in-production",
        "development-secret-key",
        "docker-dev-secret-key-change-in-production",
        "docker-jwt-secret-key-change-in-production",
        "change-me",
        "changeme",
        "secret",
        "password",
        "123456",
    ]

    # Minimum secret length
    MIN_SECRET_LENGTH = 32

    @classmethod
    def validate_environment(cls, strict: bool = False) -> ValidationResult:
        """
        Validate environment configuration

        Args:
            strict: If True, warnings become errors

        Returns:
            ValidationResult with validation details
        """
        errors = []
        warnings = []
        missing_required = []
        weak_secrets = []

        environment = os.getenv("ENVIRONMENT", "development")

        # Check required variables
        for var in cls.REQUIRED_VARS:
            value = os.getenv(var)
            if not value:
                missing_required.append(var)
                errors.append(f"Required environment variable missing: {var}")

        # Check recommended variables (only warnings)
        for var in cls.RECOMMENDED_VARS:
            value = os.getenv(var)
            if not value:
                warnings.append(f"Recommended environment variable missing: {var}")

        # Validate secrets strength (only in production)
        if environment == "production":
            secret_key = os.getenv("SECRET_KEY", "")
            jwt_secret_key = os.getenv("JWT_SECRET_KEY", "")

            # Check for weak secrets
            for secret_var, secret_value in [("SECRET_KEY", secret_key), ("JWT_SECRET_KEY", jwt_secret_key)]:
                if secret_value:
                    # Check if it's a known weak secret
                    if secret_value.lower() in [s.lower() for s in cls.WEAK_SECRETS]:
                        weak_secrets.append(secret_var)
                        errors.append(f"{secret_var} is using a weak/default value")

                    # Check minimum length
                    if len(secret_value) < cls.MIN_SECRET_LENGTH:
                        weak_secrets.append(secret_var)
                        errors.append(
                            f"{secret_var} is too short (min {cls.MIN_SECRET_LENGTH} chars, got {len(secret_value)})"
                        )

        # Check DATABASE_URL format
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            # In production, require PostgreSQL
            if environment == "production":
                if not database_url.startswith(("postgresql://", "postgres://")):
                    errors.append("DATABASE_URL must start with postgresql:// or postgres:// in production")
            # In development, allow SQLite or PostgreSQL
            elif not database_url.startswith(("sqlite://", "postgresql://", "postgres://")):
                warnings.append(f"DATABASE_URL format may be invalid: {database_url.split('://')[0]}://")

        # Check YOLO_SERVICE_URL format
        yolo_url = os.getenv("YOLO_SERVICE_URL")
        if yolo_url:
            if not yolo_url.startswith(("http://", "https://")):
                errors.append("YOLO_SERVICE_URL must start with http:// or https://")

        # Check ALLOWED_ORIGINS in production
        if environment == "production":
            allowed_origins = os.getenv("ALLOWED_ORIGINS", "")
            if "*" in allowed_origins:
                errors.append("ALLOWED_ORIGINS should not contain '*' in production")

        # Convert warnings to errors if strict mode
        if strict:
            errors.extend(warnings)
            warnings = []

        is_valid = len(errors) == 0 and len(missing_required) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            missing_required=missing_required,
            weak_secrets=weak_secrets
        )

    @classmethod
    def print_validation_report(cls, result: ValidationResult) -> None:
        """Log validation report using logging"""

        logger.info("=" * 60)
        logger.info("CONFIGURATION VALIDATION REPORT")
        logger.info("=" * 60)

        if result.is_valid:
            logger.info("Configuration is VALID")
        else:
            logger.error("Configuration is INVALID")

        if result.errors:
            logger.error(f"ERRORS ({len(result.errors)}):")
            for error in result.errors:
                logger.error(f"   - {error}")

        if result.warnings:
            logger.warning(f"WARNINGS ({len(result.warnings)}):")
            for warning in result.warnings:
                logger.warning(f"   - {warning}")

        if result.missing_required:
            logger.error(f"MISSING REQUIRED ({len(result.missing_required)}):")
            for var in result.missing_required:
                logger.error(f"   - {var}")

        if result.weak_secrets:
            logger.error(f"WEAK SECRETS ({len(result.weak_secrets)}):")
            for var in result.weak_secrets:
                logger.error(f"   - {var}")
            logger.info("Generate strong secrets with: openssl rand -hex 32")

        logger.info("=" * 60)

    @classmethod
    def validate_or_exit(cls, strict: bool = False) -> None:
        """
        Validate configuration and exit if invalid

        Args:
            strict: If True, warnings become errors
        """
        result = cls.validate_environment(strict=strict)
        cls.print_validation_report(result)

        if not result.is_valid:
            logger.critical("Cannot start application with invalid configuration")
            logger.critical("Please fix the errors above and try again")
            sys.exit(1)


def validate_config() -> ValidationResult:
    """
    Convenience function to validate configuration

    Returns:
        ValidationResult
    """
    return ConfigValidator.validate_environment()


def check_production_ready() -> bool:
    """
    Check if configuration is production-ready

    Returns:
        True if production-ready, False otherwise
    """
    result = ConfigValidator.validate_environment(strict=True)
    return result.is_valid


if __name__ == "__main__":
    # Run validation when executed directly
    import argparse

    parser = argparse.ArgumentParser(description="Validate Sentrix configuration")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--exit-on-error", action="store_true", help="Exit with code 1 if invalid")

    args = parser.parse_args()

    if args.exit_on_error:
        ConfigValidator.validate_or_exit(strict=args.strict)
    else:
        result = ConfigValidator.validate_environment(strict=args.strict)
        ConfigValidator.print_validation_report(result)
        if not result.is_valid:
            sys.exit(1)
