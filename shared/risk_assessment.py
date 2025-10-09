"""
Shared Risk Assessment Library for Sentrix
Librería compartida de evaluación de riesgo para Sentrix

Unifica la lógica de evaluación de riesgo entre backend y yolo-service
"""

from typing import List, Dict, Any, Optional
from enum import Enum


class RiskLevel(str, Enum):
    """Risk levels in Spanish (matching existing data)"""
    ALTO = "ALTO"
    MEDIO = "MEDIO"
    BAJO = "BAJO"
    MINIMO = "MINIMO"


class BreedingSiteType(str, Enum):
    """Breeding site types"""
    BASURA = "Basura"
    CALLES_MAL_HECHAS = "Calles mal hechas"
    CHARCOS_CUMULO_AGUA = "Charcos/Cumulo de agua"
    HUECOS = "Huecos"


# Risk classification mappings
HIGH_RISK_CLASSES = {
    BreedingSiteType.CHARCOS_CUMULO_AGUA,
    BreedingSiteType.BASURA
}

MEDIUM_RISK_CLASSES = {
    BreedingSiteType.HUECOS,
    BreedingSiteType.CALLES_MAL_HECHAS
}


def assess_dengue_risk(detections: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Unified risk assessment function for dengue breeding sites
    Función unificada de evaluación de riesgo para criaderos de dengue

    Args:
        detections: List of detection objects with 'class' or 'class_name' field

    Returns:
        Dict with comprehensive risk assessment
    """
    if not isinstance(detections, list):
        raise ValueError("Detections must be a list")

    # Count detections by risk category
    high_risk_count = 0
    medium_risk_count = 0

    for detection in detections:
        # Get class name from different possible fields
        class_name = detection.get('class') or detection.get('class_name') or detection.get('breeding_site_type')

        if not class_name:
            continue

        # Normalize class name
        if isinstance(class_name, str):
            class_name = class_name.strip()

        # Check risk level
        if class_name in HIGH_RISK_CLASSES or class_name in [cls.value for cls in HIGH_RISK_CLASSES]:
            high_risk_count += 1
        elif class_name in MEDIUM_RISK_CLASSES or class_name in [cls.value for cls in MEDIUM_RISK_CLASSES]:
            medium_risk_count += 1

    # Determine overall risk level using improved criteria
    total_detections = len(detections)

    if high_risk_count >= 3:
        risk_level = RiskLevel.ALTO
        risk_score = min(0.9 + (high_risk_count * 0.02), 1.0)
    elif high_risk_count >= 1 or medium_risk_count >= 3:
        risk_level = RiskLevel.MEDIO
        risk_score = 0.5 + (high_risk_count * 0.1) + (medium_risk_count * 0.05)
    elif medium_risk_count >= 1 or total_detections >= 5:
        risk_level = RiskLevel.BAJO
        risk_score = 0.2 + (medium_risk_count * 0.05) + (total_detections * 0.01)
    else:
        risk_level = RiskLevel.MINIMO
        risk_score = 0.05

    # Ensure score is within bounds
    risk_score = min(1.0, max(0.0, risk_score))

    # Generate recommendations
    recommendations = get_risk_recommendations(risk_level, high_risk_count, medium_risk_count, total_detections)

    return {
        # Primary fields
        'level': risk_level.value,
        'risk_score': risk_score,
        'total_detections': total_detections,
        'high_risk_count': high_risk_count,
        'medium_risk_count': medium_risk_count,
        'recommendations': recommendations,

        # Compatibility fields for different services
        'overall_risk': risk_level.value,  # yolo-service compatibility
        'high_risk_sites': high_risk_count,  # yolo-service compatibility
        'medium_risk_sites': medium_risk_count,  # yolo-service compatibility
    }


def get_risk_recommendations(
    risk_level: RiskLevel,
    high_risk_count: int,
    medium_risk_count: int,
    total_detections: int
) -> List[str]:
    """
    Generate contextual recommendations based on risk assessment
    Generar recomendaciones contextuales basadas en evaluación de riesgo
    """
    recommendations = []

    if risk_level == RiskLevel.ALTO:
        recommendations.extend([
            "[ALERT] Intervención inmediata requerida",
            "[WATER] Eliminar agua estancada inmediatamente",
            "[CONTACT] Contactar autoridades sanitarias locales",
            "[STOP] Evitar acumulación de desechos"
        ])
        if high_risk_count > 3:
            recommendations.append("[WARN] Múltiples focos detectados - considerar intervención a gran escala")

    elif risk_level == RiskLevel.MEDIO:
        recommendations.extend([
            "[MONITOR] Monitoreo regular necesario",
            "[CLEAN] Limpiar recipientes y contenedores",
            "[SCHEDULE] Programar inspección de seguimiento",
            "[TIP] Implementar medidas preventivas"
        ])
        if medium_risk_count > 2:
            recommendations.append("[REPORT] Considerar evaluación más detallada del área")

    elif risk_level == RiskLevel.BAJO:
        recommendations.extend([
            "[MAINTAIN] Mantenimiento preventivo",
            "[CLEAN] Limpieza regular del área",
            "[WATCH] Vigilancia periódica",
            "[INFO] Mantener prácticas de prevención"
        ])

    else:  # MINIMO
        recommendations.extend([
            "✓ Continuar vigilancia rutinaria",
            "[PROCESSING] Mantener prácticas preventivas actuales"
        ])

    # Add general recommendations based on detection count
    if total_detections > 10:
        recommendations.append("[METRICS] Alto número de detecciones - considerar intervención integral del área")
    elif total_detections > 5:
        recommendations.append("[REPORT] Múltiples puntos detectados - revisar drenaje y limpieza general")

    return recommendations


def normalize_risk_level(risk_level: str) -> Optional[RiskLevel]:
    """
    Normalize risk level from different formats
    Normalizar nivel de riesgo desde diferentes formatos
    """
    if not risk_level:
        return None

    risk_level = risk_level.upper().strip()

    # Direct mapping
    if risk_level in [level.value for level in RiskLevel]:
        return RiskLevel(risk_level)

    # English to Spanish mapping
    english_mapping = {
        "HIGH": RiskLevel.ALTO,
        "MEDIUM": RiskLevel.MEDIO,
        "LOW": RiskLevel.BAJO,
        "MINIMAL": RiskLevel.MINIMO
    }

    return english_mapping.get(risk_level)


def format_risk_assessment_for_frontend(assessment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format risk assessment for frontend consumption
    Formatear evaluación de riesgo para consumo del frontend
    """
    return {
        'riskLevel': assessment['level'],
        'riskScore': round(assessment['risk_score'], 3),
        'totalDetections': assessment['total_detections'],
        'highRiskCount': assessment['high_risk_count'],
        'mediumRiskCount': assessment['medium_risk_count'],
        'recommendations': assessment['recommendations'],
        'severity': {
            'ALTO': 'critical',
            'MEDIO': 'warning',
            'BAJO': 'info',
            'MINIMO': 'success'
        }.get(assessment['level'], 'info')
    }