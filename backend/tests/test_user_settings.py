"""
Unit tests for user settings functionality
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.models.base import Base
from src.database.models.models import UserProfile, UserSettings
from src.api.v1.auth import router
from src.database.connection import get_db
from src.utils.auth import get_password_hash
from src.schemas.settings import DEFAULT_USER_SETTINGS

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture
def test_db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(test_db):
    """Create a test user"""
    db = TestingSessionLocal()
    user = UserProfile(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        role="USER",
        display_name="Test User",
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.close()


class TestUserSettings:
    """Test user settings CRUD operations"""

    def test_create_user_settings(self, test_db, test_user):
        """Test creating user settings"""
        db = TestingSessionLocal()

        # Create settings
        settings = UserSettings(
            user_id=test_user.id,
            settings=DEFAULT_USER_SETTINGS
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

        # Verify
        assert settings.id is not None
        assert settings.user_id == test_user.id
        assert settings.settings == DEFAULT_USER_SETTINGS
        assert settings.created_at is not None
        assert settings.updated_at is not None

        db.close()

    def test_get_user_settings(self, test_db, test_user):
        """Test retrieving user settings"""
        db = TestingSessionLocal()

        # Create settings
        settings = UserSettings(
            user_id=test_user.id,
            settings={"language": "es", "timezone": "America/Argentina/Buenos_Aires"}
        )
        db.add(settings)
        db.commit()

        # Retrieve
        retrieved = db.query(UserSettings).filter(
            UserSettings.user_id == test_user.id
        ).first()

        assert retrieved is not None
        assert retrieved.settings["language"] == "es"
        assert retrieved.settings["timezone"] == "America/Argentina/Buenos_Aires"

        db.close()

    def test_update_user_settings(self, test_db, test_user):
        """Test updating user settings"""
        db = TestingSessionLocal()

        # Create settings
        settings = UserSettings(
            user_id=test_user.id,
            settings=DEFAULT_USER_SETTINGS.copy()
        )
        db.add(settings)
        db.commit()

        # Update
        settings.settings["language"] = "en"
        settings.settings["email_notifications"] = False
        db.commit()
        db.refresh(settings)

        # Verify
        assert settings.settings["language"] == "en"
        assert settings.settings["email_notifications"] is False
        assert settings.updated_at is not None

        db.close()

    def test_settings_cascade_delete(self, test_db, test_user):
        """Test that settings are deleted when user is deleted"""
        db = TestingSessionLocal()

        # Create settings
        settings = UserSettings(
            user_id=test_user.id,
            settings=DEFAULT_USER_SETTINGS
        )
        db.add(settings)
        db.commit()

        # Delete user
        db.delete(test_user)
        db.commit()

        # Verify settings are also deleted
        remaining_settings = db.query(UserSettings).filter(
            UserSettings.user_id == test_user.id
        ).first()

        assert remaining_settings is None

        db.close()

    def test_unique_user_constraint(self, test_db, test_user):
        """Test that one user can only have one settings record"""
        db = TestingSessionLocal()

        # Create first settings
        settings1 = UserSettings(
            user_id=test_user.id,
            settings=DEFAULT_USER_SETTINGS
        )
        db.add(settings1)
        db.commit()

        # Try to create duplicate - should fail
        settings2 = UserSettings(
            user_id=test_user.id,
            settings={"language": "en"}
        )
        db.add(settings2)

        with pytest.raises(Exception):  # IntegrityError
            db.commit()

        db.close()

    def test_settings_jsonb_merge(self, test_db, test_user):
        """Test merging settings with defaults"""
        db = TestingSessionLocal()

        # Create partial settings
        partial_settings = {"language": "pt", "timezone": "America/Sao_Paulo"}
        settings = UserSettings(
            user_id=test_user.id,
            settings=partial_settings
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

        # Merge with defaults
        merged = {**DEFAULT_USER_SETTINGS, **settings.settings}

        # Verify all default keys exist
        assert "language" in merged
        assert "email_notifications" in merged
        assert "default_confidence_threshold" in merged

        # Verify custom values override defaults
        assert merged["language"] == "pt"
        assert merged["timezone"] == "America/Sao_Paulo"

        db.close()


class TestSettingsValidation:
    """Test settings validation"""

    def test_valid_language(self):
        """Test valid language values"""
        from src.schemas.settings import UserSettingsBase

        valid_settings = UserSettingsBase(language="es")
        assert valid_settings.language == "es"

        valid_settings = UserSettingsBase(language="en")
        assert valid_settings.language == "en"

        valid_settings = UserSettingsBase(language="pt")
        assert valid_settings.language == "pt"

    def test_invalid_language(self):
        """Test invalid language value"""
        from src.schemas.settings import UserSettingsBase

        with pytest.raises(ValueError):
            UserSettingsBase(language="invalid")

    def test_valid_date_format(self):
        """Test valid date format values"""
        from src.schemas.settings import UserSettingsBase

        for fmt in ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"]:
            valid_settings = UserSettingsBase(date_format=fmt)
            assert valid_settings.date_format == fmt

    def test_confidence_threshold_range(self):
        """Test confidence threshold validation"""
        from src.schemas.settings import UserSettingsBase

        # Valid values
        UserSettingsBase(default_confidence_threshold=0.5)
        UserSettingsBase(default_confidence_threshold=0.7)
        UserSettingsBase(default_confidence_threshold=0.95)

        # Invalid values
        with pytest.raises(ValueError):
            UserSettingsBase(default_confidence_threshold=0.3)

        with pytest.raises(ValueError):
            UserSettingsBase(default_confidence_threshold=1.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
