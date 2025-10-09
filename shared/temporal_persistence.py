"""
Temporal Persistence Model for Detection Validity
Modelo de Persistencia Temporal para Validez de Detecciones

This module handles the temporal validity of breeding site detections,
taking into account that different types of sites have different lifespans.
"""

from enum import Enum
from typing import Dict, Optional
from datetime import datetime, timedelta
from .data_models import BreedingSiteTypeEnum, DetectionRiskEnum


class PersistenceTypeEnum(str, Enum):
    """
    Classification of breeding sites by temporal persistence
    Clasificación de criaderos por persistencia temporal
    """
    TRANSIENT = "TRANSIENT"           # Horas a días (charcos, agua temporal)
    SHORT_TERM = "SHORT_TERM"         # Días a semanas (basura temporal)
    MEDIUM_TERM = "MEDIUM_TERM"       # Semanas a meses (baches pequeños)
    LONG_TERM = "LONG_TERM"           # Meses a años (estructuras, baches grandes)
    PERMANENT = "PERMANENT"           # Permanente (cisternas, estructuras fijas)


class WeatherConditionEnum(str, Enum):
    """
    Weather conditions affecting validity
    Condiciones climáticas que afectan la validez
    """
    SUNNY = "SUNNY"           # Soleado - acelera secado
    RAINY = "RAINY"           # Lluvioso - extiende validez de agua
    CLOUDY = "CLOUDY"         # Nublado - validez normal
    DRY_SEASON = "DRY_SEASON" # Época seca - reduce validez de agua
    WET_SEASON = "WET_SEASON" # Época húmeda - extiende validez


# Persistence classification by breeding site type
BREEDING_SITE_PERSISTENCE: Dict[BreedingSiteTypeEnum, PersistenceTypeEnum] = {
    # Transient (hours to days) - dependen mucho del clima
    BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA: PersistenceTypeEnum.TRANSIENT,

    # Short-term (days to weeks) - pueden ser removidos rápidamente
    BreedingSiteTypeEnum.BASURA: PersistenceTypeEnum.SHORT_TERM,

    # Medium to Long-term (weeks to months/years) - requieren intervención estructural
    BreedingSiteTypeEnum.HUECOS: PersistenceTypeEnum.MEDIUM_TERM,
    BreedingSiteTypeEnum.CALLES_MAL_HECHAS: PersistenceTypeEnum.LONG_TERM,
}


# Default validity periods in days for each persistence type
DEFAULT_VALIDITY_DAYS: Dict[PersistenceTypeEnum, int] = {
    PersistenceTypeEnum.TRANSIENT: 2,      # 2 días (charcos pueden secarse rápido)
    PersistenceTypeEnum.SHORT_TERM: 7,     # 1 semana (basura puede ser recogida)
    PersistenceTypeEnum.MEDIUM_TERM: 30,   # 1 mes (baches pequeños)
    PersistenceTypeEnum.LONG_TERM: 180,    # 6 meses (calles rotas requieren obras)
    PersistenceTypeEnum.PERMANENT: 365,    # 1 año (estructuras permanentes)
}


# Weather multipliers for validity period
WEATHER_MULTIPLIERS: Dict[WeatherConditionEnum, float] = {
    WeatherConditionEnum.SUNNY: 0.5,      # Sol reduce validez de agua a la mitad
    WeatherConditionEnum.RAINY: 1.5,      # Lluvia extiende 50% la validez
    WeatherConditionEnum.CLOUDY: 1.0,     # Nublado = validez normal
    WeatherConditionEnum.DRY_SEASON: 0.6, # Época seca reduce validez
    WeatherConditionEnum.WET_SEASON: 1.8, # Época húmeda extiende mucho
}


# Risk-based validity adjustments
RISK_VALIDITY_MULTIPLIERS: Dict[DetectionRiskEnum, float] = {
    DetectionRiskEnum.ALTO: 1.2,    # Riesgo alto = más tiempo de validez (más crítico)
    DetectionRiskEnum.MEDIO: 1.0,   # Riesgo medio = validez normal
    DetectionRiskEnum.BAJO: 0.8,    # Riesgo bajo = menos tiempo de validez
    DetectionRiskEnum.MINIMO: 0.6,  # Riesgo mínimo = validez reducida
}


def get_persistence_type(breeding_site: BreedingSiteTypeEnum) -> PersistenceTypeEnum:
    """
    Get persistence type for a breeding site
    Obtener tipo de persistencia para un criadero
    """
    return BREEDING_SITE_PERSISTENCE.get(
        breeding_site,
        PersistenceTypeEnum.MEDIUM_TERM  # Default
    )


def calculate_validity_period(
    breeding_site: BreedingSiteTypeEnum,
    risk_level: DetectionRiskEnum,
    weather_condition: Optional[WeatherConditionEnum] = None,
    confidence: float = 0.8,
    is_validated: bool = False
) -> int:
    """
    Calculate validity period in days for a detection
    Calcular período de validez en días para una detección

    Args:
        breeding_site: Tipo de criadero
        risk_level: Nivel de riesgo
        weather_condition: Condición climática actual (opcional)
        confidence: Confianza de la detección (0-1)
        is_validated: Si fue validado por un experto

    Returns:
        Días de validez
    """
    # Get base persistence type
    persistence_type = get_persistence_type(breeding_site)
    base_days = DEFAULT_VALIDITY_DAYS[persistence_type]

    # Apply risk multiplier
    risk_multiplier = RISK_VALIDITY_MULTIPLIERS.get(risk_level, 1.0)
    validity_days = base_days * risk_multiplier

    # Apply weather multiplier only for weather-dependent types
    if weather_condition and persistence_type in [
        PersistenceTypeEnum.TRANSIENT,
        PersistenceTypeEnum.SHORT_TERM
    ]:
        weather_multiplier = WEATHER_MULTIPLIERS.get(weather_condition, 1.0)
        validity_days *= weather_multiplier

    # Confidence adjustment (lower confidence = shorter validity)
    if confidence < 0.7:
        validity_days *= 0.7
    elif confidence > 0.9:
        validity_days *= 1.1

    # Validated detections get extended validity
    if is_validated:
        validity_days *= 1.3

    # Minimum 1 day, maximum depends on type
    max_days = DEFAULT_VALIDITY_DAYS[PersistenceTypeEnum.PERMANENT]
    return max(1, min(int(validity_days), max_days))


def calculate_expiration_date(
    detection_date: datetime,
    breeding_site: BreedingSiteTypeEnum,
    risk_level: DetectionRiskEnum,
    weather_condition: Optional[WeatherConditionEnum] = None,
    confidence: float = 0.8,
    is_validated: bool = False
) -> datetime:
    """
    Calculate expiration datetime for a detection
    Calcular fecha de expiración para una detección

    Returns:
        Fecha y hora de expiración
    """
    validity_days = calculate_validity_period(
        breeding_site=breeding_site,
        risk_level=risk_level,
        weather_condition=weather_condition,
        confidence=confidence,
        is_validated=is_validated
    )

    return detection_date + timedelta(days=validity_days)


def is_detection_expired(
    expires_at: datetime,
    current_time: Optional[datetime] = None
) -> bool:
    """
    Check if a detection has expired
    Verificar si una detección ha expirado
    """
    if current_time is None:
        current_time = datetime.now()

    return current_time >= expires_at


def get_remaining_validity_days(
    expires_at: datetime,
    current_time: Optional[datetime] = None
) -> int:
    """
    Get remaining days of validity
    Obtener días restantes de validez

    Returns:
        Días restantes (0 si ya expiró)
    """
    if current_time is None:
        current_time = datetime.now()

    if is_detection_expired(expires_at, current_time):
        return 0

    delta = expires_at - current_time
    return max(0, delta.days)


def get_validity_status(
    expires_at: datetime,
    current_time: Optional[datetime] = None
) -> Dict[str, any]:
    """
    Get complete validity status for a detection
    Obtener estado completo de validez para una detección

    Returns:
        Dictionary with status information
    """
    if current_time is None:
        current_time = datetime.now()

    is_expired = is_detection_expired(expires_at, current_time)
    remaining_days = get_remaining_validity_days(expires_at, current_time)

    # Calculate percentage of validity remaining
    if is_expired:
        validity_percentage = 0
        status = "EXPIRED"
    elif remaining_days <= 1:
        validity_percentage = 10
        status = "EXPIRING_SOON"
    elif remaining_days <= 3:
        validity_percentage = 30
        status = "LOW_VALIDITY"
    elif remaining_days <= 7:
        validity_percentage = 60
        status = "MEDIUM_VALIDITY"
    else:
        validity_percentage = 100
        status = "VALID"

    return {
        "is_expired": is_expired,
        "is_expiring_soon": remaining_days <= 1 and not is_expired,
        "remaining_days": remaining_days,
        "expires_at": expires_at.isoformat(),
        "status": status,
        "validity_percentage": validity_percentage,
        "requires_revalidation": is_expired or remaining_days <= 1
    }


def should_send_expiration_alert(
    expires_at: datetime,
    last_alert_sent: Optional[datetime] = None,
    current_time: Optional[datetime] = None
) -> bool:
    """
    Determine if an expiration alert should be sent
    Determinar si debe enviarse una alerta de expiración

    Returns:
        True if alert should be sent
    """
    if current_time is None:
        current_time = datetime.now()

    remaining_days = get_remaining_validity_days(expires_at, current_time)

    # Don't send if already expired
    if remaining_days == 0:
        return False

    # Send alert 1 day before expiration
    should_alert = remaining_days == 1

    # Don't spam - only send once per detection
    if last_alert_sent is not None and should_alert:
        # Already sent alert within last 24 hours
        time_since_alert = current_time - last_alert_sent
        if time_since_alert < timedelta(hours=24):
            return False

    return should_alert


# Season detection for Argentina (Southern Hemisphere)
def get_current_season_weather(month: int) -> WeatherConditionEnum:
    """
    Estimate weather condition based on month for Argentina
    Estimar condición climática basada en el mes para Argentina

    Argentina seasons (Southern Hemisphere):
    - Summer (wet): December, January, February
    - Fall: March, April, May
    - Winter (dry): June, July, August
    - Spring: September, October, November
    """
    if month in [12, 1, 2]:  # Summer - wet season
        return WeatherConditionEnum.WET_SEASON
    elif month in [6, 7, 8]:  # Winter - dry season
        return WeatherConditionEnum.DRY_SEASON
    else:  # Fall and Spring - moderate
        return WeatherConditionEnum.CLOUDY


def get_detection_metadata(
    breeding_site: BreedingSiteTypeEnum,
    risk_level: DetectionRiskEnum
) -> Dict[str, any]:
    """
    Get complete metadata about persistence for a breeding site type
    Obtener metadata completa sobre persistencia para un tipo de criadero
    """
    persistence_type = get_persistence_type(breeding_site)
    base_validity = DEFAULT_VALIDITY_DAYS[persistence_type]

    return {
        "breeding_site": breeding_site.value,
        "risk_level": risk_level.value,
        "persistence_type": persistence_type.value,
        "base_validity_days": base_validity,
        "is_weather_dependent": persistence_type in [
            PersistenceTypeEnum.TRANSIENT,
            PersistenceTypeEnum.SHORT_TERM
        ],
        "typical_lifespan": _get_lifespan_description(persistence_type),
        "requires_frequent_monitoring": persistence_type == PersistenceTypeEnum.TRANSIENT,
        "requires_structural_intervention": persistence_type in [
            PersistenceTypeEnum.LONG_TERM,
            PersistenceTypeEnum.PERMANENT
        ]
    }


def _get_lifespan_description(persistence_type: PersistenceTypeEnum) -> str:
    """Get human-readable lifespan description"""
    descriptions = {
        PersistenceTypeEnum.TRANSIENT: "Horas a días",
        PersistenceTypeEnum.SHORT_TERM: "Días a semanas",
        PersistenceTypeEnum.MEDIUM_TERM: "Semanas a meses",
        PersistenceTypeEnum.LONG_TERM: "Meses a años",
        PersistenceTypeEnum.PERMANENT: "Permanente hasta intervención"
    }
    return descriptions.get(persistence_type, "Desconocido")
