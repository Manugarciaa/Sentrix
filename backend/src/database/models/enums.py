"""
Database enums using shared data models
Enums de base de datos usando modelos de datos compartidos
"""

import sys
import os
from sqlalchemy import Enum

# Import from shared library
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
from shared.data_models import (
    DetectionRiskEnum,
    BreedingSiteTypeEnum,
    AnalysisStatusEnum,
    ValidationStatusEnum,
    UserRoleEnum,
    LocationSourceEnum,
    RiskLevelEnum
)


# SQLAlchemy Enum types for database models
risk_level_enum = Enum(RiskLevelEnum)
detection_risk_enum = Enum(DetectionRiskEnum)
breeding_site_type_enum = Enum(BreedingSiteTypeEnum)
analysis_status_enum = Enum(AnalysisStatusEnum)
validation_status_enum = Enum(ValidationStatusEnum)
user_role_enum = Enum(UserRoleEnum)
location_source_enum = Enum(LocationSourceEnum)