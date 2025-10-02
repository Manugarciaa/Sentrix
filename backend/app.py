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

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

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
    allowed_origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
    expose_headers=["Content-Type", "Authorization"],
    max_age=600,  # Cache preflight requests for 10 minutes
)


# ============================================
# Global Exception Handlers
# ============================================
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with consistent format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "http_error"
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed information"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": 422,
                "message": "Validation error",
                "type": "validation_error",
                "details": exc.errors()
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    # Log the error
    import traceback
    print(f"[ERROR] Unexpected error: {exc}")
    print(traceback.format_exc())

    # Don't expose internal errors in production
    if os.getenv("ENVIRONMENT") == "production":
        message = "Internal server error"
    else:
        message = str(exc)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": 500,
                "message": message,
                "type": "internal_error"
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
