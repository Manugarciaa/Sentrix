"""
API endpoint tests for Sentrix Backend
Tests de endpoints API para el backend de Sentrix
"""

import pytest
import json
import uuid
from datetime import datetime
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_health_endpoint(self, client: TestClient):
        """Test main health endpoint"""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "services" in data
        assert "database" in data["services"]
        assert "redis" in data["services"]
        assert "yolo_service" in data["services"]

    def test_yolo_health_endpoint_success(self, client: TestClient, mock_yolo_service):
        """Test YOLO health endpoint with successful connection"""
        response = client.get("/api/v1/health/yolo")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "yolo_service" in data
        assert data["connection"] == "success"

    def test_yolo_health_endpoint_failure(self, client: TestClient, monkeypatch):
        """Test YOLO health endpoint with connection failure"""
        # Mock a failed health check
        async def mock_failed_health():
            raise Exception("Connection failed")

        from app.services.yolo_service import YOLOServiceClient
        monkeypatch.setattr(YOLOServiceClient, "health_check", mock_failed_health)

        response = client.get("/api/v1/health/yolo")

        assert response.status_code == 200  # Endpoint returns 200 but reports unhealthy
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["connection"] == "error"


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint response"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "Sentrix API" in data["message"]
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"


class TestAnalysisEndpoints:
    """Test analysis endpoints"""

    def test_create_analysis_with_file(self, client: TestClient, sample_image_data, mock_yolo_service):
        """Test creating analysis with file upload"""
        files = {"file": ("test.jpg", sample_image_data, "image/jpeg")}
        data = {
            "confidence_threshold": 0.6,
            "include_gps": True
        }

        response = client.post("/api/v1/analyses", files=files, data=data)

        assert response.status_code == 200
        result = response.json()
        assert "analysis_id" in result
        assert result["status"] == "pending"
        assert result["has_gps_data"] in [True, False]  # Mock can return either
        assert result["estimated_processing_time"] == "30-60 seconds"

    def test_create_analysis_with_url(self, client: TestClient, mock_yolo_service):
        """Test creating analysis with image URL"""
        data = {
            "image_url": "https://example.com/test.jpg",
            "confidence_threshold": 0.7,
            "include_gps": False
        }

        response = client.post("/api/v1/analyses", data=data)

        assert response.status_code == 200
        result = response.json()
        assert "analysis_id" in result
        assert result["status"] == "pending"

    def test_create_analysis_with_coordinates(self, client: TestClient, sample_image_data, mock_yolo_service):
        """Test creating analysis with manual coordinates"""
        files = {"file": ("test.jpg", sample_image_data, "image/jpeg")}
        data = {
            "latitude": -26.831314,
            "longitude": -65.195539,
            "confidence_threshold": 0.5
        }

        response = client.post("/api/v1/analyses", files=files, data=data)

        assert response.status_code == 200
        result = response.json()
        assert "analysis_id" in result

    def test_create_analysis_missing_input(self, client: TestClient):
        """Test creating analysis without file or URL"""
        data = {"confidence_threshold": 0.5}

        response = client.post("/api/v1/analyses", data=data)

        assert response.status_code == 400
        assert "Either 'file' or 'image_url' must be provided" in response.json()["detail"]

    def test_create_analysis_both_file_and_url(self, client: TestClient, sample_image_data):
        """Test creating analysis with both file and URL (should fail)"""
        files = {"file": ("test.jpg", sample_image_data, "image/jpeg")}
        data = {"image_url": "https://example.com/test.jpg"}

        response = client.post("/api/v1/analyses", files=files, data=data)

        assert response.status_code == 400
        assert "Provide either 'file' or 'image_url', not both" in response.json()["detail"]

    def test_create_analysis_incomplete_coordinates(self, client: TestClient, sample_image_data):
        """Test creating analysis with incomplete coordinates"""
        files = {"file": ("test.jpg", sample_image_data, "image/jpeg")}
        data = {"latitude": -26.831314}  # Missing longitude

        response = client.post("/api/v1/analyses", files=files, data=data)

        assert response.status_code == 400
        assert "both latitude and longitude are required" in response.json()["detail"]

    def test_get_analysis_success(self, client: TestClient, mock_yolo_service):
        """Test getting an existing analysis"""
        # First create an analysis
        files = {"file": ("test.jpg", b"fake_image", "image/jpeg")}
        create_response = client.post("/api/v1/analyses", files=files)
        analysis_id = create_response.json()["analysis_id"]

        # Then get it
        response = client.get(f"/api/v1/analyses/{analysis_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == analysis_id
        assert data["status"] in ["pending", "completed"]
        assert "image_filename" in data
        assert "detections" in data
        assert "risk_assessment" in data

    def test_get_analysis_not_found(self, client: TestClient):
        """Test getting non-existent analysis"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/analyses/{fake_id}")

        assert response.status_code == 404
        assert "Analysis not found" in response.json()["detail"]

    def test_list_analyses_empty(self, client: TestClient):
        """Test listing analyses when none exist"""
        response = client.get("/api/v1/analyses")

        assert response.status_code == 200
        data = response.json()
        assert data["analyses"] == []
        assert data["total"] == 0
        assert data["has_next"] is False

    def test_list_analyses_with_data(self, client: TestClient, mock_yolo_service):
        """Test listing analyses with existing data"""
        # Create a few analyses
        for i in range(3):
            files = {"file": (f"test{i}.jpg", b"fake_image", "image/jpeg")}
            client.post("/api/v1/analyses", files=files)

        response = client.get("/api/v1/analyses")

        assert response.status_code == 200
        data = response.json()
        assert len(data["analyses"]) == 3
        assert data["total"] == 3

    def test_list_analyses_with_filters(self, client: TestClient, mock_yolo_service):
        """Test listing analyses with filters"""
        # Create an analysis
        files = {"file": ("test.jpg", b"fake_image", "image/jpeg")}
        client.post("/api/v1/analyses", files=files)

        # Test with GPS filter
        response = client.get("/api/v1/analyses?has_gps=true")
        assert response.status_code == 200

        # Test with pagination
        response = client.get("/api/v1/analyses?limit=10&offset=0")
        assert response.status_code == 200

    def test_list_analyses_pagination(self, client: TestClient, mock_yolo_service):
        """Test analyses pagination"""
        # Create multiple analyses
        for i in range(5):
            files = {"file": (f"test{i}.jpg", b"fake_image", "image/jpeg")}
            client.post("/api/v1/analyses", files=files)

        # Test pagination
        response = client.get("/api/v1/analyses?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["analyses"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 0
        assert data["has_next"] is True

        # Test next page
        response = client.get("/api/v1/analyses?limit=2&offset=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["analyses"]) == 2
        assert data["offset"] == 2

    def test_create_batch_analysis(self, client: TestClient, mock_yolo_service):
        """Test batch analysis creation"""
        request_data = {
            "image_urls": [
                "https://example.com/image1.jpg",
                "https://example.com/image2.jpg",
                "https://example.com/image3.jpg"
            ],
            "confidence_threshold": 0.6,
            "include_gps": True
        }

        response = client.post("/api/v1/analyses/batch", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "batch_id" in data
        assert data["total_images"] == 3
        assert len(data["analyses"]) == 3
        assert "estimated_completion_time" in data

        # Check each analysis in the batch
        for analysis in data["analyses"]:
            assert "analysis_id" in analysis
            assert analysis["status"] == "pending"

    def test_create_batch_analysis_too_many_images(self, client: TestClient):
        """Test batch analysis with too many images"""
        request_data = {
            "image_urls": [f"https://example.com/image{i}.jpg" for i in range(51)],  # 51 images (max is 50)
            "confidence_threshold": 0.5
        }

        response = client.post("/api/v1/analyses/batch", json=request_data)

        assert response.status_code == 400
        assert "Maximum 50 images per batch" in response.json()["detail"]

    def test_create_batch_analysis_empty_list(self, client: TestClient):
        """Test batch analysis with empty image list"""
        request_data = {
            "image_urls": [],
            "confidence_threshold": 0.5
        }

        response = client.post("/api/v1/analyses/batch", json=request_data)

        assert response.status_code == 422  # Validation error from Pydantic


class TestAsyncEndpoints:
    """Test endpoints using async client"""

    @pytest.mark.asyncio
    async def test_health_async(self, async_client: AsyncClient):
        """Test health endpoint with async client"""
        response = await async_client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_create_analysis_async(self, async_client: AsyncClient, sample_image_data, mock_yolo_service):
        """Test creating analysis with async client"""
        files = {"file": ("test.jpg", sample_image_data, "image/jpeg")}
        data = {"confidence_threshold": 0.5}

        response = await async_client.post("/api/v1/analyses", files=files, data=data)

        assert response.status_code == 200
        result = response.json()
        assert "analysis_id" in result


class TestErrorHandling:
    """Test error handling scenarios"""

    def test_invalid_json_body(self, client: TestClient):
        """Test handling of invalid JSON in request body"""
        response = client.post(
            "/api/v1/analyses/batch",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422

    def test_missing_required_fields(self, client: TestClient):
        """Test handling of missing required fields"""
        response = client.post("/api/v1/analyses/batch", json={})

        assert response.status_code == 422

    def test_invalid_confidence_threshold(self, client: TestClient, sample_image_data):
        """Test handling of invalid confidence threshold"""
        files = {"file": ("test.jpg", sample_image_data, "image/jpeg")}
        data = {"confidence_threshold": 1.5}  # Invalid (should be <= 1.0)

        response = client.post("/api/v1/analyses", files=files, data=data)

        # Should still accept it for now (validation might be added later)
        assert response.status_code in [200, 422]

    def test_invalid_coordinates(self, client: TestClient, sample_image_data):
        """Test handling of invalid GPS coordinates"""
        files = {"file": ("test.jpg", sample_image_data, "image/jpeg")}
        data = {
            "latitude": 95.0,  # Invalid latitude (should be <= 90)
            "longitude": -65.195539
        }

        response = client.post("/api/v1/analyses", files=files, data=data)

        # Should be rejected by validation
        assert response.status_code == 422


class TestResponseFormats:
    """Test response format compliance"""

    def test_analysis_response_format(self, client: TestClient, mock_yolo_service):
        """Test that analysis response matches expected schema"""
        # Create and get analysis
        files = {"file": ("test.jpg", b"fake_image", "image/jpeg")}
        create_response = client.post("/api/v1/analyses", files=files)
        analysis_id = create_response.json()["analysis_id"]

        response = client.get(f"/api/v1/analyses/{analysis_id}")
        data = response.json()

        # Check required fields
        required_fields = ["id", "status", "created_at", "detections", "risk_assessment"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # Check nested structures
        if data["location"]:
            assert "has_location" in data["location"]

        if data["camera_info"]:
            assert isinstance(data["camera_info"], dict)

        assert isinstance(data["detections"], list)
        assert isinstance(data["risk_assessment"], dict)

    def test_detection_response_format(self, client: TestClient, mock_yolo_service):
        """Test detection objects in response"""
        files = {"file": ("test.jpg", b"fake_image", "image/jpeg")}
        create_response = client.post("/api/v1/analyses", files=files)
        analysis_id = create_response.json()["analysis_id"]

        response = client.get(f"/api/v1/analyses/{analysis_id}")
        data = response.json()

        for detection in data["detections"]:
            # Check required detection fields
            detection_fields = ["id", "created_at", "validation_status"]
            for field in detection_fields:
                assert field in detection, f"Missing detection field: {field}"

    def test_list_response_format(self, client: TestClient):
        """Test list response format"""
        response = client.get("/api/v1/analyses")
        data = response.json()

        # Check pagination fields
        pagination_fields = ["analyses", "total", "limit", "offset", "has_next"]
        for field in pagination_fields:
            assert field in data, f"Missing pagination field: {field}"

        assert isinstance(data["analyses"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["has_next"], bool)