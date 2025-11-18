"""
Tests unitarios para modelos de base de datos y enums del backend Sentrix
Verifica que los modelos SQLAlchemy y enums funcionen correctamente
"""

import pytest

pytestmark = pytest.mark.database
import uuid
from datetime import datetime
from sqlalchemy.exc import IntegrityError

try:
    from geoalchemy2.shape import to_shape, from_shape
    from shapely.geometry import Point
    HAS_POSTGIS = True
except ImportError:
    HAS_POSTGIS = False
    # Mock for testing without PostGIS
    def to_shape(geom):
        return None
    def from_shape(shape, srid=None):
        return None
    class Point:
        def __init__(self, x, y):
            self.x, self.y = x, y

from src.database.models.models import UserProfile, Analysis, Detection
from sentrix_shared.data_models import (
    RiskLevelEnum, DetectionRiskEnum, BreedingSiteTypeEnum,
    UserRoleEnum, LocationSourceEnum, ValidationStatusEnum
)


class TestEnums:
    """Tests para todos los enums y sus valores"""

    def test_risk_level_enum(self):
        """Test que los valores de RiskLevelEnum son correctos"""
        # RiskLevelEnum is an alias for DetectionRiskEnum (Spanish values)
        assert RiskLevelEnum.MINIMO.value == "MINIMO"
        assert RiskLevelEnum.BAJO.value == "BAJO"
        assert RiskLevelEnum.MEDIO.value == "MEDIO"
        assert RiskLevelEnum.ALTO.value == "ALTO"

    def test_detection_risk_enum(self):
        """Test que DetectionRiskEnum coincide con el servicio YOLO"""
        assert DetectionRiskEnum.BAJO.value == "BAJO"
        assert DetectionRiskEnum.MEDIO.value == "MEDIO"
        assert DetectionRiskEnum.ALTO.value == "ALTO"

    def test_breeding_site_type_enum(self):
        """Test que BreedingSiteTypeEnum coincide con las clases YOLO"""
        assert BreedingSiteTypeEnum.BASURA.value == "Basura"
        assert BreedingSiteTypeEnum.CALLES_MAL_HECHAS.value == "Calles mal hechas"
        assert BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA.value == "Charcos/Cumulo de agua"
        assert BreedingSiteTypeEnum.HUECOS.value == "Huecos"

    def test_user_role_enum(self):
        """Test que los valores de UserRoleEnum son correctos"""
        assert UserRoleEnum.ADMIN.value == "admin"
        assert UserRoleEnum.EXPERT.value == "expert"
        assert UserRoleEnum.USER.value == "user"

    def test_location_source_enum(self):
        """Test que los valores de LocationSourceEnum son correctos"""
        assert LocationSourceEnum.EXIF_GPS.value == "EXIF_GPS"
        assert LocationSourceEnum.MANUAL.value == "MANUAL"
        assert LocationSourceEnum.ESTIMATED.value == "ESTIMATED"

    def test_validation_status_enum(self):
        """Test que los valores de ValidationStatusEnum son correctos"""
        assert ValidationStatusEnum.PENDING.value == "pending"
        assert ValidationStatusEnum.PENDING_VALIDATION.value == "pending_validation"
        assert ValidationStatusEnum.VALIDATED_POSITIVE.value == "validated_positive"
        assert ValidationStatusEnum.VALIDATED_NEGATIVE.value == "validated_negative"
        assert ValidationStatusEnum.REQUIRES_REVIEW.value == "requires_review"


class TestUserProfileModel:
    """Tests para el modelo UserProfile"""

    def test_create_user_profile(self, db_session):
        """Test que se puede crear un perfil de usuario"""
        user_id = uuid.uuid4()

        user_profile = UserProfile(
            id=user_id,
            role=UserRoleEnum.USER,
            display_name="Test User",
            organization="Test Organization"
        )

        db_session.add(user_profile)
        db_session.commit()

        # Retrieve and verify
        retrieved = db_session.query(UserProfile).filter_by(id=user_id).first()
        assert retrieved is not None
        assert retrieved.display_name == "Test User"
        assert retrieved.role == UserRoleEnum.USER
        assert retrieved.organization == "Test Organization"
        assert retrieved.created_at is not None

    def test_user_profile_defaults(self, db_session):
        """Test user profile default values"""
        user_id = uuid.uuid4()

        user_profile = UserProfile(id=user_id)
        db_session.add(user_profile)
        db_session.commit()

        retrieved = db_session.query(UserProfile).filter_by(id=user_id).first()
        assert retrieved.role == UserRoleEnum.USER  # Default role
        assert retrieved.display_name is None
        assert retrieved.organization is None


class TestAnalysisModel:
    """Test Analysis model"""

    def test_create_analysis_basic(self, db_session):
        """Test creating a basic analysis"""
        user_id = uuid.uuid4()
        user_profile = UserProfile(id=user_id, role=UserRoleEnum.USER)
        db_session.add(user_profile)
        db_session.flush()

        analysis = Analysis(
            user_id=user_id,
            image_url="https://example.com/test.jpg",
            image_filename="test.jpg",
            image_size_bytes=1024000
        )

        db_session.add(analysis)
        db_session.commit()

        # Verify
        retrieved = db_session.query(Analysis).filter_by(user_id=user_id).first()
        assert retrieved is not None
        assert retrieved.image_url == "https://example.com/test.jpg"
        assert retrieved.image_filename == "test.jpg"
        assert retrieved.image_size_bytes == 1024000
        assert retrieved.has_gps_data is False  # Default
        assert retrieved.total_detections == 0  # Default

    @pytest.mark.skipif(not HAS_POSTGIS, reason="PostGIS not available")
    def test_analysis_with_gps(self, db_session):
        """Test analysis with GPS data"""
        user_id = uuid.uuid4()
        user_profile = UserProfile(id=user_id)
        db_session.add(user_profile)
        db_session.flush()

        # Create point geometry for GPS location
        point = Point(-65.195539, -26.831314)  # longitude, latitude

        analysis = Analysis(
            user_id=user_id,
            image_url="https://example.com/gps_test.jpg",
            has_gps_data=True,
            location=from_shape(point, srid=4326),
            gps_altitude_meters=458.2,
            location_source=LocationSourceEnum.EXIF_GPS,
            google_maps_url="https://maps.google.com/?q=-26.831314,-65.195539"
        )

        db_session.add(analysis)
        db_session.commit()

        # Verify GPS data
        retrieved = db_session.query(Analysis).filter_by(user_id=user_id).first()
        assert retrieved.has_gps_data is True
        assert retrieved.location_source == LocationSourceEnum.EXIF_GPS
        assert retrieved.gps_altitude_meters == 458.2

        # Verify geometry
        if retrieved.location:
            shape = to_shape(retrieved.location)
            assert abs(shape.x - (-65.195539)) < 0.000001  # longitude
            assert abs(shape.y - (-26.831314)) < 0.000001  # latitude

    def test_analysis_camera_metadata(self, db_session):
        """Test analysis with camera metadata"""
        user_id = uuid.uuid4()
        user_profile = UserProfile(id=user_id)
        db_session.add(user_profile)
        db_session.flush()

        analysis = Analysis(
            user_id=user_id,
            image_url="https://example.com/camera_test.jpg",
            camera_make="Xiaomi",
            camera_model="220333QL",
            camera_datetime="2025:09:19 15:19:08",
            camera_software="MIUI Camera"
        )

        db_session.add(analysis)
        db_session.commit()

        retrieved = db_session.query(Analysis).filter_by(user_id=user_id).first()
        assert retrieved.camera_make == "Xiaomi"
        assert retrieved.camera_model == "220333QL"
        assert retrieved.camera_datetime == "2025:09:19 15:19:08"
        assert retrieved.camera_software == "MIUI Camera"

    def test_analysis_risk_assessment(self, db_session):
        """Test analysis with risk assessment data"""
        user_id = uuid.uuid4()
        user_profile = UserProfile(id=user_id)
        db_session.add(user_profile)
        db_session.flush()

        analysis = Analysis(
            user_id=user_id,
            image_url="https://example.com/risk_test.jpg",
            total_detections=3,
            high_risk_count=1,
            medium_risk_count=2,
            risk_level=RiskLevelEnum.MEDIUM,
            risk_score=0.75,
            recommendations=["Eliminar desechos", "Monitoreo regular"]
        )

        db_session.add(analysis)
        db_session.commit()

        retrieved = db_session.query(Analysis).filter_by(user_id=user_id).first()
        assert retrieved.total_detections == 3
        assert retrieved.high_risk_count == 1
        assert retrieved.medium_risk_count == 2
        assert retrieved.risk_level == RiskLevelEnum.MEDIUM
        assert retrieved.risk_score == 0.75
        assert "Eliminar desechos" in retrieved.recommendations
        assert "Monitoreo regular" in retrieved.recommendations


class TestDetectionModel:
    """Test Detection model"""

    def test_create_detection_basic(self, db_session):
        """Test creating a basic detection"""
        # Create user and analysis first
        user_id = uuid.uuid4()
        user_profile = UserProfile(id=user_id)
        db_session.add(user_profile)
        db_session.flush()

        analysis = Analysis(
            user_id=user_id,
            image_url="https://example.com/detection_test.jpg"
        )
        db_session.add(analysis)
        db_session.flush()

        # Create detection
        detection = Detection(
            analysis_id=analysis.id,
            class_id=0,
            class_name="Basura",
            confidence=0.75,
            risk_level=DetectionRiskEnum.MEDIO,
            breeding_site_type=BreedingSiteTypeEnum.BASURA,
            polygon=[[100, 100], [200, 100], [200, 200], [100, 200]],
            mask_area=10000.0
        )

        db_session.add(detection)
        db_session.commit()

        # Verify
        retrieved = db_session.query(Detection).filter_by(analysis_id=analysis.id).first()
        assert retrieved is not None
        assert retrieved.class_id == 0
        assert retrieved.class_name == "Basura"
        assert retrieved.confidence == 0.75
        assert retrieved.risk_level == DetectionRiskEnum.MEDIO
        assert retrieved.breeding_site_type == BreedingSiteTypeEnum.BASURA
        assert retrieved.mask_area == 10000.0
        assert retrieved.validation_status == ValidationStatusEnum.PENDING  # Default

    @pytest.mark.skipif(not HAS_POSTGIS, reason="PostGIS not available")
    def test_detection_with_gps(self, db_session):
        """Test detection with GPS coordinates"""
        # Setup analysis
        user_id = uuid.uuid4()
        user_profile = UserProfile(id=user_id)
        analysis = Analysis(user_id=user_id, image_url="test.jpg")
        db_session.add_all([user_profile, analysis])
        db_session.flush()

        # Create point for detection location
        point = Point(-65.195539, -26.831314)

        detection = Detection(
            analysis_id=analysis.id,
            class_id=2,
            class_name="Charcos/Cumulo de agua",
            confidence=0.85,
            risk_level=DetectionRiskEnum.ALTO,
            breeding_site_type=BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA,
            has_location=True,
            location=from_shape(point, srid=4326),
            detection_latitude=-26.831314,
            detection_longitude=-65.195539,
            detection_altitude_meters=458.2,
            google_maps_url="https://maps.google.com/?q=-26.831314,-65.195539"
        )

        db_session.add(detection)
        db_session.commit()

        # Verify GPS data
        retrieved = db_session.query(Detection).filter_by(analysis_id=analysis.id).first()
        assert retrieved.has_location is True
        assert retrieved.detection_latitude == -26.831314
        assert retrieved.detection_longitude == -65.195539
        assert retrieved.detection_altitude_meters == 458.2
        assert "maps.google.com" in retrieved.google_maps_url

    def test_detection_validation(self, db_session):
        """Test detection validation workflow"""
        # Setup analysis and expert user
        user_id = uuid.uuid4()
        expert_id = uuid.uuid4()

        user_profile = UserProfile(id=user_id)
        expert_profile = UserProfile(id=expert_id, role=UserRoleEnum.EXPERT)
        analysis = Analysis(user_id=user_id, image_url="test.jpg")

        db_session.add_all([user_profile, expert_profile, analysis])
        db_session.flush()

        detection = Detection(
            analysis_id=analysis.id,
            class_name="Huecos",
            breeding_site_type=BreedingSiteTypeEnum.HUECOS,
            confidence=0.90
        )
        db_session.add(detection)
        db_session.flush()

        # Validate detection
        detection.validated_by = expert_id
        detection.validation_status = ValidationStatusEnum.VALIDATED_POSITIVE
        detection.validation_notes = "Confirmed by expert review"
        detection.validated_at = datetime.utcnow()

        db_session.commit()

        # Verify validation
        retrieved = db_session.query(Detection).filter_by(analysis_id=analysis.id).first()
        assert retrieved.validated_by == expert_id
        assert retrieved.validation_status == ValidationStatusEnum.VALIDATED_POSITIVE
        assert retrieved.validation_notes == "Confirmed by expert review"
        assert retrieved.validated_at is not None

    def test_detection_cascade_delete(self, db_session):
        """Test that detections are deleted when analysis is deleted"""
        # Setup
        user_id = uuid.uuid4()
        user_profile = UserProfile(id=user_id)
        analysis = Analysis(user_id=user_id, image_url="test.jpg")
        db_session.add_all([user_profile, analysis])
        db_session.flush()

        # Create multiple detections
        detections = [
            Detection(analysis_id=analysis.id, class_name="Basura"),
            Detection(analysis_id=analysis.id, class_name="Huecos")
        ]
        db_session.add_all(detections)
        db_session.commit()

        # Verify detections exist
        count_before = db_session.query(Detection).filter_by(analysis_id=analysis.id).count()
        assert count_before == 2

        # Delete analysis
        db_session.delete(analysis)
        db_session.commit()

        # Verify detections are cascade deleted
        count_after = db_session.query(Detection).filter_by(analysis_id=analysis.id).count()
        assert count_after == 0


class TestModelRelationships:
    """Test relationships between models"""

    def test_user_analysis_relationship(self, db_session):
        """Test User -> Analysis relationship"""
        user_id = uuid.uuid4()
        user_profile = UserProfile(id=user_id, display_name="Test User")

        # Create multiple analyses for user
        analyses = [
            Analysis(user_id=user_id, image_url="image1.jpg"),
            Analysis(user_id=user_id, image_url="image2.jpg")
        ]

        db_session.add(user_profile)
        db_session.add_all(analyses)
        db_session.commit()

        # Test relationship
        retrieved_user = db_session.query(UserProfile).filter_by(id=user_id).first()
        assert len(retrieved_user.analyses) == 2
        assert retrieved_user.analyses[0].image_url in ["image1.jpg", "image2.jpg"]

    def test_analysis_detection_relationship(self, db_session):
        """Test Analysis -> Detection relationship"""
        # Setup
        user_id = uuid.uuid4()
        user_profile = UserProfile(id=user_id)
        analysis = Analysis(user_id=user_id, image_url="test.jpg")
        db_session.add_all([user_profile, analysis])
        db_session.flush()

        # Create multiple detections
        detections = [
            Detection(analysis_id=analysis.id, class_name="Basura", confidence=0.7),
            Detection(analysis_id=analysis.id, class_name="Huecos", confidence=0.8)
        ]
        db_session.add_all(detections)
        db_session.commit()

        # Test relationship
        retrieved_analysis = db_session.query(Analysis).filter_by(id=analysis.id).first()
        assert len(retrieved_analysis.detections) == 2
        confidences = [d.confidence for d in retrieved_analysis.detections]
        assert 0.7 in confidences
        assert 0.8 in confidences