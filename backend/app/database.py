"""
Database module for FastAPI app
"""

from src.database.connection import get_db

# Re-export for compatibility
__all__ = ["get_db"]