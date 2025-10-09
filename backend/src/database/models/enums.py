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
# Use values_callable to ensure we use .value instead of .name
risk_level_enum = Enum(RiskLevelEnum, values_callable=lambda x: [e.value for e in x])
detection_risk_enum = Enum(DetectionRiskEnum, values_callable=lambda x: [e.value for e in x])
breeding_site_type_enum = Enum(BreedingSiteTypeEnum, values_callable=lambda x: [e.value for e in x])
analysis_status_enum = Enum(AnalysisStatusEnum, values_callable=lambda x: [e.value for e in x])
validation_status_enum = Enum(ValidationStatusEnum, values_callable=lambda x: [e.value for e in x])
user_role_enum = Enum(UserRoleEnum, values_callable=lambda x: [e.value for e in x])
location_source_enum = Enum(LocationSourceEnum, values_callable=lambda x: [e.value for e in x])