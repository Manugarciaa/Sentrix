import enum
from sqlalchemy import Enum


class RiskLevelEnum(enum.Enum):
    MINIMAL = "MINIMAL"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class DetectionRiskEnum(enum.Enum):
    BAJO = "BAJO"
    MEDIO = "MEDIO"
    ALTO = "ALTO"


class BreedingSiteTypeEnum(enum.Enum):
    BASURA = "Basura"
    CALLES_MAL_HECHAS = "Calles mal hechas"
    CHARCOS_CUMULO_AGUA = "Charcos/Cumulo de agua"
    HUECOS = "Huecos"


class UserRoleEnum(enum.Enum):
    ADMIN = "admin"
    EXPERT = "expert"
    USER = "user"


class LocationSourceEnum(enum.Enum):
    EXIF_GPS = "EXIF_GPS"
    MANUAL = "MANUAL"
    ESTIMATED = "ESTIMATED"


class ValidationStatusEnum(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


# SQLAlchemy Enum types
risk_level_enum = Enum(RiskLevelEnum)
detection_risk_enum = Enum(DetectionRiskEnum)
breeding_site_type_enum = Enum(BreedingSiteTypeEnum)
user_role_enum = Enum(UserRoleEnum)
location_source_enum = Enum(LocationSourceEnum)
validation_status_enum = Enum(ValidationStatusEnum)