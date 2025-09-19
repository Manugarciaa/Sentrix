"""
Main FastAPI application for Sentrix Backend
Aplicación principal FastAPI para Sentrix Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.v1 import health, analyses

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Sentrix API",
    description="Sistema de Detección de Criaderos de Aedes aegypti",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(analyses.router, prefix="/api/v1", tags=["analyses"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sentrix API - Sistema de Detección de Criaderos de Aedes aegypti",
        "version": "1.0.0",
        "docs": "/docs"
    }