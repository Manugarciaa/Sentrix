"""
Sentrix Backend - Main Application Entry Point
Punto de entrada principal de la aplicación Sentrix Backend
"""

import os
import sys
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Load environment variables
load_dotenv()

# Setup structured logging
from src.logging_config import setup_logging, get_logger
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
setup_logging(log_level=log_level)

# Validate configuration on startup
try:
    from src.utils.config_validator import ConfigValidator
    print("\n[CONFIG] Validating configuration...")
    validation_result = ConfigValidator.validate_environment(strict=False)

    if not validation_result.is_valid:
        ConfigValidator.print_validation_report(validation_result)
        if os.getenv("ENVIRONMENT") == "production":
            print("[ERROR] Cannot start in production with invalid configuration")
            sys.exit(1)
        else:
            print("[WARN] Starting with warnings in development mode")
    else:
        print("[OK] Configuration validated successfully")
except ImportError:
    print("[WARN] Config validator not available, skipping validation")
except Exception as e:
    print(f"[WARN] Config validation failed: {e}")

# ============================================
# Application Lifespan Events
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    print("[STARTUP] Starting Sentrix Backend...")

    # Test database connection
    try:
        from src.database.connection import test_database_connection
        db_status = test_database_connection()
        if db_status:
            print("[OK] Database connection successful")
        else:
            print("[WARN] Database connection failed")
    except Exception as e:
        print(f"[WARN] Could not test database: {e}")

    # Test YOLO service connection
    try:
        from src.core.services.yolo_service import YOLOServiceClient
        yolo_client = YOLOServiceClient()
        # Note: health check is async, skip for now
        print("[OK] YOLO service client initialized")
    except Exception as e:
        print(f"[WARN] Could not initialize YOLO client: {e}")

    print("[OK] Sentrix Backend ready!")

    yield

    # Shutdown
    print("[SHUTDOWN] Shutting down Sentrix Backend...")
    print("[OK] Cleanup complete")


# ============================================
# Create FastAPI Application
# ============================================
app = FastAPI(
    title="Sentrix API",
    description="Sistema de Detección de Criaderos de Aedes aegypti usando IA",
    version="2.3.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "Sentrix Team",
        "url": "https://github.com/yourusername/sentrix",
    },
    license_info={
        "name": "MIT",
    }
)


# ============================================
# Setup Rate Limiting
# ============================================
try:
    from src.middleware.rate_limit import setup_rate_limiting
    limiter = setup_rate_limiting(app)
    print("[OK] Rate limiting configured successfully")
except ImportError as e:
    print(f"[WARN] Rate limiting not available: {e}")
    limiter = None


# ============================================
# CORS Configuration
# ============================================
# Get allowed origins from environment or use defaults
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3000",
]

# Add production origins from environment
if allowed_origins_env:
    allowed_origins.extend(allowed_origins_env.split(","))

# Only allow * in development
if os.getenv("ENVIRONMENT", "development") == "development":
    # In development, use ["*"] directly instead of appending
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False if "*" in allowed_origins else True,  # credentials not allowed with *
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],  # Allow all headers in development
    expose_headers=["Content-Type", "Authorization", "X-Request-ID"],
    max_age=600,  # Cache preflight requests for 10 minutes
)


# ============================================
# Request ID Middleware
# ============================================
from src.middleware.request_id import setup_request_id_middleware
setup_request_id_middleware(app)
print("[OK] Request ID middleware configured")


# ============================================
# Global Exception Handlers
# ============================================
import uuid
from datetime import datetime

# Use structured logger
logger = get_logger(__name__)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions with consistent format and tracking

    Enhanced with:
    - Unique error ID for tracking
    - Request context logging with structured logging
    - Consistent JSON structure
    - Automatic request_id from context
    """
    error_id = str(uuid.uuid4())

    # Log HTTP exception with structured logging
    logger.warning(
        "http_exception",
        error_id=error_id,
        status_code=exc.status_code,
        path=str(request.url.path),
        method=request.method,
        client_host=request.client.host if request.client else "unknown",
        error_detail=str(exc.detail)
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "id": error_id,
                "code": exc.status_code,
                "message": exc.detail,
                "type": "http_error",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors with detailed information

    Enhanced with:
    - Unique error ID for tracking
    - Full validation error details
    - Structured logging with request context
    - Automatic request_id from context
    """
    error_id = str(uuid.uuid4())

    # Log validation error with structured logging
    logger.warning(
        "validation_error",
        error_id=error_id,
        path=str(request.url.path),
        method=request.method,
        client_host=request.client.host if request.client else "unknown",
        validation_errors=exc.errors()
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "id": error_id,
                "code": 422,
                "message": "Validation error",
                "type": "validation_error",
                "details": exc.errors(),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions with proper logging and error masking

    Enhanced with:
    - Unique error ID for tracking (critical for debugging)
    - Full traceback logging with structured logging
    - Production error masking
    - Request context capture
    - Automatic request_id from context
    """
    import traceback

    error_id = str(uuid.uuid4())

    # Capture full request context
    request_headers = dict(request.headers)
    # Remove sensitive headers from logs
    sensitive_headers = ['authorization', 'cookie', 'x-api-key']
    for header in sensitive_headers:
        if header in request_headers:
            request_headers[header] = "***REDACTED***"

    # Log full error with structured logging
    logger.error(
        "unhandled_exception",
        error_id=error_id,
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        path=str(request.url.path),
        method=request.method,
        client_host=request.client.host if request.client else "unknown",
        query_params=dict(request.query_params),
        headers=request_headers,
        traceback=traceback.format_exc(),
        exc_info=True
    )

    # Determine error message based on environment
    if os.getenv("ENVIRONMENT") == "production":
        # Production: mask error details
        message = "An internal error occurred. Please contact support with this error ID."
        # Don't include exception details
        error_type = "internal_error"
    else:
        # Development: show full error
        message = f"{type(exc).__name__}: {str(exc)}"
        error_type = type(exc).__name__

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "id": error_id,
                "code": 500,
                "message": message,
                "type": error_type,
                "timestamp": datetime.utcnow().isoformat(),
                # Only include in development
                **({"traceback": traceback.format_exc()} if os.getenv("ENVIRONMENT") != "production" else {})
            }
        }
    )


# ============================================
# Root Endpoints
# ============================================
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Sentrix API",
        "description": "Sistema de Detección de Criaderos de Aedes aegypti",
        "version": "2.3.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "status": "running",
        "endpoints": {
            "auth": "/api/v1/auth",
            "analyses": "/api/v1/analyses",
            "detections": "/api/v1/detections",
            "reports": "/api/v1/reports",
            "health": "/api/v1/health"
        }
    }


@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.3.0",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }


# ============================================
# Include API Routers
# ============================================
# Import routers with error handling
routers_loaded = []
routers_failed = []

try:
    from src.api.v1 import health
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    routers_loaded.append("health")
except ImportError as e:
    routers_failed.append(("health", str(e)))
    print(f"[WARN] Could not import health router: {e}")

try:
    from src.api.v1 import auth
    app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
    routers_loaded.append("auth")
except ImportError as e:
    routers_failed.append(("auth", str(e)))
    print(f"[WARN] Could not import auth router: {e}")

try:
    from src.api.v1 import analyses
    app.include_router(analyses.router, prefix="/api/v1", tags=["analyses"])
    routers_loaded.append("analyses")
except ImportError as e:
    routers_failed.append(("analyses", str(e)))
    print(f"[WARN] Could not import analyses router: {e}")

try:
    from src.api.v1 import reports
    app.include_router(reports.router, prefix="/api/v1", tags=["reports"])
    routers_loaded.append("reports")
except ImportError as e:
    routers_failed.append(("reports", str(e)))
    print(f"[WARN] Could not import reports router: {e}")

try:
    from src.api.v1 import detections
    app.include_router(detections.router, prefix="/api/v1", tags=["detections"])
    routers_loaded.append("detections")
except ImportError as e:
    routers_failed.append(("detections", str(e)))
    print(f"[WARN] Could not import detections router: {e}")

# Print router loading summary
print(f"\n[ROUTERS] Loaded: {', '.join(routers_loaded) if routers_loaded else 'None'}")
if routers_failed:
    print(f"[ROUTERS] Failed: {', '.join([r[0] for r in routers_failed])}")


# ============================================
# Development/Production Mode
# ============================================
if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    reload = os.getenv("RELOAD_ON_CHANGE", "true").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    print(f"\n{'='*50}")
    print(f"Starting Sentrix Backend Server")
    print(f"{'='*50}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Reload: {reload}")
    print(f"Log Level: {log_level}")
    print(f"{'='*50}\n")

    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True
    )
