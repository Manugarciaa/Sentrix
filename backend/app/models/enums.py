"""
Enums for app models - compatibility layer
"""

from src.database.models.enums import (
    RiskLevelEnum,
    DetectionRiskEnum,
    BreedingSiteTypeEnum,
    UserRoleEnum,
    LocationSourceEnum,
    ValidationStatusEnum,
    risk_level_enum,
    detection_risk_enum,
    breeding_site_type_enum,
    user_role_enum,
    location_source_enum,
    validation_status_enum
)

# Re-export all enums for compatibility
__all__ = [
    "RiskLevelEnum",
    "DetectionRiskEnum",
    "BreedingSiteTypeEnum",
    "UserRoleEnum",
    "LocationSourceEnum",
    "ValidationStatusEnum",
    "risk_level_enum",
    "detection_risk_enum",
    "breeding_site_type_enum",
    "user_role_enum",
    "location_source_enum",
    "validation_status_enum"
]