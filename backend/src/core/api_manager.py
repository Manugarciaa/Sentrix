"""
API Manager for Sentrix Backend
Gestor de API para Sentrix Backend

Main controller for handling API requests and coordinating services
Controlador principal para manejar peticiones API y coordinar servicios
"""

from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import httpx

from ..database.models import Analysis, Detection
from ..schemas.analyses import AnalysisCreate, AnalysisResponse
from .services.yolo_service import YOLOServiceClient
from ..utils.database_utils import get_db_context
from ..config import get_settings
from ..exceptions import (
    YOLOServiceException,
    YOLOTimeoutException,
    DatabaseException,
    AnalysisNotFoundException
)
from ..logging_config import get_logger

logger = get_logger(__name__)

settings = get_settings()


class SentrixAPIManager:
    """
    Main API manager for coordinating backend operations
    Gestor principal de API para coordinar operaciones del backend
    """

    def __init__(self):
        self.yolo_client = YOLOServiceClient()

    async def create_analysis(self, analysis_data: AnalysisCreate) -> AnalysisResponse:
        """
        Create new analysis with YOLO detection
        Crear nuevo análisis con detección YOLO
        """
        try:
            # Process image with YOLO service
            yolo_results = await self.yolo_client.detect_breeding_sites(
                image_path=analysis_data.image_path,
                confidence_threshold=analysis_data.confidence_threshold or settings.yolo_confidence_threshold
            )

            # Store in database
            with get_db_context() as db:
                # Create analysis record
                db_analysis = Analysis(
                    image_path=analysis_data.image_path,
                    user_id=analysis_data.user_id,
                    confidence_threshold=analysis_data.confidence_threshold or settings.yolo_confidence_threshold,
                    total_detections=len(yolo_results.get("detections", [])),
                    risk_level=yolo_results.get("risk_assessment", {}).get("level", "UNKNOWN")
                )
                db.add(db_analysis)
                db.flush()  # Get the ID

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

                return AnalysisResponse(
                    id=db_analysis.id,
                    image_path=db_analysis.image_path,
                    user_id=db_analysis.user_id,
                    total_detections=db_analysis.total_detections,
                    risk_level=db_analysis.risk_level,
                    created_at=db_analysis.created_at,
                    yolo_results=yolo_results
                )

        except httpx.TimeoutException:
            logger.error("yolo_service_timeout", image_path=analysis_data.image_path)
            raise YOLOTimeoutException(timeout_seconds=settings.yolo_timeout_seconds)
        except httpx.HTTPStatusError as e:
            logger.error("yolo_http_error", status=e.response.status_code, error=str(e))
            raise YOLOServiceException(f"YOLO service HTTP error: {e.response.status_code}")
        except httpx.HTTPError as e:
            logger.error("yolo_connection_error", error=str(e))
            raise YOLOServiceException(f"Failed to connect to YOLO service: {str(e)}")
        except KeyError as e:
            logger.error("missing_yolo_field", field=str(e), exc_info=True)
            raise YOLOServiceException(f"Missing required field in YOLO response: {e}")
        except Exception as e:
            logger.error("analysis_creation_failed", error=str(e), exc_info=True)
            raise DatabaseException(f"Error creating analysis: {str(e)}", operation="create_analysis")

    def get_analysis(self, analysis_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get analysis by ID with optional user filtering
        Obtener análisis por ID con filtrado opcional de usuario
        """
        with get_db_context() as db:
            query = db.query(Analysis).filter(Analysis.id == analysis_id)

            if user_id:
                query = query.filter(Analysis.user_id == user_id)

            analysis = query.first()

            if not analysis:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Analysis not found"
                )

            # Get detections
            detections = db.query(Detection).filter(Detection.analysis_id == analysis_id).all()

            return {
                "analysis": analysis,
                "detections": [
                    {
                        "id": det.id,
                        "class_name": det.class_name,
                        "confidence": det.confidence,
                        "polygon_data": det.polygon_data,
                        "location_data": det.location_data
                    }
                    for det in detections
                ]
            }

    def list_analyses(
        self,
        user_id: Optional[int] = None,
        risk_level: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List analyses with filtering options
        Listar análisis con opciones de filtrado
        """
        with get_db_context() as db:
            query = db.query(Analysis)

            if user_id:
                query = query.filter(Analysis.user_id == user_id)

            if risk_level:
                query = query.filter(Analysis.risk_level == risk_level)

            # Order by most recent first
            query = query.order_by(Analysis.created_at.desc())

            # Apply pagination
            analyses = query.offset(offset).limit(limit).all()

            return [
                {
                    "id": analysis.id,
                    "image_path": analysis.image_path,
                    "user_id": analysis.user_id,
                    "total_detections": analysis.total_detections,
                    "risk_level": analysis.risk_level,
                    "created_at": analysis.created_at
                }
                for analysis in analyses
            ]

    async def validate_detection(
        self,
        detection_id: int,
        is_valid: bool,
        expert_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate detection by expert
        Validar detección por experto
        """
        with get_db_context() as db:
            detection = db.query(Detection).filter(Detection.id == detection_id).first()

            if not detection:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Detection not found"
                )

            # Update validation status
            detection.is_validated = True
            detection.expert_validation = is_valid
            detection.expert_notes = expert_notes

            db.commit()

            return {
                "detection_id": detection.id,
                "is_valid": is_valid,
                "expert_notes": expert_notes,
                "updated_at": detection.updated_at
            }