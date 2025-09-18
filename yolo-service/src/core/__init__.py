"""
Core functionality for YOLO Dengue Detection
Funcionalidades principales para detección de criaderos de dengue
"""

from .trainer import train_dengue_model
from .detector import detect_breeding_sites
from .evaluator import assess_dengue_risk

__all__ = [
    'train_dengue_model',
    'detect_breeding_sites',
    'assess_dengue_risk'
]