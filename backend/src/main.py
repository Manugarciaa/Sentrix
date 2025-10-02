"""
DEPRECATED: This file is no longer used
USE: backend/app.py instead

This file is kept for backwards compatibility only.
All new code should import from backend/app.py
"""

import warnings
warnings.warn(
    "backend/src/main.py is deprecated. Use backend/app.py instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import the actual app for backwards compatibility
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app

__all__ = ['app']
