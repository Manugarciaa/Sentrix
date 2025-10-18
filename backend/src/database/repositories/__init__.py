"""
Database Repositories

Provides clean abstraction over database operations using the Repository Pattern.
"""

from .base import (
    BaseRepository,
    RepositoryError,
    NotFoundError,
    DuplicateError
)
from .user_repository import UserRepository
from .analysis_repository import AnalysisRepository
from .detection_repository import DetectionRepository
from .user_settings_repository import UserSettingsRepository


__all__ = [
    # Base
    "BaseRepository",
    "RepositoryError",
    "NotFoundError",
    "DuplicateError",
    # Repositories
    "UserRepository",
    "AnalysisRepository",
    "DetectionRepository",
    "UserSettingsRepository",
]
