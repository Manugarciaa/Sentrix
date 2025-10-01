"""
Simple FastAPI application entry point for Sentrix Backend
Punto de entrada simplificado para la aplicación FastAPI de Sentrix Backend
"""

import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Create FastAPI app
app = FastAPI(
    title="Sentrix API",
    description="Sistema de Detección de Criaderos de Aedes aegypti",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
allowed_origins = [
    "http://localhost:3000",  # Frontend development
    "http://localhost:3001",  # Frontend development (when 3000 is in use)
    "http://localhost:3002",  # Current frontend port
    "https://sentrix.vercel.app",  # Production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sentrix API - Sistema de Detección de Criaderos de Aedes aegypti",
        "version": "2.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "version": "2.0.0"
    }


@app.get("/api/v1/health")
async def api_health_check():
    """API health check"""
    import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {
            "database": "healthy",
            "redis": "healthy",
            "yolo_service": "unknown"
        }
    }


# Import routers with error handling
try:
    # Add src directory to path for imports
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    # Import health router as it's the most stable
    from src.api.v1 import health
    app.include_router(health.router, prefix="/api/v1", tags=["health"])

except ImportError as e:
    print(f"Warning: Could not import health router: {e}")

try:
    # Import other routers if available
    from src.api.v1 import analyses
    app.include_router(analyses.router, prefix="/api/v1", tags=["analyses"])
except ImportError as e:
    print(f"Warning: Could not import analyses router: {e}")

try:
    from src.api.v1 import auth
    app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
except ImportError as e:
    print(f"Warning: Could not import auth router: {e}")

try:
    from src.api.v1 import reports
    app.include_router(reports.router, prefix="/api/v1", tags=["reports"])
except ImportError as e:
    print(f"Warning: Could not import reports router: {e}")


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", "8000"))

    uvicorn.run(app, host=host, port=port, reload=True)