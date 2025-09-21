"""
YOLO Dengue Detection Classes Configuration
Now uses shared data models for consistency across services
Ahora usa modelos de datos compartidos para consistencia entre servicios
"""

import sys
import os
# Import shared data models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.data_models import (
    CLASS_ID_TO_BREEDING_SITE,
    BREEDING_SITE_TO_CLASS_ID,
    HIGH_RISK_CLASSES,
    MEDIUM_RISK_CLASSES,
    get_risk_level_for_breeding_site,
    YOLO_CLASS_NAMES
)

# Use shared mappings for consistency
DENGUE_CLASSES = {k: v.value for k, v in CLASS_ID_TO_BREEDING_SITE.items()}
CLASS_TO_ID = BREEDING_SITE_TO_CLASS_ID

# Convert shared enums to string lists for backward compatibility
HIGH_RISK_CLASSES = [site.value for site in HIGH_RISK_CLASSES]
MEDIUM_RISK_CLASSES = [site.value for site in MEDIUM_RISK_CLASSES]

# Generate risk level mappings using shared logic
RISK_LEVEL_BY_ID = {}
for class_id, breeding_site_enum in CLASS_ID_TO_BREEDING_SITE.items():
    risk_level = get_risk_level_for_breeding_site(breeding_site_enum)
    RISK_LEVEL_BY_ID[class_id] = risk_level.value

NUM_CLASSES = len(DENGUE_CLASSES)

# Additional exports for compatibility
YOLO_CLASS_NAMES = YOLO_CLASS_NAMES