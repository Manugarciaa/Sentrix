"""
Reports and statistics endpoints for Sentrix API
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from ...database.connection import get_db
from ...utils.auth import get_current_active_user
from ...database.models.models import UserProfile

router = APIRouter()


@router.get("/statistics")
async def get_dashboard_statistics(
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics for the current user
    """
    try:
        # For now, let's return mock data that matches the dashboard structure
        # In a real implementation, these would be calculated from actual data

        # Calculate some basic stats from user data
        total_users = db.execute(text("SELECT COUNT(*) FROM user_profiles WHERE is_active = true")).scalar()

        stats = {
            "total_analyses": 1234,  # This would come from analyses table
            "high_risk_detections": 89,  # From detections table with high risk
            "monitored_locations": 156,  # From unique locations in analyses
            "active_users": total_users or 43,
            "monthly_change": {
                "total_analyses": 12,
                "high_risk_detections": -8,
                "monitored_locations": 5,
                "active_users": 23
            }
        }

        return stats

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving statistics: {str(e)}"
        )


@router.get("/risk-distribution")
async def get_risk_distribution(
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get risk level distribution for dashboard charts
    """
    try:
        # Mock data - in real implementation this would query detections table
        distribution = [
            {"name": "Alto", "value": 23, "color": "#dc2626"},
            {"name": "Medio", "value": 45, "color": "#f59e0b"},
            {"name": "Bajo", "value": 67, "color": "#059669"},
            {"name": "Mínimo", "value": 89, "color": "#6b7280"}
        ]

        return distribution

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving risk distribution: {str(e)}"
        )


@router.get("/monthly-analyses")
async def get_monthly_analyses(
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get monthly analyses data for charts
    """
    try:
        # Mock data - in real implementation this would query analyses table grouped by month
        monthly_data = [
            {"month": "Ene", "count": 45},
            {"month": "Feb", "count": 52},
            {"month": "Mar", "count": 61},
            {"month": "Abr", "count": 73},
            {"month": "May", "count": 69},
            {"month": "Jun", "count": 84}
        ]

        return monthly_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving monthly analyses: {str(e)}"
        )


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 10,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get recent activity for dashboard
    """
    try:
        # Mock data - in real implementation this would query recent analyses and validations
        recent_activity = [
            {
                "id": 1,
                "type": "analysis",
                "description": "Nuevo análisis procesado en Miraflores",
                "risk": "ALTO",
                "time": "Hace 5 minutos",
                "timestamp": datetime.now() - timedelta(minutes=5)
            },
            {
                "id": 2,
                "type": "validation",
                "description": "Detección validada por experto en San Isidro",
                "risk": "MEDIO",
                "time": "Hace 12 minutos",
                "timestamp": datetime.now() - timedelta(minutes=12)
            },
            {
                "id": 3,
                "type": "analysis",
                "description": "Análisis completado en La Molina",
                "risk": "BAJO",
                "time": "Hace 25 minutos",
                "timestamp": datetime.now() - timedelta(minutes=25)
            },
            {
                "id": 4,
                "type": "validation",
                "description": "Múltiples detecciones en Surco",
                "risk": "ALTO",
                "time": "Hace 1 hora",
                "timestamp": datetime.now() - timedelta(hours=1)
            }
        ]

        return recent_activity[:limit]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving recent activity: {str(e)}"
        )


@router.get("/quality-metrics")
async def get_quality_metrics(
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get quality metrics for the system
    """
    try:
        metrics = {
            "accuracy": 94.5,
            "precision": 91.2,
            "recall": 87.8,
            "f1_score": 89.4,
            "processing_time_avg": 2.3,  # seconds
            "validated_detections": 78.5  # percentage
        }

        return metrics

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving quality metrics: {str(e)}"
        )


@router.get("/validation-stats")
async def get_validation_stats(
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get validation statistics
    """
    try:
        stats = {
            "pending_validations": 45,
            "validated_today": 23,
            "expert_accuracy": 96.7,
            "avg_validation_time": 145,  # seconds
            "top_validators": [
                {"name": "Dr. García", "count": 89, "accuracy": 98.1},
                {"name": "Dra. López", "count": 76, "accuracy": 96.5},
                {"name": "Dr. Martínez", "count": 54, "accuracy": 97.2}
            ]
        }

        return stats

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving validation stats: {str(e)}"
        )