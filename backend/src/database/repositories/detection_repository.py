"""
Detection Repository

Provides database operations for Detection model.
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from .base import BaseRepository
from ..models.models import Detection


class DetectionRepository(BaseRepository[Detection]):
    """Repository for Detection operations"""

    def __init__(self, db: Session):
        super().__init__(Detection, db)

    # ============================================
    # Custom Query Methods
    # ============================================

    def get_by_analysis(
        self,
        analysis_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Detection]:
        """
        Get all detections for an analysis.

        Args:
            analysis_id: Analysis UUID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Detection instances
        """
        try:
            stmt = (
                select(self.model)
                .where(self.model.analysis_id == analysis_id)
                .order_by(self.model.confidence.desc())
                .offset(skip)
                .limit(limit)
            )
            result = self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise self.RepositoryError(f"Failed to get detections by analysis: {e}")

    def get_high_confidence(
        self,
        analysis_id: Optional[UUID] = None,
        min_confidence: float = 0.8,
        limit: int = 100
    ) -> List[Detection]:
        """
        Get high-confidence detections.

        Args:
            analysis_id: Optional analysis UUID to filter by
            min_confidence: Minimum confidence threshold
            limit: Maximum number of records to return

        Returns:
            List of Detection instances
        """
        try:
            stmt = (
                select(self.model)
                .where(self.model.confidence >= min_confidence)
                .order_by(self.model.confidence.desc())
                .limit(limit)
            )

            if analysis_id:
                stmt = stmt.where(self.model.analysis_id == analysis_id)

            result = self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise self.RepositoryError(f"Failed to get high-confidence detections: {e}")

    def get_by_risk_level(
        self,
        risk_level: str,
        analysis_id: Optional[UUID] = None,
        limit: int = 100
    ) -> List[Detection]:
        """
        Get detections by risk level.

        Args:
            risk_level: Risk level (low, medium, high)
            analysis_id: Optional analysis UUID to filter by
            limit: Maximum number of records to return

        Returns:
            List of Detection instances
        """
        try:
            stmt = (
                select(self.model)
                .where(self.model.risk_level == risk_level)
                .order_by(self.model.confidence.desc())
                .limit(limit)
            )

            if analysis_id:
                stmt = stmt.where(self.model.analysis_id == analysis_id)

            result = self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise self.RepositoryError(f"Failed to get detections by risk level: {e}")

    def get_by_class(
        self,
        class_name: str,
        analysis_id: Optional[UUID] = None,
        limit: int = 100
    ) -> List[Detection]:
        """
        Get detections by class name.

        Args:
            class_name: Detection class name
            analysis_id: Optional analysis UUID to filter by
            limit: Maximum number of records to return

        Returns:
            List of Detection instances
        """
        try:
            stmt = (
                select(self.model)
                .where(self.model.class_name == class_name)
                .order_by(self.model.confidence.desc())
                .limit(limit)
            )

            if analysis_id:
                stmt = stmt.where(self.model.analysis_id == analysis_id)

            result = self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise self.RepositoryError(f"Failed to get detections by class: {e}")

    def get_pending_validation(
        self,
        limit: int = 100
    ) -> List[Detection]:
        """
        Get detections pending validation.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of Detection instances
        """
        try:
            stmt = (
                select(self.model)
                .where(self.model.validation_status == "pending")
                .where(self.model.requires_verification == True)
                .order_by(self.model.created_at.desc())
                .limit(limit)
            )
            result = self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise self.RepositoryError(f"Failed to get pending validation detections: {e}")

    def get_validated_detections(
        self,
        validated_by: Optional[UUID] = None,
        validation_status: str = "validated",
        limit: int = 100
    ) -> List[Detection]:
        """
        Get validated detections.

        Args:
            validated_by: Optional validator UUID to filter by
            validation_status: Validation status
            limit: Maximum number of records to return

        Returns:
            List of Detection instances
        """
        try:
            stmt = (
                select(self.model)
                .where(self.model.validation_status == validation_status)
                .order_by(self.model.validated_at.desc())
                .limit(limit)
            )

            if validated_by:
                stmt = stmt.where(self.model.validated_by == validated_by)

            result = self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise self.RepositoryError(f"Failed to get validated detections: {e}")

    def get_expiring_soon(
        self,
        days_ahead: int = 7,
        limit: int = 100
    ) -> List[Detection]:
        """
        Get detections expiring within specified days.

        Args:
            days_ahead: Number of days to look ahead
            limit: Maximum number of records to return

        Returns:
            List of Detection instances
        """
        try:
            expiry_threshold = datetime.now(timezone.utc) + timedelta(days=days_ahead)

            stmt = (
                select(self.model)
                .where(self.model.expires_at.isnot(None))
                .where(self.model.expires_at <= expiry_threshold)
                .where(self.model.expires_at > datetime.now(timezone.utc))
                .order_by(self.model.expires_at)
                .limit(limit)
            )
            result = self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise self.RepositoryError(f"Failed to get expiring detections: {e}")

    def get_expired(
        self,
        limit: int = 100
    ) -> List[Detection]:
        """
        Get expired detections.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of Detection instances
        """
        try:
            stmt = (
                select(self.model)
                .where(self.model.expires_at.isnot(None))
                .where(self.model.expires_at <= datetime.now(timezone.utc))
                .order_by(self.model.expires_at.desc())
                .limit(limit)
            )
            result = self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise self.RepositoryError(f"Failed to get expired detections: {e}")

    # ============================================
    # Detection-Specific Operations
    # ============================================

    def create_detection(
        self,
        analysis_id: UUID,
        class_id: int,
        class_name: str,
        confidence: float,
        risk_level: str,
        **kwargs
    ) -> Detection:
        """
        Create a new detection.

        Args:
            analysis_id: Analysis UUID
            class_id: Detection class ID
            class_name: Detection class name
            confidence: Confidence score
            risk_level: Risk level (low, medium, high)
            **kwargs: Additional detection fields

        Returns:
            Created Detection instance
        """
        return self.create(
            analysis_id=analysis_id,
            class_id=class_id,
            class_name=class_name,
            confidence=confidence,
            risk_level=risk_level,
            **kwargs
        )

    def validate_detection(
        self,
        detection_id: UUID,
        validated_by: UUID,
        validation_status: str,
        validation_notes: Optional[str] = None
    ) -> Detection:
        """
        Validate a detection.

        Args:
            detection_id: Detection UUID
            validated_by: Validator's user UUID
            validation_status: Status (validated, rejected, uncertain)
            validation_notes: Optional notes

        Returns:
            Updated Detection instance
        """
        return self.update_or_404(
            detection_id,
            validated_by=validated_by,
            validation_status=validation_status,
            validation_notes=validation_notes,
            validated_at=datetime.now(timezone.utc)
        )

    def set_temporal_validity(
        self,
        detection_id: UUID,
        validity_period_days: int,
        persistence_type: str,
        is_weather_dependent: bool = False
    ) -> Detection:
        """
        Set temporal validity for a detection.

        Args:
            detection_id: Detection UUID
            validity_period_days: Validity period in days
            persistence_type: Type (TRANSIENT, SHORT_TERM, etc.)
            is_weather_dependent: If validity depends on weather

        Returns:
            Updated Detection instance
        """
        expires_at = datetime.now(timezone.utc) + timedelta(days=validity_period_days)

        return self.update_or_404(
            detection_id,
            validity_period_days=validity_period_days,
            expires_at=expires_at,
            persistence_type=persistence_type,
            is_weather_dependent=is_weather_dependent
        )

    def mark_expiration_alert_sent(self, detection_id: UUID) -> Detection:
        """
        Mark expiration alert as sent.

        Args:
            detection_id: Detection UUID

        Returns:
            Updated Detection instance
        """
        return self.update_or_404(
            detection_id,
            last_expiration_alert_sent=datetime.now(timezone.utc)
        )

    # ============================================
    # Statistics
    # ============================================

    def count_by_analysis(self, analysis_id: UUID) -> int:
        """
        Count detections for an analysis.

        Args:
            analysis_id: Analysis UUID

        Returns:
            Number of detections
        """
        return self.count(analysis_id=analysis_id)

    def count_by_risk_level(self, risk_level: str) -> int:
        """
        Count detections by risk level.

        Args:
            risk_level: Risk level

        Returns:
            Number of detections
        """
        return self.count(risk_level=risk_level)

    def count_pending_validation(self) -> int:
        """
        Count detections pending validation.

        Returns:
            Number of detections pending validation
        """
        return self.count(validation_status="pending", requires_verification=True)

    def get_statistics(self, analysis_id: Optional[UUID] = None) -> dict:
        """
        Get detection statistics.

        Args:
            analysis_id: Optional analysis UUID to filter by

        Returns:
            Dictionary with statistics
        """
        try:
            stmt = select(
                func.count(self.model.id).label("total"),
                func.count(self.model.id).filter(self.model.risk_level == "high").label("high_risk"),
                func.count(self.model.id).filter(self.model.risk_level == "medium").label("medium_risk"),
                func.count(self.model.id).filter(self.model.risk_level == "low").label("low_risk"),
                func.avg(self.model.confidence).label("avg_confidence"),
                func.count(self.model.id).filter(self.model.validation_status == "pending").label("pending_validation"),
                func.count(self.model.id).filter(self.model.validation_status == "validated").label("validated"),
            )

            if analysis_id:
                stmt = stmt.where(self.model.analysis_id == analysis_id)

            result = self.db.execute(stmt).one()

            return {
                "total_detections": result.total or 0,
                "high_risk_count": result.high_risk or 0,
                "medium_risk_count": result.medium_risk or 0,
                "low_risk_count": result.low_risk or 0,
                "avg_confidence": float(result.avg_confidence or 0),
                "pending_validation": result.pending_validation or 0,
                "validated": result.validated or 0
            }
        except Exception as e:
            raise self.RepositoryError(f"Failed to get detection statistics: {e}")
