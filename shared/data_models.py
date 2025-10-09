"""
Shared data models and enums for Sentrix project
Modelos de datos y enums compartidos para el proyecto Sentrix

Unified enums and classifications used by both backend and yolo-service
Enums y clasificaciones unificadas usadas por backend y yolo-service
"""

from enum import Enum
from typing import Dict, List


class DetectionRiskEnum(str, Enum):
    """Risk levels for detections in Spanish"""
    ALTO = "ALTO"
    MEDIO = "MEDIO"
    BAJO = "BAJO"
    MINIMO = "MINIMO"


class BreedingSiteTypeEnum(str, Enum):
    """Types of breeding sites for Aedes aegypti"""
    BASURA = "Basura"
    CALLES_MAL_HECHAS = "Calles mal hechas"
    CHARCOS_CUMULO_AGUA = "Charcos/Cumulo de agua"
    HUECOS = "Huecos"


class AnalysisStatusEnum(str, Enum):
    """Status of analysis processing"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_VALIDATION = "requires_validation"


class ValidationStatusEnum(str, Enum):
    """Status of expert validation"""
    PENDING = "pending"  # For backward compatibility
    PENDING_VALIDATION = "pending_validation"
    VALIDATED_POSITIVE = "validated_positive"
    VALIDATED_NEGATIVE = "validated_negative"
    REQUIRES_REVIEW = "requires_review"


class UserRoleEnum(str, Enum):
    """User roles for authentication and authorization"""
    USER = "USER"
    ADMIN = "ADMIN"
    EXPERT = "EXPERT"


# RiskLevelEnum removed - use DetectionRiskEnum instead for consistency
# Backward compatibility alias
RiskLevelEnum = DetectionRiskEnum


class LocationSourceEnum(str, Enum):
    """Source of location data"""
    EXIF_GPS = "EXIF_GPS"
    MANUAL = "MANUAL"
    ESTIMATED = "ESTIMATED"


# Class ID mappings for YOLO model compatibility
CLASS_ID_TO_BREEDING_SITE: Dict[int, BreedingSiteTypeEnum] = {
    0: BreedingSiteTypeEnum.BASURA,
    1: BreedingSiteTypeEnum.CALLES_MAL_HECHAS,
    2: BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA,
    3: BreedingSiteTypeEnum.HUECOS,
}

BREEDING_SITE_TO_CLASS_ID: Dict[BreedingSiteTypeEnum, int] = {
    v: k for k, v in CLASS_ID_TO_BREEDING_SITE.items()
}

# Risk level mappings for different service compatibility
YOLO_RISK_TO_DETECTION_RISK: Dict[str, DetectionRiskEnum] = {
    "ALTO": DetectionRiskEnum.ALTO,
    "MEDIO": DetectionRiskEnum.MEDIO,
    "BAJO": DetectionRiskEnum.BAJO,
    "MINIMO": DetectionRiskEnum.MINIMO,
    # English compatibility
    "HIGH": DetectionRiskEnum.ALTO,
    "MEDIUM": DetectionRiskEnum.MEDIO,
    "LOW": DetectionRiskEnum.BAJO,
    "MINIMAL": DetectionRiskEnum.MINIMO,
}

# Risk classifications by breeding site type
HIGH_RISK_CLASSES: List[BreedingSiteTypeEnum] = [
    BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA,
    BreedingSiteTypeEnum.BASURA
]

MEDIUM_RISK_CLASSES: List[BreedingSiteTypeEnum] = [
    BreedingSiteTypeEnum.HUECOS,
    BreedingSiteTypeEnum.CALLES_MAL_HECHAS
]

# YOLO class names (for model compatibility)
YOLO_CLASS_NAMES: List[str] = [
    "Basura",
    "Calles mal hechas",
    "Charcos/Cumulo de agua",
    "Huecos"
]

# Class name normalization mapping
CLASS_NAME_NORMALIZATIONS: Dict[str, BreedingSiteTypeEnum] = {
    # Standard names
    "Basura": BreedingSiteTypeEnum.BASURA,
    "Calles mal hechas": BreedingSiteTypeEnum.CALLES_MAL_HECHAS,
    "Charcos/Cumulo de agua": BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA,
    "Huecos": BreedingSiteTypeEnum.HUECOS,

    # Alternative spellings
    "Charcos/Cumulos de agua": BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA,
    "Charcos": BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA,
    "Cumulo de agua": BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA,
    "Trash": BreedingSiteTypeEnum.BASURA,
    "Garbage": BreedingSiteTypeEnum.BASURA,
    "Holes": BreedingSiteTypeEnum.HUECOS,
    "Bad streets": BreedingSiteTypeEnum.CALLES_MAL_HECHAS,
    "Poor roads": BreedingSiteTypeEnum.CALLES_MAL_HECHAS,
}


def normalize_breeding_site_type(class_name: str) -> BreedingSiteTypeEnum:
    """
    Normalize breeding site type from various input formats
    Normalizar tipo de criadero desde varios formatos de entrada
    """
    if not class_name:
        raise ValueError("Class name cannot be empty")

    # Direct enum value match
    try:
        return BreedingSiteTypeEnum(class_name)
    except ValueError:
        pass

    # Normalization mapping
    normalized = CLASS_NAME_NORMALIZATIONS.get(class_name.strip())
    if normalized:
        return normalized

    # If no match found, raise error with suggestions
    available_classes = list(CLASS_NAME_NORMALIZATIONS.keys())
    raise ValueError(f"Unknown class name '{class_name}'. Available: {available_classes}")


def get_risk_level_for_breeding_site(breeding_site: BreedingSiteTypeEnum) -> DetectionRiskEnum:
    """
    Get default risk level for a breeding site type
    Obtener nivel de riesgo por defecto para un tipo de criadero
    """
    if breeding_site in HIGH_RISK_CLASSES:
        return DetectionRiskEnum.ALTO
    elif breeding_site in MEDIUM_RISK_CLASSES:
        return DetectionRiskEnum.MEDIO
    else:
        return DetectionRiskEnum.BAJO


def breeding_site_to_class_id(breeding_site: BreedingSiteTypeEnum) -> int:
    """Convert breeding site type to YOLO class ID"""
    return BREEDING_SITE_TO_CLASS_ID.get(breeding_site, 0)


def class_id_to_breeding_site(class_id: int) -> BreedingSiteTypeEnum:
    """Convert YOLO class ID to breeding site type"""
    if class_id not in CLASS_ID_TO_BREEDING_SITE:
        raise ValueError(f"Unknown class ID: {class_id}")
    return CLASS_ID_TO_BREEDING_SITE[class_id]


def get_all_breeding_sites() -> List[Dict[str, any]]:
    """
    Get all breeding site types with metadata
    Obtener todos los tipos de criaderos con metadata
    """
    return [
        {
            "id": breeding_site_to_class_id(site),
            "name": site.value,
            "enum_value": site,
            "risk_level": get_risk_level_for_breeding_site(site).value,
            "is_high_risk": site in HIGH_RISK_CLASSES,
            "is_medium_risk": site in MEDIUM_RISK_CLASSES
        }
        for site in BreedingSiteTypeEnum
    ]