"""
Risk evaluation module for YOLO Dengue Detection
Módulo de evaluación de riesgo para detección de criaderos de dengue
"""

from configs.classes import HIGH_RISK_CLASSES, MEDIUM_RISK_CLASSES


def assess_dengue_risk(detections):
    """Evalúa riesgo epidemiológico basado en detecciones"""
    if not isinstance(detections, list):
        raise ValueError("Las detecciones deben ser una lista")

    high_risk_count = sum(1 for d in detections
                         if d.get('class') in HIGH_RISK_CLASSES)
    medium_risk_count = sum(1 for d in detections
                           if d.get('class') in MEDIUM_RISK_CLASSES)

    if high_risk_count >= 3:
        risk_level = "ALTO"
        recommendations = [
            "Intervención inmediata requerida",
            "Eliminar agua estancada inmediatamente"
        ]
    elif high_risk_count >= 1 or medium_risk_count >= 3:
        risk_level = "MEDIO"
        recommendations = [
            "Monitoreo regular necesario",
            "Limpiar recipientes y contenedores"
        ]
    elif medium_risk_count >= 1:
        risk_level = "BAJO"
        recommendations = [
            "Mantenimiento preventivo",
            "Limpieza regular del área"
        ]
    else:
        risk_level = "MÍNIMO"
        recommendations = ["Vigilancia rutinaria"]

    return {
        'level': risk_level,
        'high_risk_sites': high_risk_count,
        'medium_risk_sites': medium_risk_count,
        'recommendations': recommendations
    }