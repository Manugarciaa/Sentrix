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
        image_data: bytes = None,
        image_url: str = None,
        model: str = "yolo11s-seg.pt",
        confidence_threshold: float = 0.5,
        include_gps: bool = True
    ) -> Dict[str, Any]:
        """
        Send image to YOLO service for detection

        Args:
            image_data: Binary image data
            image_url: URL to image (alternative to image_data)
            model: Model name to use
            confidence_threshold: Detection confidence threshold
            include_gps: Whether to include GPS metadata extraction

        Returns:
            Dict with detection results parsed for backend
        """

        if not image_data and not image_url:
            raise ValueError("Either image_data or image_url must be provided")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Prepare request data
                data = {
                    "model": model,
                    "confidence_threshold": confidence_threshold,
                    "include_gps": include_gps
                }

                # Prepare files/data for request
                if image_data:
                    files = {"file": ("image.jpg", image_data, "image/jpeg")}
                    response = await client.post(
                        f"{self.base_url}/detect",
                        data=data,
                        files=files
                    )
                else:
                    data["image_url"] = image_url
                    response = await client.post(
                        f"{self.base_url}/detect",
                        data=data
                    )

                response.raise_for_status()
                yolo_response = response.json()

                # Validate response format
                if not validate_yolo_response(yolo_response):
                    raise ValueError("Invalid YOLO service response format")

                # Parse response to backend format
                parsed_data = parse_yolo_report(yolo_response)

                return {
                    "success": True,
                    "yolo_response": yolo_response,
                    "parsed_data": parsed_data
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

    async def detect_image_from_url(
        self,
        image_url: str,
        model: str = "yolo11s-seg.pt",
        confidence_threshold: float = 0.5,
        include_gps: bool = True
    ) -> Dict[str, Any]:
        """
        Convenience method to detect from URL

        Args:
            image_url: URL to image
            model: Model name to use
            confidence_threshold: Detection confidence threshold
            include_gps: Whether to include GPS metadata

        Returns:
            Dict with detection results
        """
        return await self.detect_image(
            image_url=image_url,
            model=model,
            confidence_threshold=confidence_threshold,
            include_gps=include_gps
        )

    async def detect_image_from_file(
        self,
        image_data: bytes,
        filename: str = "image.jpg",
        model: str = "yolo11s-seg.pt",
        confidence_threshold: float = 0.5,
        include_gps: bool = True
    ) -> Dict[str, Any]:
        """
        Convenience method to detect from file data

        Args:
            image_data: Binary image data
            filename: Original filename (for metadata)
            model: Model name to use
            confidence_threshold: Detection confidence threshold
            include_gps: Whether to include GPS metadata

        Returns:
            Dict with detection results
        """
        return await self.detect_image(
            image_data=image_data,
            model=model,
            confidence_threshold=confidence_threshold,
            include_gps=include_gps
        )


# Singleton instance
yolo_client = YOLOServiceClient()