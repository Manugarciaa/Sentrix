"""
Configuration and secrets validation for Sentrix Backend
Validación de configuración y secrets para Sentrix Backend
"""

import os
import sys
from typing import List, Dict, Optional
from dataclasses import dataclass


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
            if not database_url.startswith(("postgresql://", "postgres://")):
                errors.append("DATABASE_URL must start with postgresql:// or postgres://")

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
        """Print colored validation report to console"""

        print("\n" + "=" * 60)
        print("🔍 CONFIGURATION VALIDATION REPORT")
        print("=" * 60)

        if result.is_valid:
            print("✅ Configuration is VALID")
        else:
            print("❌ Configuration is INVALID")

        if result.errors:
            print(f"\n❌ ERRORS ({len(result.errors)}):")
            for error in result.errors:
                print(f"   - {error}")

        if result.warnings:
            print(f"\n⚠️  WARNINGS ({len(result.warnings)}):")
            for warning in result.warnings:
                print(f"   - {warning}")

        if result.missing_required:
            print(f"\n📋 MISSING REQUIRED ({len(result.missing_required)}):")
            for var in result.missing_required:
                print(f"   - {var}")

        if result.weak_secrets:
            print(f"\n🔓 WEAK SECRETS ({len(result.weak_secrets)}):")
            for var in result.weak_secrets:
                print(f"   - {var}")
            print("\n💡 Generate strong secrets with:")
            print("   openssl rand -hex 32")

        print("\n" + "=" * 60 + "\n")

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
            print("❌ Cannot start application with invalid configuration")
            print("   Please fix the errors above and try again\n")
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
