# -*- coding: utf-8 -*-
"""
Detection Validity Management Endpoints
Endpoints de Gestión de Validez de Detecciones

Provides endpoints for managing temporal validity of detections:
- Get expired detections
- Get detections expiring soon
- Extend detection validity
- Re-validate expired detections
- Get validity statistics
"""

import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from ...utils.auth import get_current_user, get_current_active_user
from ...database.models.models import UserProfile
from ...utils.supabase_client import get_supabase_client

try:
    from ...utils.temporal_validity import (
        get_detection_validity_status,
        extend_detection_validity,
        enrich_detection_with_validity
    )
    TEMPORAL_VALIDITY_AVAILABLE = True
except ImportError:
    TEMPORAL_VALIDITY_AVAILABLE = False

router = APIRouter()


# Response models
class ValidityStatus(BaseModel):
    """Validity status for a detection"""
    is_expired: bool
    is_expiring_soon: bool
    remaining_days: Optional[int]
    status: str  # VALID, MEDIUM_VALIDITY, LOW_VALIDITY, EXPIRING_SOON, EXPIRED
    validity_percentage: int
    requires_revalidation: bool


class DetectionWithValidity(BaseModel):
    """Detection with validity information"""
    id: str
    analysis_id: str
    class_name: str
    confidence: float
    risk_level: str
    breeding_site_type: str
    persistence_type: Optional[str]
    validity_period_days: Optional[int]
    expires_at: Optional[str]
    is_weather_dependent: bool
    validity_status: Optional[ValidityStatus]
    created_at: str


class ValidityExtensionRequest(BaseModel):
    """Request to extend detection validity"""
    detection_id: str = Field(..., description="ID of the detection to extend")
    extension_days: int = Field(..., ge=1, le=365, description="Number of days to extend (1-365)")
    reason: str = Field(..., max_length=500, description="Reason for extension")


class ValidityExtensionResponse(BaseModel):
    """Response after extending validity"""
    detection_id: str
    old_expires_at: str
    new_expires_at: str
    extension_days: int
    extended_by: str
    extended_at: str
    reason: str


class ValidityStatistics(BaseModel):
    """Statistics about detection validity"""
    total_detections: int
    active_detections: int
    expired_detections: int
    expiring_soon_detections: int
    by_persistence_type: dict
    by_breeding_site: dict
    average_validity_days: float
    revalidation_needed: int


# Endpoints

@router.get("/detections/expired", response_model=List[DetectionWithValidity])
async def get_expired_detections(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    breeding_site_type: Optional[str] = None,
    current_user: UserProfile = Depends(get_current_active_user)
):
    """
    Get all expired detections that need revalidation
    Obtener todas las detecciones expiradas que necesitan revalidación

    Args:
        limit: Maximum number of results
        offset: Pagination offset
        breeding_site_type: Filter by breeding site type

    Returns:
        List of expired detections with validity information
    """
    if not TEMPORAL_VALIDITY_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="Temporal validity feature not available"
        )

    try:
        client = get_supabase_client()

        # Query expired detections
        query = client.table('detections').select('*').not_.is_('expires_at', 'null').lte('expires_at', datetime.now().isoformat())

        # Apply filters
        if breeding_site_type:
            query = query.eq('breeding_site_type', breeding_site_type)

        # Execute with pagination
        result = query.range(offset, offset + limit - 1).order('expires_at', desc=False).execute()

        # Enrich with validity status
        detections = []
        for detection in result.data:
            validity_status = None
            if detection.get('expires_at'):
                validity_status = get_detection_validity_status(detection['expires_at'])

            detections.append(DetectionWithValidity(
                id=detection['id'],
                analysis_id=detection['analysis_id'],
                class_name=detection.get('class_name', 'Unknown'),
                confidence=float(detection.get('confidence', 0.0)),
                risk_level=detection.get('risk_level', 'BAJO'),
                breeding_site_type=detection.get('breeding_site_type', 'UNKNOWN'),
                persistence_type=detection.get('persistence_type'),
                validity_period_days=detection.get('validity_period_days'),
                expires_at=detection.get('expires_at'),
                is_weather_dependent=detection.get('is_weather_dependent', False),
                validity_status=ValidityStatus(**validity_status) if validity_status else None,
                created_at=detection.get('created_at', datetime.now().isoformat())
            ))

        return detections

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching expired detections: {str(e)}"
        )


@router.get("/detections/expiring-soon", response_model=List[DetectionWithValidity])
async def get_expiring_soon_detections(
    days_threshold: int = Query(1, ge=1, le=30, description="Days threshold for 'expiring soon'"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: UserProfile = Depends(get_current_active_user)
):
    """
    Get detections expiring soon (within specified days)
    Obtener detecciones que están por expirar pronto

    Args:
        days_threshold: Consider detections expiring within this many days
        limit: Maximum number of results
        offset: Pagination offset

    Returns:
        List of detections expiring soon
    """
    if not TEMPORAL_VALIDITY_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="Temporal validity feature not available"
        )

    try:
        client = get_supabase_client()

        # Use the expiring_soon_detections view if available, otherwise query directly
        try:
            # Try using the view first
            result = client.table('expiring_soon_detections').select('*').range(offset, offset + limit - 1).execute()
        except Exception:
            # Fallback to direct query
            from datetime import timedelta
            now = datetime.now()
            threshold = (now + timedelta(days=days_threshold)).isoformat()

            result = client.table('detections').select('*').not_.is_('expires_at', 'null').gt('expires_at', now.isoformat()).lte('expires_at', threshold).range(offset, offset + limit - 1).order('expires_at', desc=False).execute()

        # Enrich with validity status
        detections = []
        for detection in result.data:
            validity_status = None
            if detection.get('expires_at'):
                validity_status = get_detection_validity_status(detection['expires_at'])

            detections.append(DetectionWithValidity(
                id=detection['id'],
                analysis_id=detection['analysis_id'],
                class_name=detection.get('class_name', 'Unknown'),
                confidence=float(detection.get('confidence', 0.0)),
                risk_level=detection.get('risk_level', 'BAJO'),
                breeding_site_type=detection.get('breeding_site_type', 'UNKNOWN'),
                persistence_type=detection.get('persistence_type'),
                validity_period_days=detection.get('validity_period_days'),
                expires_at=detection.get('expires_at'),
                is_weather_dependent=detection.get('is_weather_dependent', False),
                validity_status=ValidityStatus(**validity_status) if validity_status else None,
                created_at=detection.get('created_at', datetime.now().isoformat())
            ))

        return detections

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching expiring detections: {str(e)}"
        )


@router.post("/detections/extend-validity", response_model=ValidityExtensionResponse)
async def extend_validity(
    request: ValidityExtensionRequest,
    current_user: UserProfile = Depends(get_current_active_user)
):
    """
    Extend validity period for a specific detection
    Extender período de validez para una detección específica

    Requires EXPERT or ADMIN role.

    Args:
        request: Extension request with detection_id, extension_days, and reason

    Returns:
        Updated validity information
    """
    if not TEMPORAL_VALIDITY_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="Temporal validity feature not available"
        )

    # Check user has permission (EXPERT or ADMIN)
    if current_user.role not in ['EXPERT', 'ADMIN']:
        raise HTTPException(
            status_code=403,
            detail="Only experts and admins can extend detection validity"
        )

    try:
        client = get_supabase_client()

        # Get current detection
        result = client.table('detections').select('*').eq('id', request.detection_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Detection not found")

        detection = result.data[0]
        current_expires_at = detection.get('expires_at')

        if not current_expires_at:
            raise HTTPException(
                status_code=400,
                detail="Detection does not have an expiration date set"
            )

        # Calculate new expiration
        extension_result = extend_detection_validity(
            current_expires_at=current_expires_at,
            extension_days=request.extension_days,
            reason=request.reason
        )

        if 'error' in extension_result:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to calculate extension: {extension_result['error']}"
            )

        # Update detection in database
        update_data = {
            'expires_at': extension_result['expires_at'],
            'validity_period_days': detection.get('validity_period_days', 0) + request.extension_days,
        }

        update_result = client.table('detections').update(update_data).eq('id', request.detection_id).execute()

        if not update_result.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to update detection in database"
            )

        return ValidityExtensionResponse(
            detection_id=request.detection_id,
            old_expires_at=current_expires_at,
            new_expires_at=extension_result['expires_at'],
            extension_days=request.extension_days,
            extended_by=current_user.email,
            extended_at=datetime.now().isoformat(),
            reason=request.reason
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extending validity: {str(e)}"
        )


@router.post("/detections/{detection_id}/revalidate")
async def revalidate_detection(
    detection_id: str,
    weather_condition: Optional[str] = None,
    current_user: UserProfile = Depends(get_current_active_user)
):
    """
    Re-validate an expired detection and recalculate validity
    Revalidar una detección expirada y recalcular validez

    Requires EXPERT or ADMIN role.

    Args:
        detection_id: ID of the detection to revalidate
        weather_condition: Optional current weather condition

    Returns:
        Updated detection with new validity
    """
    if not TEMPORAL_VALIDITY_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="Temporal validity feature not available"
        )

    # Check user has permission
    if current_user.role not in ['EXPERT', 'ADMIN']:
        raise HTTPException(
            status_code=403,
            detail="Only experts and admins can revalidate detections"
        )

    try:
        client = get_supabase_client()

        # Get detection
        result = client.table('detections').select('*').eq('id', detection_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Detection not found")

        detection = result.data[0]

        # Mark as validated by expert
        detection['validation_status'] = 'validated'
        detection['validated_by'] = str(current_user.id)
        detection['validated_at'] = datetime.now().isoformat()

        # Recalculate validity with expert validation bonus
        enriched_detection = enrich_detection_with_validity(
            detection_data=detection,
            is_validated=True,
            weather_condition=weather_condition
        )

        # Update in database
        update_data = {
            'validation_status': 'validated',
            'validated_by': str(current_user.id),
            'validated_at': datetime.now().isoformat(),
            'validity_period_days': enriched_detection['validity_period_days'],
            'expires_at': enriched_detection['expires_at'],
            'is_weather_dependent': enriched_detection['is_weather_dependent'],
            'persistence_type': enriched_detection['persistence_type'],
        }

        update_result = client.table('detections').update(update_data).eq('id', detection_id).execute()

        if not update_result.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to update detection"
            )

        # Get validity status
        validity_status = get_detection_validity_status(enriched_detection['expires_at'])

        return {
            "detection_id": detection_id,
            "status": "revalidated",
            "validated_by": current_user.email,
            "validated_at": update_data['validated_at'],
            "validity_period_days": enriched_detection['validity_period_days'],
            "expires_at": enriched_detection['expires_at'],
            "validity_status": validity_status
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error revalidating detection: {str(e)}"
        )


@router.get("/detections/validity-stats", response_model=ValidityStatistics)
async def get_validity_statistics(
    current_user: UserProfile = Depends(get_current_active_user)
):
    """
    Get statistics about detection validity across the system
    Obtener estadísticas sobre validez de detecciones en el sistema

    Returns:
        Comprehensive validity statistics
    """
    if not TEMPORAL_VALIDITY_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="Temporal validity feature not available"
        )

    try:
        client = get_supabase_client()
        now = datetime.now().isoformat()

        # Get all detections
        all_detections = client.table('detections').select('*').execute()
        total = len(all_detections.data)

        if total == 0:
            return ValidityStatistics(
                total_detections=0,
                active_detections=0,
                expired_detections=0,
                expiring_soon_detections=0,
                by_persistence_type={},
                by_breeding_site={},
                average_validity_days=0.0,
                revalidation_needed=0
            )

        # Count by status
        active = 0
        expired = 0
        expiring_soon = 0
        by_persistence = {}
        by_breeding_site = {}
        total_validity_days = 0
        validity_count = 0

        for detection in all_detections.data:
            expires_at = detection.get('expires_at')

            # Count persistence types
            persistence_type = detection.get('persistence_type', 'UNKNOWN')
            by_persistence[persistence_type] = by_persistence.get(persistence_type, 0) + 1

            # Count breeding sites
            breeding_site = detection.get('breeding_site_type', 'UNKNOWN')
            by_breeding_site[breeding_site] = by_breeding_site.get(breeding_site, 0) + 1

            # Calculate average validity
            validity_days = detection.get('validity_period_days')
            if validity_days:
                total_validity_days += validity_days
                validity_count += 1

            # Determine status
            if not expires_at:
                active += 1
            else:
                validity_status = get_detection_validity_status(expires_at)
                if validity_status['is_expired']:
                    expired += 1
                elif validity_status['is_expiring_soon']:
                    expiring_soon += 1
                else:
                    active += 1

        average_validity = total_validity_days / validity_count if validity_count > 0 else 0.0

        return ValidityStatistics(
            total_detections=total,
            active_detections=active,
            expired_detections=expired,
            expiring_soon_detections=expiring_soon,
            by_persistence_type=by_persistence,
            by_breeding_site=by_breeding_site,
            average_validity_days=round(average_validity, 1),
            revalidation_needed=expired + expiring_soon
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching validity statistics: {str(e)}"
        )


@router.get("/detections/{detection_id}/validity", response_model=ValidityStatus)
async def get_detection_validity(
    detection_id: str,
    current_user: UserProfile = Depends(get_current_active_user)
):
    """
    Get current validity status for a specific detection
    Obtener estado actual de validez para una detección específica

    Args:
        detection_id: ID of the detection

    Returns:
        Current validity status
    """
    if not TEMPORAL_VALIDITY_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="Temporal validity feature not available"
        )

    try:
        client = get_supabase_client()

        result = client.table('detections').select('expires_at').eq('id', detection_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Detection not found")

        expires_at = result.data[0].get('expires_at')

        if not expires_at:
            # No expiration set - always valid
            return ValidityStatus(
                is_expired=False,
                is_expiring_soon=False,
                remaining_days=None,
                status="VALID",
                validity_percentage=100,
                requires_revalidation=False
            )

        validity_status = get_detection_validity_status(expires_at)
        return ValidityStatus(**validity_status)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching detection validity: {str(e)}"
        )
