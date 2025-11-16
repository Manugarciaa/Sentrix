"""
YOLO Service client for integrating with the yolo-service
Cliente del servicio YOLO para integrar con el yolo-service

Enhanced with timeout configuration and retry logic for production resilience
"""

import httpx
from typing import Dict, Any, Optional
from fastapi import HTTPException
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_log,
    after_log
)
from pybreaker import CircuitBreaker, CircuitBreakerError

from ...config import get_settings
from ...utils.integrations.yolo_integration import parse_yolo_report, validate_yolo_response
from ...utils.image_conversion import prepare_image_for_processing
from ...logging_config import get_logger, get_request_id

logger = get_logger(__name__)
settings = get_settings()


# Circuit breaker for YOLO service
# Opens after 5 consecutive failures, stays open for 60 seconds
# Note: Listeners removed to avoid compatibility issues with pybreaker
yolo_circuit_breaker = CircuitBreaker(
    fail_max=5,              # Open circuit after 5 consecutive failures
    reset_timeout=60,        # Try to close after 60 seconds
    exclude=[httpx.HTTPStatusError],  # Don't count 4xx/5xx as circuit failures
    name="yolo-service"
)


class YOLOServiceClient:
    """
    Client for communicating with the YOLO service

    Features:
    - Configurable timeouts (connect, read, write, pool)
    - Connection pooling with limits
    - Automatic retry with exponential backoff
    - Comprehensive error handling
    """

    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.yolo_service_url

        # Configure timeout for different operations
        self.timeout = httpx.Timeout(
            connect=5.0,    # 5 seconds to establish connection
            read=settings.yolo_timeout_seconds,      # Configurable timeout for YOLO processing
            write=10.0,     # 10 seconds to send request
            pool=5.0        # 5 seconds to get connection from pool
        )

        # Configure connection pooling
        self.limits = httpx.Limits(
            max_connections=100,        # Max total connections
            max_keepalive_connections=20  # Max idle connections in pool
        )

    async def health_check(self) -> Dict[str, Any]:
        """
        Check YOLO service health status

        Timeouts: 10s total (no retry for health checks)

        Returns:
            Dict with health status

        Raises:
            HTTPException: If health check fails
        """
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(10.0),
                limits=self.limits
            ) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return response.json()

        except httpx.ConnectError as e:
            logger.error(f"Cannot connect to YOLO service at {self.base_url}: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Cannot connect to YOLO service at {self.base_url}"
            )
        except httpx.TimeoutException as e:
            logger.error(f"YOLO service health check timeout: {e}")
            raise HTTPException(
                status_code=504,
                detail="YOLO service health check timeout"
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"YOLO service returned error: {e.response.status_code}")
            raise HTTPException(
                status_code=503,
                detail=f"YOLO service unhealthy: {e.response.status_code}"
            )
        except Exception as e:
            logger.error(f"YOLO service health check failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=503,
                detail=f"YOLO service error: {str(e)}"
            )

    @yolo_circuit_breaker
    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.WARNING)
    )
    async def _call_yolo_detect(
        self,
        image_data: bytes,
        filename: str,
        form_data: dict,
        content_type: str
    ) -> httpx.Response:
        """
        Internal method to call YOLO detect endpoint with retry logic

        Retries on:
        - TimeoutException: Server too slow or overloaded
        - ConnectError: Server temporarily unreachable

        Does NOT retry on:
        - HTTPStatusError (4xx, 5xx): Application-level errors
        - Other exceptions: Likely unrecoverable

        Retry schedule:
        - Attempt 1: Immediate
        - Attempt 2: Wait 1 second
        - Attempt 3: Wait 2 seconds
        - Attempt 4: Wait 4 seconds (max 3 retries)
        """
        async with httpx.AsyncClient(
            timeout=self.timeout,
            limits=self.limits
        ) as client:
            files = {"file": (filename, image_data, content_type)}

            # Propagate request ID to YOLO service for distributed tracing
            headers = {}
            request_id = get_request_id()
            if request_id:
                headers["X-Request-ID"] = request_id

            response = await client.post(
                f"{self.base_url}/detect",
                data=form_data,
                files=files,
                headers=headers
            )

            # Raise for HTTP errors (will not trigger retry)
            response.raise_for_status()

            return response

    async def detect_image(
        self,
        image_data: bytes,
        filename: str = "image.jpg",
        confidence_threshold: float = None,
        include_gps: bool = True
    ) -> Dict[str, Any]:
        """
        Enviar imagen al servicio YOLO para detección

        Enhanced with:
        - Automatic retry on timeouts and connection errors (3 attempts)
        - Detailed timeout logging
        - Connection pooling for performance

        Args:
            image_data: Datos binarios de la imagen
            filename: Nombre del archivo (para determinar tipo)
            confidence_threshold: Umbral de confianza para detección
            include_gps: Si extraer metadatos GPS

        Returns:
            Dict con resultados de detección procesados para backend

        Raises:
            ValueError: If image_data is empty
            HTTPException: If YOLO service fails after retries
        """

        if not image_data:
            raise ValueError("image_data es requerido")

        # Set default confidence threshold from settings
        if confidence_threshold is None:
            confidence_threshold = settings.yolo_confidence_threshold

        try:
            # Convert HEIC to JPEG if needed
            processed_image_data, processed_filename = prepare_image_for_processing(image_data, filename)

            # Preparar datos de formulario
            form_data = {
                "confidence_threshold": confidence_threshold,
                "include_gps": include_gps
            }

            # Determinar tipo MIME basado en extensión
            content_type = "image/jpeg"
            if processed_filename.lower().endswith(('.png',)):
                content_type = "image/png"
            elif processed_filename.lower().endswith(('.tiff', '.tif')):
                content_type = "image/tiff"

            logger.info(
                "yolo_detection_started",
                original_filename=filename,
                processed_filename=processed_filename,
                original_size=len(image_data),
                processed_size=len(processed_image_data),
                confidence_threshold=confidence_threshold,
                content_type=content_type
            )

            # Call with retry logic using processed image data
            response = await self._call_yolo_detect(
                image_data=processed_image_data,
                filename=processed_filename,
                form_data=form_data,
                content_type=content_type
            )

            yolo_response = response.json()

            logger.info(
                "yolo_detection_completed",
                image_filename=filename,
                processing_time_ms=yolo_response.get("processing_time_ms"),
                total_detections=yolo_response.get("total_detections", 0)
            )

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
                "confidence_threshold": yolo_response.get("confidence_threshold"),
                "processed_image_path": yolo_response.get("processed_image_path"),  # Ruta de imagen procesada
                "processed_image_base64": yolo_response.get("processed_image_base64")  # Imagen procesada en base64
            }

        except CircuitBreakerError:
            logger.error(
                "yolo_circuit_breaker_open",
                image_filename=filename,
                message="Circuit breaker is OPEN - YOLO service temporarily unavailable"
            )
            raise HTTPException(
                status_code=503,
                detail="YOLO service temporarily unavailable due to repeated failures. Please try again in a moment."
            )

        except httpx.HTTPStatusError as e:
            logger.error(
                "yolo_http_error",
                status_code=e.response.status_code,
                response_text=e.response.text[:500],  # Limit log size
                image_filename=filename,
                exc_info=True
            )
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"YOLO service error: {e.response.text}"
            )

        except httpx.ConnectError as e:
            logger.error(
                "yolo_connection_error",
                yolo_service_url=self.base_url,
                image_filename=filename,
                error=str(e),
                exc_info=True
            )
            raise HTTPException(
                status_code=503,
                detail=f"YOLO service unavailable. Please try again later."
            )

        except httpx.TimeoutException as e:
            logger.error(
                "yolo_timeout_error",
                image_filename=filename,
                file_size=len(image_data),
                timeout_config=str(self.timeout),
                exc_info=True
            )
            raise HTTPException(
                status_code=504,
                detail="YOLO service timeout - image processing took too long. Try a smaller image."
            )

        except Exception as e:
            logger.error(
                "yolo_unexpected_error",
                image_filename=filename,
                error_type=type(e).__name__,
                error=str(e),
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail=f"Internal error processing image: {str(e)}"
            )

    async def download_processed_image(self, processed_image_path: str) -> bytes:
        """
        Descarga la imagen procesada desde el YOLO service

        Args:
            processed_image_path: Ruta de la imagen procesada en el servidor YOLO

        Returns:
            bytes: Datos binarios de la imagen procesada

        Raises:
            HTTPException: Si no se puede descargar la imagen
        """
        if not processed_image_path:
            logger.warning("download_processed_image_no_path", message="No processed image path provided")
            return None

        try:
            import os
            # La ruta del YOLO service es absoluta, necesitamos convertirla a relativa para el endpoint
            # Ejemplo: /tmp/processed/imagen_processed.jpg -> processed/imagen_processed.jpg
            relative_path = os.path.basename(os.path.dirname(processed_image_path)) + "/" + os.path.basename(processed_image_path)

            # Endpoint para descargar archivos del YOLO service
            download_url = f"{self.base_url}/download/{relative_path}"

            logger.info(
                "downloading_processed_image",
                processed_image_path=processed_image_path,
                download_url=download_url
            )

            async with httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                limits=self.limits
            ) as client:
                response = await client.get(download_url)
                response.raise_for_status()

                image_data = response.content

                logger.info(
                    "processed_image_downloaded",
                    image_size=len(image_data),
                    path=processed_image_path
                )

                return image_data

        except httpx.HTTPStatusError as e:
            logger.warning(
                "processed_image_download_failed",
                status_code=e.response.status_code,
                path=processed_image_path,
                error=str(e)
            )
            # No es crítico si falla, retornar None
            return None

        except Exception as e:
            logger.warning(
                "processed_image_download_error",
                path=processed_image_path,
                error=str(e)
            )
            # No es crítico si falla, retornar None
            return None

    async def get_available_models(self) -> Dict[str, Any]:
        """
        Obtener lista de modelos disponibles en el servicio YOLO

        Timeouts: 10s total (no retry for non-critical operation)

        Returns:
            Dict con modelos disponibles (empty list on error)
        """
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(10.0),
                limits=self.limits
            ) as client:
                response = await client.get(f"{self.base_url}/models")
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return {"available_models": [], "current_model": "unknown"}


# Singleton instance
yolo_client = YOLOServiceClient()