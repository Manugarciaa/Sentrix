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

    IMPROVED LOGIC:
    - Considers diversity of breeding site types (not just count)
    - Multiple types in same area = CRITICAL (ecosystem problem)
    - Same type repeated = Less critical (isolated issue)

    Args:
        detections: List of detection objects with 'class' or 'class_name' field

    Returns:
        Dict with comprehensive risk assessment
    """
    if not isinstance(detections, list):
        raise ValueError("Detections must be a list")

    # Count detections by risk category AND track unique types
    high_risk_count = 0
    medium_risk_count = 0
    unique_types = set()
    type_counts = {}

    for detection in detections:
        # Get class name from different possible fields
        class_name = detection.get('class') or detection.get('class_name') or detection.get('breeding_site_type')

        if not class_name:
            continue

        # Normalize class name
        if isinstance(class_name, str):
            class_name = class_name.strip()

        # Track unique types and counts
        unique_types.add(class_name)
        type_counts[class_name] = type_counts.get(class_name, 0) + 1

        # Check risk level
        if class_name in HIGH_RISK_CLASSES or class_name in [cls.value for cls in HIGH_RISK_CLASSES]:
            high_risk_count += 1
        elif class_name in MEDIUM_RISK_CLASSES or class_name in [cls.value for cls in MEDIUM_RISK_CLASSES]:
            medium_risk_count += 1

    # Calculate diversity metrics
    total_detections = len(detections)
    unique_type_count = len(unique_types)
    diversity_ratio = unique_type_count / total_detections if total_detections > 0 else 0

    # IMPROVED RISK ASSESSMENT LOGIC
    # Key insight: Multiple different types = Systemic problem (more critical)
    #              Same type repeated = Localized issue (less critical)

    # Critical conditions (ALTO):
    # 1. Multiple different types detected (ecosystem problem)
    # 2. High-risk sites with diversity
    # 3. Large number of high-risk detections
    if unique_type_count >= 3 and total_detections >= 4:
        # Multiple different breeding site types = CRITICAL
        risk_level = RiskLevel.ALTO
        risk_score = min(0.85 + (unique_type_count * 0.05), 1.0)
    elif high_risk_count >= 3 and unique_type_count >= 2:
        # Multiple high-risk sites of different types
        risk_level = RiskLevel.ALTO
        risk_score = min(0.9 + (high_risk_count * 0.02), 1.0)
    elif high_risk_count >= 5:
        # Many high-risk sites (even if same type)
        risk_level = RiskLevel.ALTO
        risk_score = min(0.85 + (high_risk_count * 0.03), 1.0)

    # Medium risk conditions (MEDIO):
    # 1. Some diversity with moderate detections
    # 2. High-risk sites present
    # 3. Multiple medium-risk sites with diversity
    elif unique_type_count >= 2 and (high_risk_count >= 1 or medium_risk_count >= 2):
        # Diverse types with some risk
        risk_level = RiskLevel.MEDIO
        risk_score = 0.5 + (unique_type_count * 0.05) + (high_risk_count * 0.1)
    elif high_risk_count >= 1:
        # At least one high-risk site
        risk_level = RiskLevel.MEDIO
        risk_score = 0.5 + (high_risk_count * 0.1) + (medium_risk_count * 0.05)
    elif medium_risk_count >= 3 and unique_type_count >= 2:
        # Multiple medium-risk of different types
        risk_level = RiskLevel.MEDIO
        risk_score = 0.45 + (medium_risk_count * 0.05)

    # Low risk conditions (BAJO):
    # 1. Single type repeated (localized issue)
    # 2. Few detections without diversity
    elif medium_risk_count >= 1 or (total_detections >= 3 and unique_type_count == 1):
        # Some detections but low diversity (same thing repeated)
        risk_level = RiskLevel.BAJO
        risk_score = 0.25 + (total_detections * 0.02)

    # Minimal risk (MINIMO):
    # Very few detections or no significant patterns
    else:
        risk_level = RiskLevel.MINIMO
        risk_score = 0.05 + (total_detections * 0.01)

    # Ensure score is within bounds
    risk_score = min(1.0, max(0.0, risk_score))

    # Generate recommendations with diversity context
    recommendations = get_risk_recommendations(
        risk_level, high_risk_count, medium_risk_count, total_detections,
        unique_type_count, diversity_ratio
    )

    return {
        # Primary fields
        'level': risk_level.value,
        'risk_score': risk_score,
        'total_detections': total_detections,
        'high_risk_count': high_risk_count,
        'medium_risk_count': medium_risk_count,
        'unique_types': unique_type_count,
        'diversity_ratio': round(diversity_ratio, 2),
        'type_distribution': type_counts,
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
    total_detections: int,
    unique_type_count: int = 0,
    diversity_ratio: float = 0.0
) -> List[str]:
    """
    Generate contextual recommendations based on risk assessment
    Generar recomendaciones contextuales basadas en evaluación de riesgo

    Now includes diversity-based recommendations
    """
    recommendations = []

    if risk_level == RiskLevel.ALTO:
        recommendations.extend([
            "[ALERT] Intervención inmediata requerida",
            "[WATER] Eliminar agua estancada inmediatamente",
            "[CONTACT] Contactar autoridades sanitarias locales",
            "[STOP] Evitar acumulación de desechos"
        ])

        # Diversity-based recommendations
        if unique_type_count >= 3:
            recommendations.append("[CRITICAL] Múltiples tipos de criaderos detectados - problema sistémico del área")
        elif high_risk_count > 3:
            recommendations.append("[WARN] Múltiples focos detectados - considerar intervención a gran escala")

    elif risk_level == RiskLevel.MEDIO:
        recommendations.extend([
            "[MONITOR] Monitoreo regular necesario",
            "[CLEAN] Limpiar recipientes y contenedores",
            "[SCHEDULE] Programar inspección de seguimiento",
            "[TIP] Implementar medidas preventivas"
        ])

        # Diversity-based recommendations
        if unique_type_count >= 2:
            recommendations.append("[DIVERSITY] Diferentes tipos de criaderos detectados - revisar condiciones generales del área")
        elif medium_risk_count > 2:
            recommendations.append("[REPORT] Considerar evaluación más detallada del área")

    elif risk_level == RiskLevel.BAJO:
        recommendations.extend([
            "[MAINTAIN] Mantenimiento preventivo",
            "[CLEAN] Limpieza regular del área",
            "[WATCH] Vigilancia periódica",
            "[INFO] Mantener prácticas de prevención"
        ])

        # Single type detection pattern
        if unique_type_count == 1 and total_detections >= 3:
            recommendations.append("[PATTERN] Mismo tipo repetido - problema localizado, fácil de resolver")

    else:  # MINIMO
        recommendations.extend([
            "✓ Continuar vigilancia rutinaria",
            "[PROCESSING] Mantener prácticas preventivas actuales"
        ])

    # Add general recommendations based on detection count and diversity
    if total_detections > 10:
        recommendations.append("[METRICS] Alto número de detecciones - considerar intervención integral del área")
    elif total_detections > 5 and unique_type_count == 1:
        recommendations.append("[LOCALIZED] Múltiples detecciones del mismo tipo - revisar fuente específica")
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