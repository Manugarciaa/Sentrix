"""
Pydantic schemas for analyses and detections
Esquemas Pydantic para análisis y detecciones
"""

from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from uuid import UUID

from sentrix_shared.data_models import (
    RiskLevelEnum, DetectionRiskEnum, BreedingSiteTypeEnum,
    LocationSourceEnum, ValidationStatusEnum
)


# Request schemas
class AnalysisUploadRequest(BaseModel):
    """Schema for uploading an image for analysis"""
    image_url: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    confidence_threshold: Optional[float] = Field(0.5, ge=0.1, le=1.0)
    include_gps: bool = True

    @field_validator('latitude', 'longitude')
    @classmethod
    def validate_coordinates(cls, v, info):
        """Validate that if one coordinate is provided, both must be provided"""
        values = info.data if hasattr(info, 'data') else {}
        lat = values.get('latitude') if 'latitude' in values else v
        lng = values.get('longitude') if 'longitude' in values else None

        if lat is not None and lng is None:
            raise ValueError('If latitude is provided, longitude must also be provided')
        if lng is not None and lat is None:
            raise ValueError('If longitude is provided, latitude must also be provided')

        return v


# Response schemas
class LocationResponse(BaseModel):
    """GPS location information"""
    has_location: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    coordinates: Optional[str] = None
    altitude_meters: Optional[float] = None
    location_source: Optional[LocationSourceEnum] = None
    google_maps_url: Optional[str] = None
    google_earth_url: Optional[str] = None


class CameraInfoResponse(BaseModel):
    """Camera metadata information"""
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    camera_datetime: Optional[str] = None
    camera_software: Optional[str] = None


class DetectionResponse(BaseModel):
    """Individual detection response"""
    id: UUID
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    confidence: Optional[float] = None
    risk_level: Optional[DetectionRiskEnum] = None
    breeding_site_type: Optional[BreedingSiteTypeEnum] = None

    # Geometry
    polygon: Optional[List[List[float]]] = None
    mask_area: Optional[float] = None
    area_square_pixels: Optional[float] = None

    # Location
    location: Optional[LocationResponse] = None

    # Image metadata
    source_filename: Optional[str] = None
    camera_info: Optional[CameraInfoResponse] = None

    # Validation
    validation_status: ValidationStatusEnum = ValidationStatusEnum.PENDING
    validation_notes: Optional[str] = None
    validated_at: Optional[datetime] = None

    created_at: datetime

    class Config:
        from_attributes = True


class RiskAssessmentResponse(BaseModel):
    """Risk assessment information"""
    level: Optional[RiskLevelEnum] = None
    risk_score: Optional[float] = None
    total_detections: int = 0
    high_risk_count: int = 0
    medium_risk_count: int = 0
    recommendations: List[str] = []


class AnalysisResponse(BaseModel):
    """Complete analysis response"""
    id: UUID
    status: str  # Will be enum later (pending, processing, completed, failed)

    # Image info
    image_url: Optional[str] = None
    image_filename: Optional[str] = None
    processed_image_url: Optional[str] = None
    processed_image_filename: Optional[str] = None
    image_size_bytes: Optional[int] = None

    # GPS and camera info
    location: Optional[LocationResponse] = None
    camera_info: Optional[CameraInfoResponse] = None

    # Processing info
    model_used: Optional[str] = None
    confidence_threshold: Optional[float] = None
    processing_time_ms: Optional[int] = None
    yolo_service_version: Optional[str] = None

    # Results
    risk_assessment: Optional[RiskAssessmentResponse] = None
    detections: List[DetectionResponse] = []

    # Timestamps
    image_taken_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnalysisUploadResponse(BaseModel):
    """Response for successful analysis upload"""
    analysis_id: UUID
    status: str = "pending"
    has_gps_data: bool = False
    camera_detected: Optional[str] = None
    estimated_processing_time: str = "30-60 seconds"
    message: str = "Analysis queued for processing"


# Batch processing schemas
class BatchUploadRequest(BaseModel):
    """Schema for batch image processing"""
    image_urls: List[str] = Field(..., min_items=1, max_items=50)
    confidence_threshold: Optional[float] = Field(0.5, ge=0.1, le=1.0)
    include_gps: bool = True


class BatchUploadResponse(BaseModel):
    """Response for batch upload"""
    batch_id: UUID
    total_images: int
    analyses: List[AnalysisUploadResponse]
    estimated_completion_time: str


# Query schemas
class AnalysisListQuery(BaseModel):
    """Query parameters for listing analyses"""
    user_id: Optional[UUID] = None
    has_gps: Optional[bool] = None
    camera_make: Optional[str] = None
    risk_level: Optional[RiskLevelEnum] = None
    since: Optional[datetime] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

    # Bounding box: sw_lat,sw_lng,ne_lat,ne_lng
    bbox: Optional[str] = Field(None, pattern=r'^-?\d+\.?\d*,-?\d+\.?\d*,-?\d+\.?\d*,-?\d+\.?\d*$')


class AnalysisListResponse(BaseModel):
    """Response for analysis listing"""
    analyses: List[AnalysisResponse]
    total: int
    limit: int
    offset: int
    has_next: bool


# Legacy compatibility schemas
class AnalysisCreate(BaseModel):
    """Schema for creating analysis - legacy compatibility"""
    image_filename: str
    confidence_threshold: Optional[float] = 0.5
    user_id: Optional[UUID] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


# Error schemas
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    error: str = "validation_error"
    message: str
    field_errors: List[Dict[str, str]] = []


# Health check schema
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str]
    uptime_seconds: float