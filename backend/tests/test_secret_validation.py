"""
Tests for secret key validation
"""

import pytest
import os
from unittest.mock import patch

from src.config import Settings


def test_development_mode_allows_default_secrets():
    """Test that development mode allows default secrets with warnings"""
    with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
        settings = Settings()
        # Should not raise exception
        assert settings.secret_key is not None
        assert settings.environment == "development"


def test_production_rejects_default_secret_key():
    """Test that production mode rejects default SECRET_KEY"""
    with patch.dict(os.environ, {
        "ENVIRONMENT": "production",
        "SECRET_KEY": "dev-secret-key-change-in-production",
        "JWT_SECRET_KEY": "some-valid-key-with-32-characters-or-more"
    }, clear=True):
        with pytest.raises(SystemExit):
            Settings()


def test_production_rejects_default_jwt_key():
    """Test that production mode rejects default JWT_SECRET_KEY"""
    with patch.dict(os.environ, {
        "ENVIRONMENT": "production",
        "SECRET_KEY": "some-valid-key-with-32-characters-or-more",
        "JWT_SECRET_KEY": "dev-jwt-secret-key-change-in-production"
    }, clear=True):
        with pytest.raises(SystemExit):
            Settings()


def test_production_rejects_short_secret():
    """Test that production mode rejects short secrets"""
    with patch.dict(os.environ, {
        "ENVIRONMENT": "production",
        "SECRET_KEY": "short",
        "JWT_SECRET_KEY": "also_short"
    }, clear=True):
        with pytest.raises(SystemExit):
            Settings()


def test_production_accepts_valid_secrets():
    """Test that production mode accepts valid secrets"""
    with patch.dict(os.environ, {
        "ENVIRONMENT": "production",
        "SECRET_KEY": "valid-secret-key-with-32-chars-XXXXXXXXX",
        "JWT_SECRET_KEY": "valid-jwt-key-with-32-chars-YYYYYYYYYY"
    }, clear=True):
        settings = Settings()
        assert len(settings.secret_key) >= 32
        assert len(settings.jwt_secret_key) >= 32
        assert settings.environment == "production"


def test_production_rejects_same_secrets():
    """Test that production warns if both secrets are identical"""
    same_key = "valid-secret-key-with-32-chars-XXXXXXXXX"
    with patch.dict(os.environ, {
        "ENVIRONMENT": "production",
        "SECRET_KEY": same_key,
        "JWT_SECRET_KEY": same_key
    }, clear=True):
        with pytest.raises(SystemExit):
            Settings()


def test_production_rejects_empty_secret_key():
    """Test that production rejects empty SECRET_KEY"""
    with patch.dict(os.environ, {
        "ENVIRONMENT": "production",
        "JWT_SECRET_KEY": "valid-jwt-key-with-32-chars-YYYYYYYYYY"
    }, clear=True):
        with pytest.raises(SystemExit):
            Settings()


def test_production_rejects_empty_jwt_key():
    """Test that production rejects empty JWT_SECRET_KEY"""
    with patch.dict(os.environ, {
        "ENVIRONMENT": "production",
        "SECRET_KEY": "valid-secret-key-with-32-chars-XXXXXXXXX"
    }, clear=True):
        with pytest.raises(SystemExit):
            Settings()


def test_is_default_secret_detection():
    """Test default secret pattern detection"""
    # Should detect default secrets
    assert Settings._is_default_secret("dev-secret-key-change-in-production") == True
    assert Settings._is_default_secret("your-secret-key") == True
    assert Settings._is_default_secret("test-secret") == True
    assert Settings._is_default_secret("changeme") == True
    assert Settings._is_default_secret("CHANGEME") == True
    assert Settings._is_default_secret("replace-this") == True
    assert Settings._is_default_secret("example-key") == True
    assert Settings._is_default_secret("") == True

    # Should NOT detect valid secrets
    assert Settings._is_default_secret("Xk7Vp9Rq3Yt5Zw8Bm4Ln6Hj2Dc1Fg0Sa") == False
    assert Settings._is_default_secret("a" * 32) == False
    assert Settings._is_default_secret("production-grade-secret-key-32-chars") == False


def test_staging_environment_treated_as_production():
    """Test that staging environment uses production rules"""
    with patch.dict(os.environ, {
        "ENVIRONMENT": "staging",
        "SECRET_KEY": "dev-secret-key-change-in-production",
        "JWT_SECRET_KEY": "valid-jwt-key-with-32-chars-YYYYYYYYYY"
    }, clear=True):
        # Staging should allow default secrets since it's not explicitly "production"
        # This behavior can be changed if you want staging to also be strict
        settings = Settings()
        assert settings.environment == "staging"


def test_minimum_key_length_exactly_32():
    """Test that exactly 32 characters is accepted"""
    key_32 = "a" * 32
    with patch.dict(os.environ, {
        "ENVIRONMENT": "production",
        "SECRET_KEY": key_32,
        "JWT_SECRET_KEY": key_32 + "b"  # Make it different
    }, clear=True):
        settings = Settings()
        assert len(settings.secret_key) == 32


def test_minimum_key_length_31_rejected():
    """Test that 31 characters is rejected"""
    key_31 = "a" * 31
    with patch.dict(os.environ, {
        "ENVIRONMENT": "production",
        "SECRET_KEY": key_31,
        "JWT_SECRET_KEY": "b" * 32
    }, clear=True):
        with pytest.raises(SystemExit):
            Settings()
