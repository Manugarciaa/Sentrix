import enum
import sys
import os
from sqlalchemy import Enum

# Import shared data models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
from shared.data_models import (
    DetectionRiskEnum as SharedDetectionRiskEnum,
    BreedingSiteTypeEnum as SharedBreedingSiteTypeEnum,
    AnalysisStatusEnum as SharedAnalysisStatusEnum,
    ValidationStatusEnum as SharedValidationStatusEnum,
    UserRoleEnum as SharedUserRoleEnum
)


# Use shared enums but maintain backward compatibility
class RiskLevelEnum(enum.Enum):
    """Backward compatibility for RiskLevelEnum"""
    MINIMO = "MINIMO"  # Fixed spelling to match shared enum
    BAJO = "BAJO"
    MEDIO = "MEDIO"
    ALTO = "ALTO"


# Alias shared enums for direct use
DetectionRiskEnum = SharedDetectionRiskEnum
BreedingSiteTypeEnum = SharedBreedingSiteTypeEnum
AnalysisStatusEnum = SharedAnalysisStatusEnum
UserRoleEnum = SharedUserRoleEnum


class LocationSourceEnum(enum.Enum):
    EXIF_GPS = "EXIF_GPS"
    MANUAL = "MANUAL"
    ESTIMATED = "ESTIMATED"


# Keep local validation status for database compatibility
class ValidationStatusEnum(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    # Add shared enum values for compatibility
    PENDING_VALIDATION = "pending_validation"
    VALIDATED_POSITIVE = "validated_positive"
    VALIDATED_NEGATIVE = "validated_negative"
    REQUIRES_REVIEW = "requires_review"


# SQLAlchemy Enum types
risk_level_enum = Enum(RiskLevelEnum)
detection_risk_enum = Enum(DetectionRiskEnum)
breeding_site_type_enum = Enum(BreedingSiteTypeEnum)
user_role_enum = Enum(UserRoleEnum)
location_source_enum = Enum(LocationSourceEnum)
validation_status_enum = Enum(ValidationStatusEnum)