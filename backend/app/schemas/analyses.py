"""
Analysis schemas for API endpoints
Esquemas de análisis para endpoints de API
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

# Base Location Schema
class LocationData(BaseModel):
    """Location data schema"""
    has_location: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    coordinates: Optional[str] = None
    altitude_meters: Optional[float] = None
    location_source: Optional[str] = None
    google_maps_url: Optional[str] = None
    google_earth_url: Optional[str] = None

# Base Camera Schema
class CameraInfo(BaseModel):
    """Camera information schema"""
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    camera_datetime: Optional[str] = None
    camera_software: Optional[str] = None

# Risk Assessment Schema
class RiskAssessment(BaseModel):
    """Risk assessment schema"""
    level: str
    risk_score: Optional[float] = None
    total_detections: int
    high_risk_count: Optional[int] = 0
    medium_risk_count: Optional[int] = 0
    low_risk_count: Optional[int] = 0
    recommendations: Optional[List[str]] = []

# Detection Schema
class DetectionData(BaseModel):
    """Detection data schema"""
    id: uuid.UUID
    class_id: int
    class_name: str
    confidence: float
    risk_level: str
    breeding_site_type: str
    polygon: List[List[float]]
    mask_area: float
    area_square_pixels: Optional[float] = None
    location: Optional[LocationData] = None
    source_filename: Optional[str] = None
    camera_info: Optional[CameraInfo] = None
    validation_status: str = "pending"
    validation_notes: Optional[str] = None
    validated_at: Optional[datetime] = None
    created_at: datetime

# Analysis Request Schemas
class AnalysisUploadRequest(BaseModel):
    """Schema for analysis upload request"""
    image_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    confidence_threshold: float = Field(default=0.5, ge=0.1, le=1.0)
    include_gps: bool = True

class BatchUploadRequest(BaseModel):
    """Schema for batch analysis request"""
    image_urls: List[str] = Field(..., min_items=1, max_items=50)
    confidence_threshold: float = Field(default=0.5, ge=0.1, le=1.0)
    include_gps: bool = True

# Analysis Response Schemas
class AnalysisUploadResponse(BaseModel):
    """Schema for analysis upload response"""
    analysis_id: uuid.UUID
    status: str
    has_gps_data: bool
    camera_detected: Optional[str] = None
    estimated_processing_time: Optional[str] = None
    message: str

class AnalysisResponse(BaseModel):
    """Schema for complete analysis response"""
    id: uuid.UUID
    status: str
    image_filename: str
    image_size_bytes: Optional[int] = None

    # Location data
    location: Optional[LocationData] = None

    # Camera information
    camera_info: Optional[CameraInfo] = None

    # Processing information
    model_used: Optional[str] = None
    confidence_threshold: Optional[float] = None
    processing_time_ms: Optional[int] = None
    yolo_service_version: Optional[str] = None

    # Risk assessment
    risk_assessment: Optional[RiskAssessment] = None

    # Detections
    detections: List[DetectionData] = []

    # Timestamps
    image_taken_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class AnalysisListQuery(BaseModel):
    """Schema for analysis list query parameters"""
    user_id: Optional[str] = None
    has_gps: Optional[bool] = None
    camera_make: Optional[str] = None
    risk_level: Optional[str] = None
    since: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    bbox: Optional[str] = None

class AnalysisListResponse(BaseModel):
    """Schema for analysis list response"""
    analyses: List[AnalysisResponse]
    total: int
    limit: int
    offset: int
    has_next: bool

class BatchUploadResponse(BaseModel):
    """Schema for batch upload response"""
    batch_id: uuid.UUID
    total_images: int
    analyses: List[AnalysisUploadResponse]
    estimated_completion_time: str

# Legacy compatibility schemas
class AnalysisCreate(BaseModel):
    """Legacy schema for creating analysis"""
    image_filename: str
    confidence_threshold: float = 0.5

class DetectionResponse(BaseModel):
    """Legacy schema for detection response"""
    id: int
    analysis_id: int
    class_id: int
    class_name: str
    confidence: float
    risk_level: str
    has_location: bool
    detection_latitude: Optional[float] = None
    detection_longitude: Optional[float] = None

# Error Schemas
class ErrorResponse(BaseModel):
    """Standard error response schema"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ValidationErrorResponse(BaseModel):
    """Validation error response schema"""
    error: str = "validation_error"
    message: str
    field_errors: List[Dict[str, str]] = []

# Health Check Schema
class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str]
    uptime_seconds: float