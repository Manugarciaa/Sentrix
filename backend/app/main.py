"""
Main FastAPI application for Sentrix Backend
Aplicación principal FastAPI para Sentrix Backend
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.v1 import health, analyses, auth, reports

# Load environment variables
load_dotenv()

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Sentrix API",
    description="Sistema de Detección de Criaderos de Aedes aegypti",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - Configuración segura
allowed_origins = [
    "http://localhost:3000",  # Frontend development
    "http://localhost:3002",  # Current frontend port
    "http://localhost:8080",  # Alternative frontend port
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3002",
    "http://127.0.0.1:8080",
]

# Add production origins from environment if available
import os
if production_origins := os.getenv("ALLOWED_ORIGINS"):
    allowed_origins.extend(production_origins.split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(analyses.router, prefix="/api/v1", tags=["analyses"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sentrix API - Sistema de Detección de Criaderos de Aedes aegypti",
        "version": "1.0.0",
        "docs": "/docs"
    }