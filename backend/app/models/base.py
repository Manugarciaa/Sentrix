"""
Base model for SQLAlchemy
"""

from src.database.models.models import Base

# Re-export for compatibility
__all__ = ["Base"]