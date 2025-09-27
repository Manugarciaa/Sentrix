"""
FastAPI application for Sentrix Backend
Aplicación FastAPI para Sentrix Backend
"""

import sys
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Ensure shared library is available
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import configuration
from .config import get_settings

settings = get_settings()

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

# Import and include routers
try:
    from .api.v1 import health, analyses, auth, reports

    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(analyses.router, prefix="/api/v1", tags=["analyses"])
    app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
    app.include_router(reports.router, prefix="/api/v1", tags=["reports"])

except ImportError as e:
    print(f"Warning: Could not import all routers: {e}")


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