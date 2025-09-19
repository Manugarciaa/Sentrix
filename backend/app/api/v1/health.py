"""
Health check endpoints
Endpoints de verificación de salud del sistema
"""

import httpx
from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check():
    """
    Health check endpoint para verificar el estado del sistema
    """
    try:
        # Check database connection (mock for now)
        db_status = "healthy"  # Will implement with actual DB later

        # Check Redis connection (mock for now)
        redis_status = "healthy"  # Will implement with actual Redis later

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "services": {
                "database": db_status,
                "redis": redis_status,
                "yolo_service": "unknown"  # Will check in next endpoint
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@router.get("/health/yolo")
async def yolo_health_check():
    """
    Proxy health check al yolo-service
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{settings.yolo_service_url}/health")

            if response.status_code == 200:
                yolo_data = response.json()
                return {
                    "status": "healthy",
                    "yolo_service": yolo_data,
                    "connection": "success"
                }
            else:
                return {
                    "status": "unhealthy",
                    "yolo_service": None,
                    "connection": f"HTTP {response.status_code}"
                }

    except httpx.ConnectError:
        return {
            "status": "unhealthy",
            "yolo_service": None,
            "connection": "connection_refused",
            "message": f"Cannot connect to YOLO service at {settings.yolo_service_url}"
        }
    except httpx.TimeoutException:
        return {
            "status": "unhealthy",
            "yolo_service": None,
            "connection": "timeout",
            "message": "YOLO service timeout"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "yolo_service": None,
            "connection": "error",
            "message": str(e)
        }