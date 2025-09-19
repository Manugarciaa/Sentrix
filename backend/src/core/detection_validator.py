"""
Detection Validator for Sentrix Backend
Validador de Detecciones para Sentrix Backend

Handles expert validation and quality assurance of detections
Maneja validación de expertos y aseguramiento de calidad de detecciones
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func

from ..utils.database_utils import get_db_context
from ..database.models import Detection, Analysis, User
from ..database.models.enums import RiskLevel, UserRole


class DetectionValidator:
    """
    Validator for expert review and quality assurance
    Validador para revisión de expertos y aseguramiento de calidad
    """

    def __init__(self):
        pass

    def get_pending_validations(
        self,
        expert_id: Optional[int] = None,
        priority: str = "high_risk",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get detections pending expert validation
        Obtener detecciones pendientes de validación de expertos
        """
        with get_db_context() as db:
            query = db.query(Detection).join(Analysis).filter(
                Detection.is_validated == False
            )

            # Filter by priority
            if priority == "high_risk":
                query = query.filter(Analysis.risk_level.in_([
                    RiskLevel.ALTO.value,
                    RiskLevel.CRITICO.value
                ]))
            elif priority == "high_confidence":
                query = query.filter(Detection.confidence >= 0.8)

            # Order by analysis creation date (most recent first)
            query = query.order_by(Analysis.created_at.desc())

            detections = query.limit(limit).all()

            return [
                {
                    "detection_id": det.id,
                    "analysis_id": det.analysis_id,
                    "class_name": det.class_name,
                    "confidence": det.confidence,
                    "image_path": det.analysis.image_path,
                    "risk_level": det.analysis.risk_level,
                    "created_at": det.analysis.created_at,
                    "mask_area": det.mask_area,
                    "has_gps": bool(det.location_data and det.location_data.get("has_location"))
                }
                for det in detections
            ]

    def validate_detection(
        self,
        detection_id: int,
        expert_id: int,
        is_valid: bool,
        expert_notes: Optional[str] = None,
        confidence_adjustment: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Validate detection by expert
        Validar detección por experto
        """
        with get_db_context() as db:
            detection = db.query(Detection).filter(Detection.id == detection_id).first()

            if not detection:
                raise ValueError("Detection not found")

            # Update validation
            detection.is_validated = True
            detection.expert_validation = is_valid
            detection.expert_notes = expert_notes
            detection.validated_by = expert_id
            detection.validated_at = datetime.now()

            # Adjust confidence if provided
            if confidence_adjustment is not None:
                detection.expert_confidence = confidence_adjustment

            db.commit()

            return {
                "detection_id": detection.id,
                "validated": True,
                "expert_validation": is_valid,
                "expert_notes": expert_notes,
                "validated_at": detection.validated_at
            }

    def batch_validate_detections(
        self,
        validations: List[Dict[str, Any]],
        expert_id: int
    ) -> Dict[str, Any]:
        """
        Validate multiple detections in batch
        Validar múltiples detecciones por lotes

        Args:
            validations: List of dicts with keys: detection_id, is_valid, notes
        """
        results = {
            "validated": 0,
            "failed": 0,
            "errors": []
        }

        with get_db_context() as db:
            for validation in validations:
                try:
                    detection_id = validation["detection_id"]
                    is_valid = validation["is_valid"]
                    notes = validation.get("notes")

                    detection = db.query(Detection).filter(Detection.id == detection_id).first()

                    if not detection:
                        results["errors"].append({
                            "detection_id": detection_id,
                            "error": "Detection not found"
                        })
                        results["failed"] += 1
                        continue

                    # Update validation
                    detection.is_validated = True
                    detection.expert_validation = is_valid
                    detection.expert_notes = notes
                    detection.validated_by = expert_id
                    detection.validated_at = datetime.now()

                    results["validated"] += 1

                except Exception as e:
                    results["errors"].append({
                        "detection_id": validation.get("detection_id"),
                        "error": str(e)
                    })
                    results["failed"] += 1

            db.commit()

        return results

    def get_validation_statistics(
        self,
        expert_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get validation statistics
        Obtener estadísticas de validación
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        with get_db_context() as db:
            base_query = db.query(Detection).filter(
                Detection.is_validated == True,
                Detection.validated_at >= cutoff_date
            )

            if expert_id:
                base_query = base_query.filter(Detection.validated_by == expert_id)

            # Total validations
            total_validations = base_query.count()

            # Approved vs rejected
            approved = base_query.filter(Detection.expert_validation == True).count()
            rejected = base_query.filter(Detection.expert_validation == False).count()

            # By class
            class_stats = base_query.with_entities(
                Detection.class_name,
                func.count(Detection.id).label('count'),
                func.avg(Detection.confidence).label('avg_confidence')
            ).group_by(Detection.class_name).all()

            # Expert activity (if no specific expert)
            expert_activity = []
            if not expert_id:
                expert_stats = db.query(
                    Detection.validated_by,
                    func.count(Detection.id).label('validations')
                ).filter(
                    Detection.is_validated == True,
                    Detection.validated_at >= cutoff_date
                ).group_by(Detection.validated_by).all()

                expert_activity = [
                    {"expert_id": exp_id, "validations": count}
                    for exp_id, count in expert_stats
                ]

            return {
                "period_days": days,
                "total_validations": total_validations,
                "approved": approved,
                "rejected": rejected,
                "approval_rate": approved / total_validations if total_validations > 0 else 0,
                "class_statistics": [
                    {
                        "class_name": class_name,
                        "validations": count,
                        "avg_confidence": float(avg_conf) if avg_conf else 0
                    }
                    for class_name, count, avg_conf in class_stats
                ],
                "expert_activity": expert_activity
            }

    def get_quality_metrics(self) -> Dict[str, Any]:
        """
        Get overall quality metrics for the detection system
        Obtener métricas de calidad generales del sistema de detección
        """
        with get_db_context() as db:
            # Total detections
            total_detections = db.query(Detection).count()

            # Validated detections
            validated_detections = db.query(Detection).filter(
                Detection.is_validated == True
            ).count()

            # Accuracy metrics (from validated detections)
            if validated_detections > 0:
                approved_detections = db.query(Detection).filter(
                    Detection.is_validated == True,
                    Detection.expert_validation == True
                ).count()

                accuracy = approved_detections / validated_detections
            else:
                accuracy = 0

            # Confidence distribution
            confidence_ranges = [
                (0.5, 0.7, "Medium"),
                (0.7, 0.9, "High"),
                (0.9, 1.0, "Very High")
            ]

            confidence_distribution = {}
            for min_conf, max_conf, label in confidence_ranges:
                count = db.query(Detection).filter(
                    Detection.confidence >= min_conf,
                    Detection.confidence < max_conf
                ).count()
                confidence_distribution[label] = count

            # Risk level distribution
            risk_distribution = db.query(
                Analysis.risk_level,
                func.count(Analysis.id)
            ).group_by(Analysis.risk_level).all()

            return {
                "total_detections": total_detections,
                "validated_detections": validated_detections,
                "validation_coverage": validated_detections / total_detections if total_detections > 0 else 0,
                "system_accuracy": accuracy,
                "confidence_distribution": confidence_distribution,
                "risk_distribution": {
                    risk: count for risk, count in risk_distribution
                }
            }

    def suggest_retraining_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Suggest detections for model retraining based on expert feedback
        Sugerir detecciones para reentrenamiento del modelo basado en feedback de expertos
        """
        with get_db_context() as db:
            # Get rejected detections with high original confidence
            rejected_high_conf = db.query(Detection).join(Analysis).filter(
                Detection.is_validated == True,
                Detection.expert_validation == False,
                Detection.confidence >= 0.7
            ).order_by(Detection.confidence.desc()).limit(limit // 2).all()

            # Get approved detections with low original confidence
            approved_low_conf = db.query(Detection).join(Analysis).filter(
                Detection.is_validated == True,
                Detection.expert_validation == True,
                Detection.confidence < 0.6
            ).order_by(Detection.confidence.asc()).limit(limit // 2).all()

            suggestions = []

            for detection in rejected_high_conf:
                suggestions.append({
                    "detection_id": detection.id,
                    "image_path": detection.analysis.image_path,
                    "class_name": detection.class_name,
                    "original_confidence": detection.confidence,
                    "expert_validation": False,
                    "suggestion_reason": "High confidence but expert rejected",
                    "priority": "high"
                })

            for detection in approved_low_conf:
                suggestions.append({
                    "detection_id": detection.id,
                    "image_path": detection.analysis.image_path,
                    "class_name": detection.class_name,
                    "original_confidence": detection.confidence,
                    "expert_validation": True,
                    "suggestion_reason": "Low confidence but expert approved",
                    "priority": "medium"
                })

            return suggestions