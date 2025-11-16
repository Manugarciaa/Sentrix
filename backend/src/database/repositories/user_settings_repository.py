"""
User Settings Repository

Provides database operations for UserSettings model.
"""

from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from .base import BaseRepository, NotFoundError
from ..models.models import UserSettings


class UserSettingsRepository(BaseRepository[UserSettings]):
    """Repository for UserSettings operations"""

    def __init__(self, db: Session):
        super().__init__(UserSettings, db)

    # ============================================
    # Custom Query Methods
    # ============================================

    def get_by_user_id(self, user_id: UUID) -> Optional[UserSettings]:
        """
        Get settings for a user.

        Args:
            user_id: User's UUID

        Returns:
            UserSettings instance or None if not found
        """
        return self.get_by_field("user_id", user_id)

    def get_by_user_id_or_404(self, user_id: UUID) -> UserSettings:
        """
        Get settings for a user or raise NotFoundError.

        Args:
            user_id: User's UUID

        Returns:
            UserSettings instance

        Raises:
            NotFoundError: If settings not found
        """
        settings = self.get_by_user_id(user_id)
        if settings is None:
            raise NotFoundError(f"Settings for user {user_id} not found")
        return settings

    # ============================================
    # Settings-Specific Operations
    # ============================================

    def create_settings(
        self,
        user_id: UUID,
        settings: Optional[Dict[str, Any]] = None
    ) -> UserSettings:
        """
        Create settings for a user.

        Args:
            user_id: User's UUID
            settings: Optional initial settings dictionary

        Returns:
            Created UserSettings instance

        Raises:
            DuplicateError: If settings already exist for this user
        """
        return self.create(
            user_id=user_id,
            settings=settings or {}
        )

    def get_or_create_settings(
        self,
        user_id: UUID,
        default_settings: Optional[Dict[str, Any]] = None
    ) -> UserSettings:
        """
        Get existing settings or create default ones.

        Args:
            user_id: User's UUID
            default_settings: Optional default settings dictionary

        Returns:
            UserSettings instance (existing or newly created)
        """
        settings = self.get_by_user_id(user_id)
        if settings is None:
            settings = self.create_settings(user_id, default_settings)
        return settings

    def update_settings(
        self,
        user_id: UUID,
        settings: Dict[str, Any]
    ) -> UserSettings:
        """
        Replace all settings for a user.

        Args:
            user_id: User's UUID
            settings: New settings dictionary

        Returns:
            Updated UserSettings instance

        Raises:
            NotFoundError: If settings not found
        """
        settings_record = self.get_by_user_id_or_404(user_id)
        return self.update_or_404(settings_record.id, settings=settings)

    def merge_settings(
        self,
        user_id: UUID,
        partial_settings: Dict[str, Any]
    ) -> UserSettings:
        """
        Merge partial settings with existing settings.

        Args:
            user_id: User's UUID
            partial_settings: Settings to merge

        Returns:
            Updated UserSettings instance

        Raises:
            NotFoundError: If settings not found
        """
        settings_record = self.get_by_user_id_or_404(user_id)
        current_settings = settings_record.settings or {}

        # Merge settings (partial settings override current)
        merged_settings = {**current_settings, **partial_settings}

        return self.update_or_404(settings_record.id, settings=merged_settings)

    def get_setting(
        self,
        user_id: UUID,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Get a specific setting value.

        Args:
            user_id: User's UUID
            key: Setting key
            default: Default value if key not found

        Returns:
            Setting value or default

        Raises:
            NotFoundError: If settings not found
        """
        settings_record = self.get_by_user_id_or_404(user_id)
        settings = settings_record.settings or {}
        return settings.get(key, default)

    def set_setting(
        self,
        user_id: UUID,
        key: str,
        value: Any
    ) -> UserSettings:
        """
        Set a specific setting value.

        Args:
            user_id: User's UUID
            key: Setting key
            value: Setting value

        Returns:
            Updated UserSettings instance

        Raises:
            NotFoundError: If settings not found
        """
        return self.merge_settings(user_id, {key: value})

    def remove_setting(
        self,
        user_id: UUID,
        key: str
    ) -> UserSettings:
        """
        Remove a specific setting key.

        Args:
            user_id: User's UUID
            key: Setting key to remove

        Returns:
            Updated UserSettings instance

        Raises:
            NotFoundError: If settings not found
        """
        settings_record = self.get_by_user_id_or_404(user_id)
        settings = settings_record.settings or {}

        # Remove key if it exists
        if key in settings:
            del settings[key]
            return self.update_or_404(settings_record.id, settings=settings)

        return settings_record

    def clear_settings(self, user_id: UUID) -> UserSettings:
        """
        Clear all settings for a user (set to empty dict).

        Args:
            user_id: User's UUID

        Returns:
            Updated UserSettings instance

        Raises:
            NotFoundError: If settings not found
        """
        return self.update_settings(user_id, {})

    # ============================================
    # Bulk Operations
    # ============================================

    def set_settings_for_all_users(
        self,
        key: str,
        value: Any
    ) -> int:
        """
        Set a specific setting for all users.

        Args:
            key: Setting key
            value: Setting value

        Returns:
            Number of users updated
        """
        try:
            # Get all user settings
            all_settings = self.get_all(limit=10000)  # Adjust limit as needed

            updated_count = 0
            for settings_record in all_settings:
                current_settings = settings_record.settings or {}
                current_settings[key] = value
                self.update(settings_record.id, settings=current_settings)
                updated_count += 1

            self.commit()
            return updated_count
        except Exception as e:
            self.rollback()
            raise self.RepositoryError(f"Failed to set settings for all users: {e}")

    # ============================================
    # Common Settings Helpers
    # ============================================

    def get_notification_preferences(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get notification preferences for a user.

        Args:
            user_id: User's UUID

        Returns:
            Dictionary with notification preferences
        """
        return self.get_setting(user_id, "notifications", {
            "email_enabled": True,
            "push_enabled": True,
            "high_risk_alerts": True,
            "weekly_summary": True
        })

    def update_notification_preferences(
        self,
        user_id: UUID,
        preferences: Dict[str, Any]
    ) -> UserSettings:
        """
        Update notification preferences.

        Args:
            user_id: User's UUID
            preferences: Notification preferences

        Returns:
            Updated UserSettings instance
        """
        current_prefs = self.get_notification_preferences(user_id)
        merged_prefs = {**current_prefs, **preferences}
        return self.set_setting(user_id, "notifications", merged_prefs)

    def get_privacy_settings(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get privacy settings for a user.

        Args:
            user_id: User's UUID

        Returns:
            Dictionary with privacy settings
        """
        return self.get_setting(user_id, "privacy", {
            "share_analyses": False,
            "public_profile": False,
            "allow_analytics": True
        })

    def update_privacy_settings(
        self,
        user_id: UUID,
        settings: Dict[str, Any]
    ) -> UserSettings:
        """
        Update privacy settings.

        Args:
            user_id: User's UUID
            settings: Privacy settings

        Returns:
            Updated UserSettings instance
        """
        current_settings = self.get_privacy_settings(user_id)
        merged_settings = {**current_settings, **settings}
        return self.set_setting(user_id, "privacy", merged_settings)

    def get_ui_preferences(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get UI preferences for a user.

        Args:
            user_id: User's UUID

        Returns:
            Dictionary with UI preferences
        """
        return self.get_setting(user_id, "ui", {
            "theme": "light",
            "language": "en",
            "map_default_zoom": 12,
            "show_tutorial": True
        })

    def update_ui_preferences(
        self,
        user_id: UUID,
        preferences: Dict[str, Any]
    ) -> UserSettings:
        """
        Update UI preferences.

        Args:
            user_id: User's UUID
            preferences: UI preferences

        Returns:
            Updated UserSettings instance
        """
        current_prefs = self.get_ui_preferences(user_id)
        merged_prefs = {**current_prefs, **preferences}
        return self.set_setting(user_id, "ui", merged_prefs)
