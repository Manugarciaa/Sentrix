"""
YOLO Service client for integrating with the yolo-service
Cliente del servicio YOLO para integrar con el yolo-service
"""

import httpx
from typing import Dict, Any, Optional
from fastapi import HTTPException
import logging

from app.config import get_settings
from app.utils.yolo_integration import parse_yolo_report, validate_yolo_response

logger = logging.getLogger(__name__)
settings = get_settings()


class YOLOServiceClient:
    """Client for communicating with the YOLO service"""

    def __init__(self, base_url: str = None, timeout: float = 60.0):
        self.base_url = base_url or settings.yolo_service_url
        self.timeout = timeout

    async def health_check(self) -> Dict[str, Any]:
        """
        Check YOLO service health status

        Returns:
            Dict with health status
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return response.json()

        except httpx.ConnectError:
            raise HTTPException(
                status_code=503,
                detail=f"Cannot connect to YOLO service at {self.base_url}"
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="YOLO service timeout"
            )
        except Exception as e:
            logger.error(f"YOLO service health check failed: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"YOLO service error: {str(e)}"
            )

    async def detect_image(
        self,
        image_data: bytes,
        filename: str = "image.jpg",
        confidence_threshold: float = 0.5,
        include_gps: bool = True
    ) -> Dict[str, Any]:
        """
        Enviar imagen al servicio YOLO para detección

        Args:
            image_data: Datos binarios de la imagen
            filename: Nombre del archivo (para determinar tipo)
            confidence_threshold: Umbral de confianza para detección
            include_gps: Si extraer metadatos GPS

        Returns:
            Dict con resultados de detección procesados para backend
        """

        if not image_data:
            raise ValueError("image_data es requerido")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Preparar datos de formulario
                form_data = {
                    "confidence_threshold": confidence_threshold,
                    "include_gps": include_gps
                }

                # Determinar tipo MIME basado en extensión
                content_type = "image/jpeg"
                if filename.lower().endswith(('.png',)):
                    content_type = "image/png"
                elif filename.lower().endswith(('.tiff', '.tif')):
                    content_type = "image/tiff"

                # Preparar archivo para envío
                files = {"file": (filename, image_data, content_type)}

                response = await client.post(
                    f"{self.base_url}/detect",
                    data=form_data,
                    files=files
                )

                response.raise_for_status()
                yolo_response = response.json()

                logger.info(f"YOLO service responded successfully for {filename}")

                return {
                    "success": True,
                    "analysis_id": yolo_response.get("analysis_id"),
                    "status": yolo_response.get("status"),
                    "detections": yolo_response.get("detections", []),
                    "total_detections": yolo_response.get("total_detections", 0),
                    "risk_assessment": yolo_response.get("risk_assessment", {}),
                    "location": yolo_response.get("location"),
                    "camera_info": yolo_response.get("camera_info"),
                    "processing_time_ms": yolo_response.get("processing_time_ms", 0),
                    "model_used": yolo_response.get("model_used"),
                    "confidence_threshold": yolo_response.get("confidence_threshold")
                }

        except httpx.HTTPStatusError as e:
            logger.error(f"YOLO service HTTP error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"YOLO service error: {e.response.text}"
            )
        except httpx.ConnectError:
            logger.error(f"Cannot connect to YOLO service at {self.base_url}")
            raise HTTPException(
                status_code=503,
                detail=f"Cannot connect to YOLO service at {self.base_url}"
            )
        except httpx.TimeoutException:
            logger.error("YOLO service timeout")
            raise HTTPException(
                status_code=504,
                detail="YOLO service timeout - image processing took too long"
            )
        except Exception as e:
            logger.error(f"Unexpected error calling YOLO service: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Internal error processing image: {str(e)}"
            )

    async def get_available_models(self) -> Dict[str, Any]:
        """
        Obtener lista de modelos disponibles en el servicio YOLO

        Returns:
            Dict con modelos disponibles
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/models")
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return {"available_models": [], "current_model": "unknown"}


# Singleton instance
yolo_client = YOLOServiceClient()