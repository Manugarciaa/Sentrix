"""
Temporal Validity Utilities for Detection Management
Utilidades de Validez Temporal para Gestión de Detecciones

Integrates the shared temporal persistence model with backend detection creation.
Integra el modelo de persistencia temporal compartido con la creación de detecciones en backend.
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Add shared to path
shared_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

try:
    from shared.temporal_persistence import (
        calculate_validity_period,
        calculate_expiration_date,
        get_persistence_type,
        get_current_season_weather,
        get_validity_status,
        PersistenceTypeEnum,
        WeatherConditionEnum
    )
    from shared.data_models import BreedingSiteTypeEnum, DetectionRiskEnum
    TEMPORAL_PERSISTENCE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Temporal persistence not available: {e}")
    TEMPORAL_PERSISTENCE_AVAILABLE = False


def calculate_detection_validity(
    breeding_site_type: str,
    risk_level: str,
    confidence: float,
    is_validated: bool = False,
    detection_date: Optional[datetime] = None,
    weather_condition: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculate validity fields for a detection
    Calcular campos de validez para una detección

    Args:
        breeding_site_type: Type of breeding site (e.g., "CHARCOS_CUMULO_AGUA")
        risk_level: Risk level (e.g., "ALTO", "MEDIO", "BAJO")
        confidence: Detection confidence (0-1)
        is_validated: Whether detection was validated by expert
        detection_date: Date of detection (defaults to now)
        weather_condition: Current weather condition (optional, auto-detected from season)

    Returns:
        Dictionary with validity fields to add to detection record
    """
    if not TEMPORAL_PERSISTENCE_AVAILABLE:
        # Fallback: return simple defaults
        return {
            "validity_period_days": 30,
            "expires_at": None,
            "is_weather_dependent": False,
            "persistence_type": "MEDIUM_TERM",
            "last_expiration_alert_sent": None
        }

    try:
        # Convert string enums to actual enum values
        try:
            breeding_site_enum = BreedingSiteTypeEnum[breeding_site_type]
        except (KeyError, ValueError):
            # Unknown breeding site type, use default
            breeding_site_enum = BreedingSiteTypeEnum.HUECOS  # Default to medium-term

        # Map Spanish/English risk levels to DetectionRiskEnum
        risk_mapping = {
            "ALTO": DetectionRiskEnum.ALTO,
            "alto": DetectionRiskEnum.ALTO,
            "high": DetectionRiskEnum.ALTO,
            "MEDIO": DetectionRiskEnum.MEDIO,
            "medio": DetectionRiskEnum.MEDIO,
            "medium": DetectionRiskEnum.MEDIO,
            "BAJO": DetectionRiskEnum.BAJO,
            "bajo": DetectionRiskEnum.BAJO,
            "low": DetectionRiskEnum.BAJO,
            "MÍNIMO": DetectionRiskEnum.MINIMO,
            "minimo": DetectionRiskEnum.MINIMO,
            "minimal": DetectionRiskEnum.MINIMO,
        }
        risk_enum = risk_mapping.get(risk_level, DetectionRiskEnum.MEDIO)

        # Use provided detection date or current time
        if detection_date is None:
            detection_date = datetime.now()

        # Auto-detect weather condition from season if not provided
        weather_enum = None
        if weather_condition:
            try:
                weather_enum = WeatherConditionEnum[weather_condition]
            except (KeyError, ValueError):
                pass  # Invalid weather, will be None

        # If no weather provided, estimate from current month (Argentina seasons)
        if weather_enum is None:
            weather_enum = get_current_season_weather(detection_date.month)

        # Get persistence type
        persistence_type = get_persistence_type(breeding_site_enum)

        # Calculate validity period in days
        validity_days = calculate_validity_period(
            breeding_site=breeding_site_enum,
            risk_level=risk_enum,
            weather_condition=weather_enum,
            confidence=confidence,
            is_validated=is_validated
        )

        # Calculate expiration date
        expires_at = calculate_expiration_date(
            detection_date=detection_date,
            breeding_site=breeding_site_enum,
            risk_level=risk_enum,
            weather_condition=weather_enum,
            confidence=confidence,
            is_validated=is_validated
        )

        # Determine if weather dependent
        is_weather_dependent = persistence_type in [
            PersistenceTypeEnum.TRANSIENT,
            PersistenceTypeEnum.SHORT_TERM
        ]

        return {
            "validity_period_days": validity_days,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "is_weather_dependent": is_weather_dependent,
            "persistence_type": persistence_type.value,
            "last_expiration_alert_sent": None  # Will be set when alert is sent
        }

    except Exception as e:
        print(f"Error calculating detection validity: {e}")
        # Return safe defaults on error
        return {
            "validity_period_days": 30,
            "expires_at": None,
            "is_weather_dependent": False,
            "persistence_type": "MEDIUM_TERM",
            "last_expiration_alert_sent": None
        }


def enrich_detection_with_validity(
    detection_data: Dict[str, Any],
    is_validated: bool = False,
    weather_condition: Optional[str] = None
) -> Dict[str, Any]:
    """
    Enrich detection data dictionary with validity fields
    Enriquecer diccionario de datos de detección con campos de validez

    Args:
        detection_data: Detection data dictionary
        is_validated: Whether detection was validated
        weather_condition: Current weather (optional)

    Returns:
        Detection data with validity fields added
    """
    # Extract required fields from detection data
    breeding_site_type = detection_data.get("breeding_site_type", "HUECOS")
    risk_level = detection_data.get("risk_level", "MEDIO")
    confidence = float(detection_data.get("confidence", 0.8))

    # Parse created_at if available
    detection_date = None
    if "created_at" in detection_data:
        try:
            if isinstance(detection_data["created_at"], str):
                detection_date = datetime.fromisoformat(detection_data["created_at"].replace('Z', '+00:00'))
            elif isinstance(detection_data["created_at"], datetime):
                detection_date = detection_data["created_at"]
        except (ValueError, AttributeError):
            pass  # Use default (now)

    # Calculate validity fields
    validity_fields = calculate_detection_validity(
        breeding_site_type=breeding_site_type,
        risk_level=risk_level,
        confidence=confidence,
        is_validated=is_validated,
        detection_date=detection_date,
        weather_condition=weather_condition
    )

    # Merge validity fields into detection data
    enriched_data = detection_data.copy()
    enriched_data.update(validity_fields)

    return enriched_data


def get_detection_validity_status(expires_at: str) -> Dict[str, Any]:
    """
    Get current validity status for a detection
    Obtener estado actual de validez para una detección

    Args:
        expires_at: ISO format expiration datetime string

    Returns:
        Dictionary with validity status information
    """
    if not TEMPORAL_PERSISTENCE_AVAILABLE or not expires_at:
        return {
            "is_expired": False,
            "is_expiring_soon": False,
            "remaining_days": None,
            "status": "VALID",
            "validity_percentage": 100,
            "requires_revalidation": False
        }

    try:
        expires_datetime = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        return get_validity_status(expires_datetime)
    except (ValueError, AttributeError) as e:
        print(f"Error parsing expiration date: {e}")
        return {
            "is_expired": False,
            "is_expiring_soon": False,
            "remaining_days": None,
            "status": "UNKNOWN",
            "validity_percentage": 100,
            "requires_revalidation": False
        }


def should_revalidate_detection(
    expires_at: Optional[str],
    last_validation_date: Optional[str] = None
) -> bool:
    """
    Determine if a detection should be revalidated
    Determinar si una detección debe ser revalidada

    Args:
        expires_at: ISO format expiration datetime string
        last_validation_date: ISO format last validation date (optional)

    Returns:
        True if detection needs revalidation
    """
    if not expires_at:
        return False  # No expiration set, no revalidation needed

    validity_status = get_detection_validity_status(expires_at)
    return validity_status.get("requires_revalidation", False)


def extend_detection_validity(
    current_expires_at: str,
    extension_days: int,
    reason: str = "manual_extension"
) -> Dict[str, Any]:
    """
    Extend validity period for a detection
    Extender período de validez para una detección

    Args:
        current_expires_at: Current expiration date (ISO format)
        extension_days: Number of days to extend
        reason: Reason for extension

    Returns:
        Dictionary with new validity fields
    """
    try:
        from datetime import timedelta

        current_expiration = datetime.fromisoformat(current_expires_at.replace('Z', '+00:00'))
        new_expiration = current_expiration + timedelta(days=extension_days)

        return {
            "expires_at": new_expiration.isoformat(),
            "validity_extended": True,
            "extension_days": extension_days,
            "extension_reason": reason,
            "extended_at": datetime.now().isoformat()
        }

    except (ValueError, AttributeError) as e:
        print(f"Error extending validity: {e}")
        return {
            "error": str(e)
        }
