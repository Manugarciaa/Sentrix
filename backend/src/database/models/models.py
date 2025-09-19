from sqlalchemy import (
    Column, String, Integer, DateTime, Boolean, Text, DECIMAL,
    ForeignKey, ARRAY, JSON as JSONB, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from geoalchemy2.types import Geometry

from .base import Base
from .enums import (
    risk_level_enum, detection_risk_enum, breeding_site_type_enum,
    user_role_enum, location_source_enum, validation_status_enum
)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True)
    role = Column(user_role_enum, default="user")
    display_name = Column(Text)
    organization = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    analyses = relationship("Analysis", back_populates="user")
    validated_detections = relationship("Detection", back_populates="validator")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"))
    image_url = Column(Text, nullable=False)
    image_filename = Column(Text)
    image_size_bytes = Column(Integer)

    # Geolocalización
    location = Column(Geography(geometry_type="POINT", srid=4326))
    has_gps_data = Column(Boolean, default=False)
    gps_altitude_meters = Column(DECIMAL(8, 2))
    gps_date = Column(Text)
    gps_timestamp = Column(Text)
    location_source = Column(location_source_enum)

    # Metadata de cámara
    camera_make = Column(Text)
    camera_model = Column(Text)
    camera_datetime = Column(Text)
    camera_software = Column(Text)

    # URLs de verificación
    google_maps_url = Column(Text)
    google_earth_url = Column(Text)

    # Contadores de detecciones
    total_detections = Column(Integer, default=0)
    high_risk_count = Column(Integer, default=0)
    medium_risk_count = Column(Integer, default=0)
    risk_level = Column(risk_level_enum)
    risk_score = Column(DECIMAL(4, 3))
    recommendations = Column(ARRAY(Text))

    # Configuración de procesamiento
    model_used = Column(Text)
    confidence_threshold = Column(DECIMAL(3, 2))
    processing_time_ms = Column(Integer)
    yolo_service_version = Column(Text)

    # Timestamps
    image_taken_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("UserProfile", back_populates="analyses")
    detections = relationship("Detection", back_populates="analysis", cascade="all, delete-orphan")


class Detection(Base):
    __tablename__ = "detections"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id", ondelete="CASCADE"))

    # Información básica de detección
    class_id = Column(Integer)
    class_name = Column(Text)
    confidence = Column(DECIMAL(5, 4))
    risk_level = Column(detection_risk_enum)

    # Geometría (polígono de segmentación)
    polygon = Column(JSONB)
    mask_area = Column(DECIMAL(12, 2))

    # Geolocalización específica de esta detección
    location = Column(Geography(geometry_type="POINT", srid=4326))
    has_location = Column(Boolean, default=False)
    detection_latitude = Column(DECIMAL(10, 8))
    detection_longitude = Column(DECIMAL(11, 8))
    detection_altitude_meters = Column(DECIMAL(8, 2))

    # URLs de verificación específicas
    google_maps_url = Column(Text)
    google_earth_url = Column(Text)

    # Metadata para backend integration
    breeding_site_type = Column(breeding_site_type_enum)  # Usar enum específico
    area_square_pixels = Column(DECIMAL(12, 2))
    requires_verification = Column(Boolean, default=True)

    # Información de imagen fuente
    source_filename = Column(Text)
    camera_make = Column(Text)
    camera_model = Column(Text)
    image_datetime = Column(Text)

    # Validación por expertos
    validated_by = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"))
    validation_status = Column(validation_status_enum, default="pending")
    validation_notes = Column(Text)
    validated_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    analysis = relationship("Analysis", back_populates="detections")
    validator = relationship("UserProfile", back_populates="validated_detections")