"""
Health check endpoints for Sentrix Backend
Endpoints de verificación de salud del sistema

Provides two types of health checks:
- /health: Liveness probe (simple check that app is running)
- /health/ready: Readiness probe (checks all dependencies)
"""

import httpx
import os
from fastapi import APIRouter, status as http_status
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from ...config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check():
    """
    Liveness probe - Simple check that application is running

    This endpoint should always return 200 OK if the application is alive.
    Load balancers use this to detect if the instance should be restarted.

    Does NOT check dependencies - use /health/ready for that.
    """
    return {
        "status": "healthy",
        "service": "sentrix-backend",
        "version": "2.3.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/health/ready")
async def readiness_check():
    """
    Readiness probe - Comprehensive check of all dependencies

    This endpoint returns 200 OK only if ALL dependencies are available.
    Load balancers use this to determine if instance can receive traffic.

    Checks:
    - Database connectivity
    - YOLO service availability
    - Redis connectivity (if configured)

    Returns:
    - 200 OK: All dependencies healthy, ready to receive traffic
    - 503 Service Unavailable: One or more dependencies unhealthy
    """
    checks = {
        "database": await check_database(),
        "yolo_service": await check_yolo_service(),
        "redis": await check_redis()
    }

    # Determine overall health
    all_healthy = all(check["healthy"] for check in checks.values())

    response = {
        "status": "ready" if all_healthy else "not_ready",
        "service": "sentrix-backend",
        "version": "2.3.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks
    }

    # Return 503 if any check failed
    status_code = http_status.HTTP_200_OK if all_healthy else http_status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content=response
    )


@router.get("/health/yolo")
async def yolo_health_check():
    """
    Detailed YOLO service health check

    Returns full YOLO service health information
    """
    yolo_check = await check_yolo_service()

    response = {
        "status": "healthy" if yolo_check["healthy"] else "unhealthy",
        "yolo_service": yolo_check,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    status_code = http_status.HTTP_200_OK if yolo_check["healthy"] else http_status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content=response
    )


@router.get("/health/circuit-breakers")
async def circuit_breakers_status():
    """
    Circuit breaker status endpoint

    Returns the current state of all circuit breakers in the system.
    Useful for monitoring and understanding service protection status.

    Circuit breaker states:
    - closed: Normal operation, requests pass through
    - open: Too many failures, requests fail fast
    - half-open: Testing if service recovered
    """
    from ...core.services.yolo_service import yolo_circuit_breaker

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "circuit_breakers": {
            "yolo_service": {
                "name": yolo_circuit_breaker.name,
                "state": yolo_circuit_breaker.current_state,
                "fail_counter": yolo_circuit_breaker.fail_counter,
                "fail_max": yolo_circuit_breaker.fail_max,
                "reset_timeout": yolo_circuit_breaker.reset_timeout,
                "description": "Circuit breaker for YOLO object detection service"
            }
        }
    }


# ============================================
# Dependency Check Functions
# ============================================

async def check_database() -> dict:
    """
    Check database connectivity

    Returns:
        dict: {
            "healthy": bool,
            "response_time_ms": int,
            "error": str (optional)
        }
    """
    from datetime import datetime
    start_time = datetime.now()

    try:
        # Try to import database connection
        try:
            from ...database.connection import test_database_connection
            db_status = test_database_connection()
        except ImportError:
            # If connection module not available, try Supabase
            try:
                from ...utils.supabase_client import SupabaseManager
                supabase = SupabaseManager()
                # Simple query to test connection
                result = supabase.client.table('analyses').select('id').limit(1).execute()
                db_status = True
            except Exception as e:
                return {
                    "healthy": False,
                    "response_time_ms": 0,
                    "error": f"Database check failed: {str(e)}"
                }

        response_time = int((datetime.now() - start_time).total_seconds() * 1000)

        if db_status:
            return {
                "healthy": True,
                "response_time_ms": response_time,
                "connection": "established"
            }
        else:
            return {
                "healthy": False,
                "response_time_ms": response_time,
                "error": "Database connection test returned false"
            }

    except Exception as e:
        response_time = int((datetime.now() - start_time).total_seconds() * 1000)
        return {
            "healthy": False,
            "response_time_ms": response_time,
            "error": str(e)
        }


async def check_yolo_service() -> dict:
    """
    Check YOLO service availability

    Returns:
        dict: {
            "healthy": bool,
            "response_time_ms": int,
            "service_url": str,
            "model_available": bool (optional),
            "error": str (optional)
        }
    """
    from datetime import datetime
    start_time = datetime.now()

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
            response = await client.get(f"{settings.yolo_service_url}/health")

            response_time = int((datetime.now() - start_time).total_seconds() * 1000)

            if response.status_code == 200:
                yolo_data = response.json()

                return {
                    "healthy": True,
                    "response_time_ms": response_time,
                    "service_url": settings.yolo_service_url,
                    "status": yolo_data.get("status"),
                    "model_available": yolo_data.get("model_available", False),
                    "version": yolo_data.get("version")
                }
            else:
                return {
                    "healthy": False,
                    "response_time_ms": response_time,
                    "service_url": settings.yolo_service_url,
                    "error": f"HTTP {response.status_code}"
                }

    except httpx.ConnectError:
        response_time = int((datetime.now() - start_time).total_seconds() * 1000)
        return {
            "healthy": False,
            "response_time_ms": response_time,
            "service_url": settings.yolo_service_url,
            "error": "Connection refused - YOLO service not reachable"
        }

    except httpx.TimeoutException:
        return {
            "healthy": False,
            "response_time_ms": 5000,  # Timeout threshold
            "service_url": settings.yolo_service_url,
            "error": "Timeout - YOLO service did not respond within 5 seconds"
        }

    except Exception as e:
        response_time = int((datetime.now() - start_time).total_seconds() * 1000)
        return {
            "healthy": False,
            "response_time_ms": response_time,
            "service_url": settings.yolo_service_url,
            "error": str(e)
        }


async def check_redis() -> dict:
    """
    Check Redis connectivity

    Returns:
        dict: {
            "healthy": bool,
            "response_time_ms": int,
            "error": str (optional)
        }
    """
    from datetime import datetime
    start_time = datetime.now()

    # Check if Redis is configured
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        return {
            "healthy": True,  # Not configured = not required
            "response_time_ms": 0,
            "status": "not_configured"
        }

    try:
        import redis

        r = redis.from_url(redis_url, socket_connect_timeout=5)
        r.ping()

        response_time = int((datetime.now() - start_time).total_seconds() * 1000)

        return {
            "healthy": True,
            "response_time_ms": response_time,
            "connection": "established"
        }

    except ImportError:
        return {
            "healthy": True,  # Redis not installed = not required
            "response_time_ms": 0,
            "status": "not_installed"
        }

    except redis.exceptions.ConnectionError:
        response_time = int((datetime.now() - start_time).total_seconds() * 1000)
        return {
            "healthy": False,
            "response_time_ms": response_time,
            "error": "Connection refused - Redis not reachable"
        }

    except redis.exceptions.TimeoutError:
        return {
            "healthy": False,
            "response_time_ms": 5000,
            "error": "Timeout - Redis did not respond within 5 seconds"
        }

    except Exception as e:
        response_time = int((datetime.now() - start_time).total_seconds() * 1000)
        return {
            "healthy": False,
            "response_time_ms": response_time,
            "error": str(e)
        }
