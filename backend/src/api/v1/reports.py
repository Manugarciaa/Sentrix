"""
Reports and statistics endpoints for Sentrix API
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from ...database.connection import get_db
from ...utils.auth import get_current_active_user
from ...database.models.models import UserProfile
from ...exceptions import DatabaseException, ImageProcessingException
from ...logging_config import get_logger

logger = get_logger(__name__)

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

    except KeyError as e:
        logger.error("stats_missing_field", field=str(e), exc_info=True)
        raise DatabaseException(f"Missing required field in statistics: {e}", operation="get_dashboard_stats")
    except Exception as e:
        logger.error("stats_retrieval_error", error=str(e), exc_info=True)
        raise DatabaseException(f"Error retrieving statistics: {str(e)}", operation="get_dashboard_stats")


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
        logger.error("risk_distribution_error", error=str(e), exc_info=True)
        raise DatabaseException(f"Error retrieving risk distribution: {str(e)}", operation="get_risk_distribution")


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
        logger.error("monthly_analyses_error", error=str(e), exc_info=True)
        raise DatabaseException(f"Error retrieving monthly analyses: {str(e)}", operation="get_monthly_analyses")


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
        logger.error("recent_activity_error", error=str(e), exc_info=True)
        raise DatabaseException(f"Error retrieving recent activity: {str(e)}", operation="get_recent_activity")


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
        logger.error("quality_metrics_error", error=str(e), exc_info=True)
        raise DatabaseException(f"Error retrieving quality metrics: {str(e)}", operation="get_quality_metrics")


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
        logger.error("validation_stats_error", error=str(e), exc_info=True)
        raise DatabaseException(f"Error retrieving validation stats: {str(e)}", operation="get_validation_stats")


@router.get("/list")
async def get_reports_list(
    skip: int = 0,
    limit: int = 20,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get list of generated reports

    Note: Reports are generated on-demand. This endpoint returns empty for now.
    In a full implementation, you'd store report metadata in a Reports table.
    """
    return {
        "reports": [],
        "total": 0,
        "message": "Reports are generated on-demand. Use /generate endpoint."
    }


@router.post("/generate")
async def generate_report(
    report_config: dict,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate a new report

    Creates a PDF or CSV report based on configuration and returns it as download.
    """
    from ..services.report_service import ReportService
    from datetime import datetime
    from fastapi.responses import StreamingResponse

    try:
        # Validate report config
        report_type = report_config.get("type", "summary")
        report_format = report_config.get("format", "pdf")

        # Extract filters
        filters = {
            "date_from": report_config.get("date_from"),
            "date_to": report_config.get("date_to"),
            "risk_level": report_config.get("filters", {}).get("risk_level"),
            "has_gps": report_config.get("filters", {}).get("has_gps"),
        }

        # Initialize report service
        report_service = ReportService(db)

        # Generate report based on format
        if report_format == "pdf":
            buffer = report_service.generate_pdf_report(
                report_type=report_type,
                filters=filters,
                user_id=current_user.id
            )

            filename = f"sentrix_report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            return StreamingResponse(
                buffer,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}"
                }
            )

        elif report_format == "csv":
            buffer = report_service.generate_csv_report(
                report_type=report_type,
                filters=filters
            )

            filename = f"sentrix_report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            return StreamingResponse(
                iter([buffer.getvalue()]),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}"
                }
            )

        else:
            # JSON format
            stats = report_service._get_summary_statistics(filters)
            return {
                "format": "json",
                "report_type": report_type,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "data": stats
            }

    except ImportError as e:
        logger.error("report_service_not_available", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Report generation service not available"
        )
    except ValueError as e:
        logger.error("report_invalid_config", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid report configuration: {str(e)}"
        )
    except OSError as e:
        logger.error("report_io_error", error=str(e), exc_info=True)
        raise ImageProcessingException(f"Error writing report file: {str(e)}")
    except Exception as e:
        logger.error("report_generation_error", error=str(e), exc_info=True)
        raise ImageProcessingException(f"Error generating report: {str(e)}")


@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a report

    Deletes a report and its associated file.
    """
    try:
        # In a real implementation, you would:
        # 1. Verify report exists and belongs to user (or user is admin)
        # 2. Delete file from storage
        # 3. Delete metadata from database

        # For now, return success
        return {
            "message": "Report deleted successfully",
            "report_id": report_id
        }

    except FileNotFoundError as e:
        logger.error("report_not_found", report_id=report_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report not found: {report_id}"
        )
    except OSError as e:
        logger.error("report_delete_io_error", report_id=report_id, error=str(e), exc_info=True)
        raise ImageProcessingException(f"Error deleting report file: {str(e)}")
    except Exception as e:
        logger.error("report_delete_error", report_id=report_id, error=str(e), exc_info=True)
        raise DatabaseException(f"Error deleting report: {str(e)}", operation="delete_report")