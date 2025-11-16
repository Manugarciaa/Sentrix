"""
Tests for heatmap features: authentication-aware limiting and breeding site type differentiation
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import uuid
from sqlalchemy.orm import Session


class TestHeatmapAuthenticationLimiting:
    """Test that heatmap returns 10 points for public, all points for authenticated users"""

    def test_public_heatmap_returns_max_10_points(self, client: TestClient, db_session, create_test_analyses_with_gps):
        """
        Test that unauthenticated requests to /heatmap-data return max 10 points
        """
        # Create 15 analyses with GPS data
        analyses = create_test_analyses_with_gps(count=15)

        # Make unauthenticated request
        response = client.get("/api/v1/heatmap-data")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        # Should return max 10 points for public access
        assert len(data["data"]) <= 10
        assert data["total_locations"] <= 10

    def test_authenticated_heatmap_returns_all_points(self, client: TestClient, db_session,
                                                     create_test_analyses_with_gps, auth_headers):
        """
        Test that authenticated requests to /heatmap-data return all points
        """
        # Create 15 analyses with GPS data
        analyses = create_test_analyses_with_gps(count=15)

        # Make authenticated request
        response = client.get("/api/v1/heatmap-data", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        # Should return all points for authenticated access
        assert len(data["data"]) >= 10  # More than the public limit
        assert data["total_locations"] >= 10

    def test_public_heatmap_with_explicit_limit(self, client: TestClient, db_session,
                                                create_test_analyses_with_gps):
        """
        Test that public users cannot exceed 10 points even with explicit limit parameter
        """
        # Create 20 analyses
        analyses = create_test_analyses_with_gps(count=20)

        # Try to request 100 points as public user
        response = client.get("/api/v1/heatmap-data?limit=100")

        assert response.status_code == 200
        data = response.json()

        # Should still be capped at 10 for public
        assert len(data["data"]) <= 10

    def test_authenticated_heatmap_respects_custom_limit(self, client: TestClient, db_session,
                                                         create_test_analyses_with_gps, auth_headers):
        """
        Test that authenticated users can set custom limits
        """
        # Create 20 analyses
        analyses = create_test_analyses_with_gps(count=20)

        # Request only 5 points as authenticated user
        response = client.get("/api/v1/heatmap-data?limit=5", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should respect the custom limit
        assert len(data["data"]) <= 5


class TestHeatmapBreedingSiteTypeDifferentiation:
    """Test that heatmap creates separate points for different breeding site types"""

    def test_single_analysis_multiple_breeding_types(self, client: TestClient, db_session,
                                                     create_analysis_with_multiple_breeding_types):
        """
        Test that a single analysis with multiple breeding site types generates multiple heatmap points
        """
        # Create analysis with 3 different breeding site types at same location
        analysis = create_analysis_with_multiple_breeding_types(
            breeding_types=["Basura", "Charcos/Cumulo de agua", "Huecos"]
        )

        # Get heatmap data
        response = client.get("/api/v1/heatmap-data")

        assert response.status_code == 200
        data = response.json()

        # Should have 3 points (one per breeding site type) at same coordinates
        assert len(data["data"]) == 3

        # All points should have same coordinates
        lat = data["data"][0]["latitude"]
        lng = data["data"][0]["longitude"]
        for point in data["data"]:
            assert point["latitude"] == lat
            assert point["longitude"] == lng

        # Each point should have different breeding site type
        breeding_types = [point["breedingSiteType"] for point in data["data"]]
        assert "Basura" in breeding_types
        assert "Charcos/Cumulo de agua" in breeding_types
        assert "Huecos" in breeding_types

    def test_heatmap_includes_breeding_site_type_field(self, client: TestClient, db_session,
                                                       create_test_analyses_with_gps):
        """
        Test that heatmap points include breedingSiteType field
        """
        # Create analyses with different breeding site types
        analyses = create_test_analyses_with_gps(count=5)

        response = client.get("/api/v1/heatmap-data")

        assert response.status_code == 200
        data = response.json()

        # Each point should have breedingSiteType field
        for point in data["data"]:
            assert "breedingSiteType" in point
            assert "latitude" in point
            assert "longitude" in point
            assert "intensity" in point
            assert "riskLevel" in point
            assert "detectionCount" in point

    def test_heatmap_breeding_type_counts(self, client: TestClient, db_session,
                                         create_test_analyses_with_gps):
        """
        Test that heatmap response includes breeding_type_counts
        """
        # Create analyses with various breeding types
        analyses = create_test_analyses_with_gps(count=10)

        response = client.get("/api/v1/heatmap-data")

        assert response.status_code == 200
        data = response.json()

        # Should include breeding_type_counts in response
        assert "breeding_type_counts" in data
        assert isinstance(data["breeding_type_counts"], dict)

    def test_multiple_detections_same_type_single_point(self, client: TestClient, db_session,
                                                        create_analysis_with_detections):
        """
        Test that multiple detections of same type at same location create single point
        """
        # Create analysis with 3 "Basura" detections
        analysis = create_analysis_with_detections(
            breeding_types=["Basura", "Basura", "Basura"]
        )

        response = client.get("/api/v1/heatmap-data")

        assert response.status_code == 200
        data = response.json()

        # Should have only 1 point for all Basura detections
        assert len(data["data"]) == 1
        assert data["data"][0]["breedingSiteType"] == "Basura"
        # Detection count should be 3
        assert data["data"][0]["detectionCount"] == 3


class TestHeatmapRiskLevelCalculation:
    """Test that risk levels are calculated correctly per breeding site type"""

    def test_risk_level_per_breeding_type(self, client: TestClient, db_session,
                                          create_analysis_with_mixed_risk_detections):
        """
        Test that each breeding site type gets its own risk level
        """
        # Create analysis with:
        # - 2 high-risk Basura detections
        # - 1 low-risk Charcos detection
        analysis = create_analysis_with_mixed_risk_detections()

        response = client.get("/api/v1/heatmap-data")

        assert response.status_code == 200
        data = response.json()

        # Should have 2 points
        assert len(data["data"]) == 2

        # Find Basura point
        basura_point = next(p for p in data["data"] if p["breedingSiteType"] == "Basura")
        assert basura_point["riskLevel"] == "ALTO"  # High risk

        # Find Charcos point
        charcos_point = next(p for p in data["data"] if p["breedingSiteType"] == "Charcos/Cumulo de agua")
        assert charcos_point["riskLevel"] == "BAJO"  # Low risk


# ============================================
# Fixtures
# ============================================

@pytest.fixture
def create_test_analyses_with_gps(db_session):
    """
    Fixture to create test analyses with GPS data
    """
    def _create_analyses(count=10):
        from src.database.models.models import Analysis
        from src.database.models.enums import risk_level_enum

        analyses = []
        for i in range(count):
            # Create different locations
            lat = -26.8083 + (i * 0.01)  # Vary latitude
            lng = -65.2176 + (i * 0.01)  # Vary longitude

            analysis = Analysis(
                id=uuid.uuid4(),
                image_url=f"test_image_{i}.jpg",
                image_filename=f"test_{i}.jpg",
                image_size_bytes=100000,
                has_gps_data=True,
                google_maps_url=f"https://maps.google.com/?q={lat},{lng}",
                total_detections=1,
                risk_level="high" if i % 3 == 0 else "medium",
                created_at=datetime.utcnow()
            )

            db_session.add(analysis)

            # Add a detection with breeding site type
            from src.database.models.models import Detection
            breeding_types = ["Basura", "Charcos/Cumulo de agua", "Huecos", "Calles mal hechas"]

            detection = Detection(
                id=uuid.uuid4(),
                analysis_id=analysis.id,
                class_id=i % 4,
                class_name=f"Detection_{i}",
                confidence=0.85,
                risk_level="alto" if i % 3 == 0 else "medio",
                breeding_site_type=breeding_types[i % 4],
                polygon=[],
                mask_area=100.0
            )

            db_session.add(detection)
            analyses.append(analysis)

        db_session.commit()
        return analyses

    return _create_analyses


@pytest.fixture
def create_analysis_with_multiple_breeding_types(db_session):
    """
    Fixture to create a single analysis with multiple different breeding site types
    """
    def _create_analysis(breeding_types):
        from src.database.models.models import Analysis, Detection

        # Single location
        lat, lng = -26.8083, -65.2176

        analysis = Analysis(
            id=uuid.uuid4(),
            image_url="test_multi_type.jpg",
            image_filename="test_multi.jpg",
            image_size_bytes=100000,
            has_gps_data=True,
            google_maps_url=f"https://maps.google.com/?q={lat},{lng}",
            total_detections=len(breeding_types),
            risk_level="high",
            created_at=datetime.utcnow()
        )

        db_session.add(analysis)

        # Add detections for each breeding type
        for i, breeding_type in enumerate(breeding_types):
            detection = Detection(
                id=uuid.uuid4(),
                analysis_id=analysis.id,
                class_id=i,
                class_name=f"Detection_{i}",
                confidence=0.85,
                risk_level="alto",
                breeding_site_type=breeding_type,
                polygon=[],
                mask_area=100.0
            )
            db_session.add(detection)

        db_session.commit()
        return analysis

    return _create_analysis


@pytest.fixture
def create_analysis_with_detections(db_session):
    """
    Fixture to create analysis with specific number of detections of same type
    """
    def _create_analysis(breeding_types):
        from src.database.models.models import Analysis, Detection

        lat, lng = -26.8083, -65.2176

        analysis = Analysis(
            id=uuid.uuid4(),
            image_url="test_same_type.jpg",
            image_filename="test_same.jpg",
            image_size_bytes=100000,
            has_gps_data=True,
            google_maps_url=f"https://maps.google.com/?q={lat},{lng}",
            total_detections=len(breeding_types),
            risk_level="high",
            created_at=datetime.utcnow()
        )

        db_session.add(analysis)

        for i, breeding_type in enumerate(breeding_types):
            detection = Detection(
                id=uuid.uuid4(),
                analysis_id=analysis.id,
                class_id=0,
                class_name=f"Detection_{i}",
                confidence=0.85,
                risk_level="alto",
                breeding_site_type=breeding_type,
                polygon=[],
                mask_area=100.0
            )
            db_session.add(detection)

        db_session.commit()
        return analysis

    return _create_analysis


@pytest.fixture
def create_analysis_with_mixed_risk_detections(db_session):
    """
    Fixture to create analysis with different risk levels for different breeding types
    """
    def _create_analysis():
        from src.database.models.models import Analysis, Detection

        lat, lng = -26.8083, -65.2176

        analysis = Analysis(
            id=uuid.uuid4(),
            image_url="test_mixed_risk.jpg",
            image_filename="test_mixed.jpg",
            image_size_bytes=100000,
            has_gps_data=True,
            google_maps_url=f"https://maps.google.com/?q={lat},{lng}",
            total_detections=3,
            risk_level="high",
            created_at=datetime.utcnow()
        )

        db_session.add(analysis)

        # High-risk Basura detections
        for i in range(2):
            detection = Detection(
                id=uuid.uuid4(),
                analysis_id=analysis.id,
                class_id=0,
                class_name="Basura",
                confidence=0.95,
                risk_level="alto",
                breeding_site_type="Basura",
                polygon=[],
                mask_area=200.0
            )
            db_session.add(detection)

        # Low-risk Charcos detection
        detection = Detection(
            id=uuid.uuid4(),
            analysis_id=analysis.id,
            class_id=1,
            class_name="Charcos",
            confidence=0.65,
            risk_level="bajo",
            breeding_site_type="Charcos/Cumulo de agua",
            polygon=[],
            mask_area=50.0
        )
        db_session.add(detection)

        db_session.commit()
        return analysis

    return _create_analysis


@pytest.fixture
def auth_headers(client: TestClient, db_session):
    """
    Fixture to create authenticated user and return auth headers
    """
    from src.database.models.models import UserProfile
    from src.utils.auth import get_password_hash

    # Create test user
    user = UserProfile(
        email="test@sentrix.com",
        hashed_password=get_password_hash("testpassword123"),
        display_name="Test User",
        role="user",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()

    # Login to get token
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@sentrix.com",
            "password": "testpassword123"
        }
    )

    assert response.status_code == 200
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}
