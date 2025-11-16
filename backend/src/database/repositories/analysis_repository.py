"""
Analysis Repository

Provides database operations for Analysis model.
"""

from typing import Optional, List, Tuple
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from .base import BaseRepository
from ..models.models import Analysis, Detection


class AnalysisRepository(BaseRepository[Analysis]):
    """Repository for Analysis operations"""

    def __init__(self, db: Session):
        super().__init__(Analysis, db)

    # ============================================
    # Custom Query Methods
    # ============================================

    def get_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Analysis]:
        """
        Get all analyses for a user.

        Args:
            user_id: User's UUID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Analysis instances
        """
        try:
            stmt = (
                select(self.model)
                .where(self.model.user_id == user_id)
                .order_by(self.model.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            result = self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise self.RepositoryError(f"Failed to get analyses by user: {e}")

    def get_with_detections(self, analysis_id: UUID) -> Optional[Analysis]:
        """
        Get analysis with all detections eagerly loaded.

        Args:
            analysis_id: Analysis UUID

        Returns:
            Analysis instance with detections or None
        """
        try:
            stmt = (
                select(self.model)
                .options(joinedload(self.model.detections))
                .where(self.model.id == analysis_id)
            )
            result = self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            raise self.RepositoryError(f"Failed to get analysis with detections: {e}")

    def get_high_risk_analyses(
        self,
        user_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Analysis]:
        """
        Get high-risk analyses.

        Args:
            user_id: Optional user UUID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of high-risk Analysis instances
        """
        try:
            stmt = (
                select(self.model)
                .where(self.model.risk_level == "high")
                .order_by(self.model.created_at.desc())
            )

            if user_id:
                stmt = stmt.where(self.model.user_id == user_id)

            stmt = stmt.offset(skip).limit(limit)
            result = self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise self.RepositoryError(f"Failed to get high-risk analyses: {e}")

    def get_by_risk_level(
        self,
        risk_level: str,
        user_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Analysis]:
        """
        Get analyses by risk level.

        Args:
            risk_level: Risk level (low, medium, high)
            user_id: Optional user UUID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Analysis instances
        """
        try:
            stmt = (
                select(self.model)
                .where(self.model.risk_level == risk_level)
                .order_by(self.model.created_at.desc())
            )

            if user_id:
                stmt = stmt.where(self.model.user_id == user_id)

            stmt = stmt.offset(skip).limit(limit)
            result = self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise self.RepositoryError(f"Failed to get analyses by risk level: {e}")

    def get_recent_analyses(
        self,
        user_id: Optional[UUID] = None,
        limit: int = 10
    ) -> List[Analysis]:
        """
        Get most recent analyses.

        Args:
            user_id: Optional user UUID to filter by
            limit: Maximum number of records to return

        Returns:
            List of Analysis instances
        """
        try:
            stmt = (
                select(self.model)
                .order_by(self.model.created_at.desc())
                .limit(limit)
            )

            if user_id:
                stmt = stmt.where(self.model.user_id == user_id)

            result = self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise self.RepositoryError(f"Failed to get recent analyses: {e}")

    def get_by_location(
        self,
        latitude: float,
        longitude: float,
        radius_meters: float = 1000,
        limit: int = 100
    ) -> List[Analysis]:
        """
        Get analyses within a geographic radius.

        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_meters: Search radius in meters
            limit: Maximum number of records to return

        Returns:
            List of Analysis instances within radius
        """
        try:
            # Using PostGIS ST_DWithin for geographic queries
            from geoalchemy2 import functions as geo_func

            point = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)

            stmt = (
                select(self.model)
                .where(
                    geo_func.ST_DWithin(
                        self.model.location,
                        point,
                        radius_meters
                    )
                )
                .where(self.model.has_gps_data == True)
                .order_by(self.model.created_at.desc())
                .limit(limit)
            )

            result = self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise self.RepositoryError(f"Failed to get analyses by location: {e}")

    # ============================================
    # Analysis-Specific Operations
    # ============================================

    def create_analysis(
        self,
        user_id: UUID,
        image_url: str,
        image_filename: str,
        image_size_bytes: int,
        **kwargs
    ) -> Analysis:
        """
        Create a new analysis.

        Args:
            user_id: User's UUID
            image_url: URL of the uploaded image
            image_filename: Original filename
            image_size_bytes: File size in bytes
            **kwargs: Additional analysis fields

        Returns:
            Created Analysis instance
        """
        return self.create(
            user_id=user_id,
            image_url=image_url,
            image_filename=image_filename,
            image_size_bytes=image_size_bytes,
            **kwargs
        )

    def update_detection_counts(
        self,
        analysis_id: UUID,
        total_detections: int,
        high_risk_count: int,
        medium_risk_count: int
    ) -> Analysis:
        """
        Update detection counts for an analysis.

        Args:
            analysis_id: Analysis UUID
            total_detections: Total number of detections
            high_risk_count: Number of high-risk detections
            medium_risk_count: Number of medium-risk detections

        Returns:
            Updated Analysis instance
        """
        return self.update_or_404(
            analysis_id,
            total_detections=total_detections,
            high_risk_count=high_risk_count,
            medium_risk_count=medium_risk_count
        )

    def update_risk_assessment(
        self,
        analysis_id: UUID,
        risk_level: str,
        risk_score: float,
        recommendations: List[str]
    ) -> Analysis:
        """
        Update risk assessment for an analysis.

        Args:
            analysis_id: Analysis UUID
            risk_level: Overall risk level (low, medium, high)
            risk_score: Numerical risk score
            recommendations: List of recommendations

        Returns:
            Updated Analysis instance
        """
        return self.update_or_404(
            analysis_id,
            risk_level=risk_level,
            risk_score=risk_score,
            recommendations=recommendations
        )

    def set_processing_metadata(
        self,
        analysis_id: UUID,
        model_used: str,
        confidence_threshold: float,
        processing_time_ms: int,
        yolo_service_version: str
    ) -> Analysis:
        """
        Set processing metadata for an analysis.

        Args:
            analysis_id: Analysis UUID
            model_used: Name/version of model used
            confidence_threshold: Confidence threshold applied
            processing_time_ms: Processing time in milliseconds
            yolo_service_version: YOLO service version

        Returns:
            Updated Analysis instance
        """
        return self.update_or_404(
            analysis_id,
            model_used=model_used,
            confidence_threshold=confidence_threshold,
            processing_time_ms=processing_time_ms,
            yolo_service_version=yolo_service_version
        )

    # ============================================
    # Statistics
    # ============================================

    def count_by_user(self, user_id: UUID) -> int:
        """
        Count analyses for a user.

        Args:
            user_id: User's UUID

        Returns:
            Number of analyses
        """
        return self.count(user_id=user_id)

    def count_high_risk(self, user_id: Optional[UUID] = None) -> int:
        """
        Count high-risk analyses.

        Args:
            user_id: Optional user UUID to filter by

        Returns:
            Number of high-risk analyses
        """
        filters = {"risk_level": "high"}
        if user_id:
            filters["user_id"] = user_id
        return self.count(**filters)

    def get_statistics(self, user_id: Optional[UUID] = None) -> dict:
        """
        Get analysis statistics.

        Args:
            user_id: Optional user UUID to filter by

        Returns:
            Dictionary with statistics
        """
        try:
            stmt = select(
                func.count(self.model.id).label("total"),
                func.count(self.model.id).filter(self.model.risk_level == "high").label("high_risk"),
                func.count(self.model.id).filter(self.model.risk_level == "medium").label("medium_risk"),
                func.count(self.model.id).filter(self.model.risk_level == "low").label("low_risk"),
                func.avg(self.model.total_detections).label("avg_detections"),
                func.sum(self.model.total_detections).label("total_detections")
            )

            if user_id:
                stmt = stmt.where(self.model.user_id == user_id)

            result = self.db.execute(stmt).one()

            return {
                "total_analyses": result.total or 0,
                "high_risk_count": result.high_risk or 0,
                "medium_risk_count": result.medium_risk or 0,
                "low_risk_count": result.low_risk or 0,
                "avg_detections_per_analysis": float(result.avg_detections or 0),
                "total_detections": result.total_detections or 0
            }
        except Exception as e:
            raise self.RepositoryError(f"Failed to get analysis statistics: {e}")
