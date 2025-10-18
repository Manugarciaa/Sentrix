"""
Tests for Pydantic Settings Configuration

Comprehensive test coverage for:
- Field validation
- Type checking
- Production validation rules
- Environment variable parsing
- Computed properties
- Error messages
- Singleton behavior
"""

import os
import sys
import pytest
from typing import Dict
from unittest.mock import patch
from pydantic import ValidationError

from src.config import Settings, get_settings, reset_settings


class TestBasicConfiguration:
    """Test basic configuration loading and defaults"""

    def test_default_settings_load(self):
        """Test that settings load with default values"""
        settings = Settings()

        assert settings.environment == "development"
        assert settings.debug is True
        assert settings.log_level == "INFO"
        assert settings.backend_host == "0.0.0.0"
        assert settings.backend_port == 8000

    def test_development_environment_default(self):
        """Test development is the default environment"""
        settings = Settings()

        assert settings.environment == "development"
        assert settings.is_development is True
        assert settings.is_production is False

    def test_settings_from_env_vars(self):
        """Test loading settings from environment variables"""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "staging",
            "DEBUG": "false",
            "LOG_LEVEL": "WARNING",
            "BACKEND_PORT": "9000"
        }):
            reset_settings()
            settings = Settings()

            assert settings.environment == "staging"
            assert settings.debug is False
            assert settings.log_level == "WARNING"
            assert settings.backend_port == 9000


class TestFieldValidation:
    """Test Pydantic field validation"""

    def test_port_validation_valid_range(self):
        """Test port number must be between 1 and 65535"""
        # Valid ports
        settings = Settings(backend_port=8000)
        assert settings.backend_port == 8000

        settings = Settings(backend_port=1)
        assert settings.backend_port == 1

        settings = Settings(backend_port=65535)
        assert settings.backend_port == 65535

    def test_port_validation_invalid_range(self):
        """Test port validation fails for out-of-range values"""
        with pytest.raises(ValidationError) as exc_info:
            Settings(backend_port=0)

        assert "greater than or equal to 1" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            Settings(backend_port=70000)

        assert "less than or equal to 65535" in str(exc_info.value)

    def test_secret_key_min_length(self):
        """Test secret keys must be at least 32 characters"""
        # Valid length
        settings = Settings(secret_key="a" * 32)
        assert len(settings.secret_key) == 32

        # Too short
        with pytest.raises(ValidationError) as exc_info:
            Settings(secret_key="too-short")

        assert "at least 32 characters" in str(exc_info.value)

    def test_jwt_secret_key_min_length(self):
        """Test JWT secret keys must be at least 32 characters"""
        # Valid length
        settings = Settings(jwt_secret_key="b" * 32)
        assert len(settings.jwt_secret_key) == 32

        # Too short
        with pytest.raises(ValidationError) as exc_info:
            Settings(jwt_secret_key="short")

        assert "at least 32 characters" in str(exc_info.value)

    def test_environment_literal_validation(self):
        """Test environment must be one of allowed values"""
        # Valid values
        Settings(environment="development")
        Settings(environment="staging")

        # Production requires valid config, so test separately
        Settings(
            environment="production",
            secret_key="a" * 32,
            jwt_secret_key="b" * 32,
            database_url="postgresql://user:pass@host/db",
            debug=False
        )

        # Invalid value
        with pytest.raises(ValidationError) as exc_info:
            Settings(environment="invalid")

        error_str = str(exc_info.value)
        assert "development" in error_str or "staging" in error_str or "production" in error_str

    def test_max_file_size_validation(self):
        """Test file size limits"""
        # Valid: within range (1MB to 100MB)
        settings = Settings(max_file_size=50 * 1024 * 1024)
        assert settings.max_file_size == 50 * 1024 * 1024

        # Too small (less than 1MB)
        with pytest.raises(ValidationError) as exc_info:
            Settings(max_file_size=512 * 1024)  # 512KB

        # Too large (more than 100MB)
        with pytest.raises(ValidationError) as exc_info:
            Settings(max_file_size=150 * 1024 * 1024)


class TestEnvironmentParsing:
    """Test parsing of comma-separated environment variables"""

    def test_parse_allowed_origins_from_string(self):
        """Test parsing comma-separated origins"""
        settings = Settings(
            allowed_origins="http://localhost:3000,http://localhost:3001,http://example.com"
        )

        assert len(settings.allowed_origins) == 3
        assert "http://localhost:3000" in settings.allowed_origins
        assert "http://localhost:3001" in settings.allowed_origins
        assert "http://example.com" in settings.allowed_origins

    def test_parse_allowed_origins_strips_whitespace(self):
        """Test that origin parsing strips whitespace"""
        settings = Settings(
            allowed_origins=" http://localhost:3000 , http://localhost:3001 "
        )

        assert settings.allowed_origins == [
            "http://localhost:3000",
            "http://localhost:3001"
        ]

    def test_parse_allowed_extensions_from_string(self):
        """Test parsing comma-separated file extensions"""
        settings = Settings(
            allowed_extensions=".jpg,.png,.tiff"
        )

        assert len(settings.allowed_extensions) == 3
        assert ".jpg" in settings.allowed_extensions
        assert ".png" in settings.allowed_extensions
        assert ".tiff" in settings.allowed_extensions

    def test_parse_extensions_adds_dot_prefix(self):
        """Test that extension parsing adds dot if missing"""
        settings = Settings(
            allowed_extensions="jpg,png,.tiff"
        )

        # Should normalize all to have dots
        assert ".jpg" in settings.allowed_extensions
        assert ".png" in settings.allowed_extensions
        assert ".tiff" in settings.allowed_extensions

    def test_parse_extensions_strips_whitespace(self):
        """Test that extension parsing strips whitespace"""
        settings = Settings(
            allowed_extensions=" .jpg , .png , .tiff "
        )

        assert settings.allowed_extensions == [".jpg", ".png", ".tiff"]


class TestLogLevelValidation:
    """Test log level validation"""

    def test_valid_log_levels(self):
        """Test all valid log levels are accepted"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in valid_levels:
            settings = Settings(log_level=level)
            assert settings.log_level == level

    def test_log_level_case_insensitive(self):
        """Test log level is case insensitive"""
        settings = Settings(log_level="info")
        assert settings.log_level == "INFO"

        settings = Settings(log_level="WaRnInG")
        assert settings.log_level == "WARNING"

    def test_invalid_log_level(self):
        """Test invalid log level raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            Settings(log_level="INVALID")

        assert "log_level must be one of" in str(exc_info.value)


class TestProductionValidation:
    """Test production-specific validation rules"""

    def test_production_validation_blocks_default_secrets(self, capsys):
        """Test production mode blocks default secret keys"""
        with pytest.raises(SystemExit) as exc_info:
            Settings(
                environment="production",
                secret_key="dev-secret-key-change-in-production",
                jwt_secret_key="dev-jwt-secret-key-change-in-production"
            )

        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "SECRET_KEY contains default/placeholder text" in captured.out
        assert "JWT_SECRET_KEY contains default/placeholder text" in captured.out

    def test_production_validation_blocks_test_database(self, capsys):
        """Test production mode blocks test database"""
        with pytest.raises(SystemExit) as exc_info:
            Settings(
                environment="production",
                secret_key="a" * 32,
                jwt_secret_key="b" * 32,
                database_url="sqlite:///./test.db"
            )

        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "DATABASE_URL must be configured for production" in captured.out

    def test_production_validation_requires_debug_false(self, capsys):
        """Test production mode requires debug=False"""
        with pytest.raises(SystemExit) as exc_info:
            Settings(
                environment="production",
                secret_key="a" * 32,
                jwt_secret_key="b" * 32,
                database_url="postgresql://user:pass@host/db",
                debug=True  # Invalid in production
            )

        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "DEBUG must be False in production" in captured.out

    def test_production_validation_requires_different_secrets(self, capsys):
        """Test production mode requires different secret keys"""
        same_secret = "a" * 32

        with pytest.raises(SystemExit) as exc_info:
            Settings(
                environment="production",
                secret_key=same_secret,
                jwt_secret_key=same_secret,  # Same as secret_key
                database_url="postgresql://user:pass@host/db",
                debug=False
            )

        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "SECRET_KEY and JWT_SECRET_KEY should be different" in captured.out

    def test_production_validation_passes_with_valid_config(self, capsys):
        """Test production validation passes with valid configuration"""
        settings = Settings(
            environment="production",
            secret_key="a" * 32,
            jwt_secret_key="b" * 32,
            database_url="postgresql://user:pass@host/db",
            debug=False
        )

        assert settings.environment == "production"

        captured = capsys.readouterr()
        assert "Production configuration validated successfully" in captured.out

    def test_development_mode_shows_warnings(self, capsys):
        """Test development mode shows warnings for default secrets"""
        settings = Settings(
            environment="development",
            secret_key="dev-secret-key-change-in-production",
            jwt_secret_key="dev-jwt-secret-key-change-in-production"
        )

        assert settings.environment == "development"

        captured = capsys.readouterr()
        assert "Development mode warnings:" in captured.out
        assert "SECRET_KEY is using default value" in captured.out
        assert "JWT_SECRET_KEY is using default value" in captured.out


class TestSecretDetection:
    """Test _is_default_secret() helper method"""

    def test_detects_default_secrets(self):
        """Test detection of default/placeholder secrets"""
        # These should be detected as default secrets
        default_patterns = [
            "dev-secret-key-change-in-production",
            "your-secret-key-here-please-change",
            "test-secret-for-development-only",
            "placeholder-secret-replace-this",
            "example-secret-key-not-for-production",
            "changeme-this-is-not-secure",
            "replace-this-secret-immediately"
        ]

        for secret in default_patterns:
            # Pad to minimum length if needed
            if len(secret) < 32:
                secret = secret + "x" * (32 - len(secret))

            assert Settings._is_default_secret(secret) is True

    def test_accepts_real_secrets(self):
        """Test that real secrets are not flagged as default"""
        # These should NOT be detected as default secrets
        real_secrets = [
            "a" * 32,
            "B7j9KpL2mN4qR6tV8wX0yZ3aC5eF7hI9",
            "randomly-generated-secure-key-12345678901234567890",
            "real-secure-secret-without-bad-patterns-123"
        ]

        for secret in real_secrets:
            assert Settings._is_default_secret(secret) is False

    def test_rejects_short_secrets(self):
        """Test that secrets shorter than 32 chars are flagged"""
        assert Settings._is_default_secret("short") is True
        assert Settings._is_default_secret("a" * 31) is True
        assert Settings._is_default_secret("a" * 32) is False


class TestComputedProperties:
    """Test computed properties"""

    def test_celery_broker_defaults_to_redis_url(self):
        """Test celery_broker defaults to redis_url"""
        settings = Settings(redis_url="redis://custom:6379/0")

        assert settings.celery_broker == "redis://custom:6379/0"

    def test_celery_broker_uses_custom_if_set(self):
        """Test celery_broker uses custom value if provided"""
        settings = Settings(
            redis_url="redis://default:6379/0",
            celery_broker_url="redis://custom-broker:6379/1"
        )

        assert settings.celery_broker == "redis://custom-broker:6379/1"

    def test_celery_backend_defaults_to_redis_url(self):
        """Test celery_backend defaults to redis_url"""
        settings = Settings(redis_url="redis://custom:6379/0")

        assert settings.celery_backend == "redis://custom:6379/0"

    def test_celery_backend_uses_custom_if_set(self):
        """Test celery_backend uses custom value if provided"""
        settings = Settings(
            redis_url="redis://default:6379/0",
            celery_result_backend="redis://custom-backend:6379/2"
        )

        assert settings.celery_backend == "redis://custom-backend:6379/2"

    def test_is_production_property(self):
        """Test is_production computed property"""
        settings = Settings(environment="production", debug=False, secret_key="a"*32, jwt_secret_key="b"*32, database_url="postgresql://...")
        assert settings.is_production is True

        settings = Settings(environment="development")
        assert settings.is_production is False

    def test_is_development_property(self):
        """Test is_development computed property"""
        settings = Settings(environment="development")
        assert settings.is_development is True

        # Note: production would fail validation, so test with staging
        settings = Settings(environment="staging")
        assert settings.is_development is False


class TestSettingsSingleton:
    """Test settings singleton pattern"""

    def test_get_settings_returns_singleton(self):
        """Test get_settings returns the same instance"""
        reset_settings()

        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    def test_reset_settings_clears_singleton(self):
        """Test reset_settings clears the singleton"""
        reset_settings()

        settings1 = get_settings()
        reset_settings()
        settings2 = get_settings()

        assert settings1 is not settings2

    def test_singleton_validation_error_exits(self, capsys):
        """Test validation errors in get_settings() cause exit"""
        reset_settings()

        with patch.dict(os.environ, {"BACKEND_PORT": "invalid"}):
            with pytest.raises(SystemExit) as exc_info:
                get_settings()

            assert exc_info.value.code == 1

            captured = capsys.readouterr()
            assert "Configuration validation failed" in captured.out


class TestConfigurationExamples:
    """Test real-world configuration examples"""

    def test_typical_development_config(self):
        """Test a typical development configuration"""
        settings = Settings(
            environment="development",
            debug=True,
            log_level="DEBUG",
            backend_port=8000,
            database_url="sqlite:///./test.db",
            redis_url="redis://localhost:6379/0"
        )

        assert settings.environment == "development"
        assert settings.debug is True
        assert settings.is_development is True

    def test_typical_production_config(self):
        """Test a typical production configuration"""
        settings = Settings(
            environment="production",
            debug=False,
            log_level="WARNING",
            backend_port=8000,
            secret_key="prod-secret-key-32-chars-long-abc123",
            jwt_secret_key="prod-jwt-key-32-chars-long-xyz789!",
            database_url="postgresql://user:pass@prod-db:5432/sentrix",
            redis_url="redis://prod-redis:6379/0",
            allowed_origins="https://app.sentrix.com,https://www.sentrix.com"
        )

        assert settings.environment == "production"
        assert settings.debug is False
        assert settings.is_production is True
        assert len(settings.allowed_origins) == 2

    def test_supabase_integration_config(self):
        """Test configuration with Supabase"""
        settings = Settings(
            database_url="postgresql://postgres:pass@db.supabase.co:5432/postgres",
            supabase_url="https://abc123.supabase.co",
            supabase_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            supabase_service_role_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        )

        assert settings.supabase_url is not None
        assert settings.supabase_key is not None
        assert settings.supabase_service_role_key is not None


class TestErrorMessages:
    """Test that error messages are clear and helpful"""

    def test_port_error_message_is_clear(self):
        """Test port validation error message"""
        with pytest.raises(ValidationError) as exc_info:
            Settings(backend_port=100000)

        error_msg = str(exc_info.value)
        assert "backend_port" in error_msg.lower()

    def test_secret_length_error_message(self):
        """Test secret key length error message"""
        with pytest.raises(ValidationError) as exc_info:
            Settings(secret_key="short")

        error_msg = str(exc_info.value)
        assert "secret_key" in error_msg.lower()
        assert "32" in error_msg

    def test_production_error_messages_are_detailed(self, capsys):
        """Test production validation shows detailed errors"""
        with pytest.raises(SystemExit):
            Settings(
                environment="production",
                secret_key="dev-secret-key-change-in-production",
                jwt_secret_key="dev-jwt-secret-key-change-in-production",
                database_url="sqlite:///./test.db",
                debug=True
            )

        captured = capsys.readouterr()
        output = captured.out

        # Should list all errors
        assert "SECRET_KEY contains default" in output
        assert "JWT_SECRET_KEY contains default" in output
        assert "DATABASE_URL must be configured" in output
        assert "DEBUG must be False" in output

        # Should provide actionable guidance
        assert "python -c 'import secrets" in output or "Generate a secure key" in output


# Test execution
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
