"""
Database models for Sentrix Backend
Modelos de base de datos para Sentrix Backend
"""

from .base import Base
from .models import UserProfile, Analysis, Detection
from .enums import *

# Export main classes
__all__ = [
    "Base",
    "UserProfile",
    "Analysis",
    "Detection"
]

# Alias for compatibility
User = UserProfile