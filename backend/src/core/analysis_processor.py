"""
Analysis Processor for Sentrix Backend
Procesador de Análisis para Sentrix Backend

Handles batch processing and analysis workflows
Maneja procesamiento por lotes y flujos de trabajo de análisis
"""

import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

from .services.yolo_service import YOLOServiceClient
from ..utils.paths import get_logs_dir
from ..utils.database_utils import get_db_context
from ..database.models import Analysis, Detection


class AnalysisProcessor:
    """
    Processor for handling multiple analysis operations
    Procesador para manejar múltiples operaciones de análisis
    """

    def __init__(self):
        self.yolo_client = YOLOServiceClient()
        self.logs_dir = get_logs_dir()

    async def batch_process_images(
        self,
        image_paths: List[str],
        user_id: int,
        confidence_threshold: float = 0.5,
        include_gps: bool = True
    ) -> Dict[str, Any]:
        """
        Process multiple images in batch
        Procesar múltiples imágenes por lotes
        """
        results = {
            "total_images": len(image_paths),
            "processed": 0,
            "failed": 0,
            "analyses": [],
            "errors": []
        }

        # Create batch log
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        log_file = self.logs_dir / f"{batch_id}.json"

        for image_path in image_paths:
            try:
                # Validate image exists
                if not Path(image_path).exists():
                    results["errors"].append({
                        "image_path": image_path,
                        "error": "File not found"
                    })
                    results["failed"] += 1
                    continue

                # Process with YOLO
                yolo_results = await self.yolo_client.detect_breeding_sites(
                    image_path=image_path,
                    confidence_threshold=confidence_threshold,
                    include_gps=include_gps
                )

                # Store in database
                analysis_id = await self._store_analysis_result(
                    image_path=image_path,
                    user_id=user_id,
                    confidence_threshold=confidence_threshold,
                    yolo_results=yolo_results
                )

                results["analyses"].append({
                    "analysis_id": analysis_id,
                    "image_path": image_path,
                    "detections": len(yolo_results.get("detections", [])),
                    "risk_level": yolo_results.get("risk_assessment", {}).get("level")
                })

                results["processed"] += 1

            except Exception as e:
                results["errors"].append({
                    "image_path": image_path,
                    "error": str(e)
                })
                results["failed"] += 1

        # Save batch log
        await self._save_batch_log(log_file, batch_id, results)

        return results

    async def _store_analysis_result(
        self,
        image_path: str,
        user_id: int,
        confidence_threshold: float,
        yolo_results: Dict[str, Any]
    ) -> int:
        """
        Store analysis result in database
        Almacenar resultado de análisis en base de datos
        """
        with get_db_context() as db:
            # Create analysis record
            db_analysis = Analysis(
                image_path=image_path,
                user_id=user_id,
                confidence_threshold=confidence_threshold,
                total_detections=len(yolo_results.get("detections", [])),
                risk_level=yolo_results.get("risk_assessment", {}).get("level", "UNKNOWN")
            )
            db.add(db_analysis)
            db.flush()

            # Create detection records
            for detection in yolo_results.get("detections", []):
                db_detection = Detection(
                    analysis_id=db_analysis.id,
                    class_name=detection["class"],
                    class_id=detection["class_id"],
                    confidence=detection["confidence"],
                    polygon_data=detection.get("polygon", []),
                    mask_area=detection.get("mask_area", 0.0),
                    location_data=detection.get("location", {})
                )
                db.add(db_detection)

            db.commit()
            return db_analysis.id

    async def _save_batch_log(
        self,
        log_file: Path,
        batch_id: str,
        results: Dict[str, Any]
    ):
        """
        Save batch processing log
        Guardar log de procesamiento por lotes
        """
        log_data = {
            "batch_id": batch_id,
            "timestamp": datetime.now().isoformat(),
            "results": results
        }

        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"ERROR: Error saving batch log: {e}")

    async def get_batch_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get batch processing statistics
        Obtener estadísticas de procesamiento por lotes
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)

        with get_db_context() as db:
            # Total analyses
            total_analyses = db.query(Analysis).filter(
                Analysis.created_at >= cutoff_date
            ).count()

            # Analyses by risk level
            risk_stats = db.query(Analysis.risk_level, db.func.count(Analysis.id)).filter(
                Analysis.created_at >= cutoff_date
            ).group_by(Analysis.risk_level).all()

            # Total detections
            total_detections = db.query(Detection).join(Analysis).filter(
                Analysis.created_at >= cutoff_date
            ).count()

            # Detection validation stats
            validation_stats = db.query(
                Detection.expert_validation,
                db.func.count(Detection.id)
            ).filter(
                Detection.is_validated == True
            ).group_by(Detection.expert_validation).all()

            return {
                "period_days": days,
                "total_analyses": total_analyses,
                "total_detections": total_detections,
                "risk_level_distribution": {
                    risk: count for risk, count in risk_stats
                },
                "validation_stats": {
                    "validated_detections": sum(count for _, count in validation_stats),
                    "expert_approved": sum(count for is_valid, count in validation_stats if is_valid),
                    "expert_rejected": sum(count for is_valid, count in validation_stats if not is_valid)
                }
            }

    async def cleanup_old_analyses(self, days: int = 90) -> Dict[str, Any]:
        """
        Cleanup old analyses (soft delete)
        Limpiar análisis antiguos (eliminación suave)
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)

        with get_db_context() as db:
            # Mark old analyses as deleted
            updated_count = db.query(Analysis).filter(
                Analysis.created_at < cutoff_date,
                Analysis.deleted_at.is_(None)
            ).update({
                "deleted_at": datetime.now()
            })

            db.commit()

            return {
                "cleaned_analyses": updated_count,
                "cutoff_date": cutoff_date.isoformat()
            }