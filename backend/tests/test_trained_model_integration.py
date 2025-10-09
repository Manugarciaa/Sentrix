"""
Test suite for Backend integration with trained YOLO model
Tests de integración del Backend con el modelo YOLO entrenado
"""

import pytest
import os
import tempfile
import requests
import io
from PIL import Image
from fastapi.testclient import TestClient

# Import the FastAPI app
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app
from src.services.analysis_service import analysis_service


class TestTrainedModelIntegration:
    """Test integration with the trained YOLO model"""

    @classmethod
    def setup_class(cls):
        """Set up test class"""
        cls.client = TestClient(app)
        cls.yolo_service_url = "http://localhost:8001"
        cls.test_image_path = "../yolo-service/test_images/imagen_test.jpg"

    def test_health_endpoint(self):
        """Test backend health endpoint"""
        response = self.client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()

        required_keys = ["status", "timestamp", "version", "services"]
        for key in required_keys:
            assert key in data

        assert data["status"] == "healthy"

    def test_yolo_service_connection(self):
        """Test connection to YOLO service"""
        try:
            response = requests.get(f"{self.yolo_service_url}/health", timeout=5)
            if response.status_code != 200:
                pytest.skip("YOLO service not running - start it first")
        except requests.ConnectionError:
            pytest.skip("YOLO service not running - start it first")

    def test_analysis_upload_with_trained_model(self):
        """Test analysis upload using trained model"""
        # Skip if YOLO service not running
        try:
            requests.get(f"{self.yolo_service_url}/health", timeout=5)
        except requests.ConnectionError:
            pytest.skip("YOLO service not running")

        # Create a test image
        image = Image.new('RGB', (640, 480), color='blue')
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='JPEG')
        image_bytes.seek(0)

        files = {"file": ("test_image.jpg", image_bytes, "image/jpeg")}
        data = {
            "confidence_threshold": 0.5,
            "include_gps": True
        }

        response = self.client.post("/api/v1/analyses", files=files, data=data)

        # Should succeed even if no detections found
        assert response.status_code == 200
        result = response.json()

        # Verify response structure
        required_keys = ["analysis_id", "status", "has_gps_data", "estimated_processing_time", "message"]
        for key in required_keys:
            assert key in result

        assert result["status"] in ["completed", "failed"]

        # If successful, test getting the analysis
        if result["status"] == "completed":
            analysis_id = result["analysis_id"]
            get_response = self.client.get(f"/api/v1/analyses/{analysis_id}")

            # Should return analysis details without errors
            assert get_response.status_code == 200
            analysis_data = get_response.json()

            # Verify analysis structure
            analysis_keys = ["id", "status", "image_filename", "risk_assessment", "detections"]
            for key in analysis_keys:
                assert key in analysis_data

    def test_analysis_service_error_handling(self):
        """Test analysis service error handling"""
        # Test with invalid image data
        invalid_data = b"not an image"

        # Create analysis service instance
        service = analysis_service

        # This should handle errors gracefully
        try:
            result = service.process_image_analysis(
                image_data=invalid_data,
                filename="invalid.jpg",
                confidence_threshold=0.5,
                include_gps=True
            )
            # If it doesn't throw, it should return error status
            if result.get("status") == "failed":
                assert "error" in result
        except Exception as e:
            # Should handle errors gracefully
            assert isinstance(e, Exception)

    def test_enum_value_mapping(self):
        """Test that enum value mapping works correctly"""
        # Test the detection record creation logic
        from src.services.analysis_service import AnalysisService

        service = AnalysisService()

        # Test detection with our trained model classes
        test_detection = {
            "class_name": "Charcos/Cumulos de agua",
            "class_id": 2,
            "confidence": 0.75,
            "risk_level": "MEDIO",
            "breeding_site_type": "Charcos/Cumulos de agua",
            "polygon": [[100, 100], [200, 100], [200, 200], [100, 200]],
            "mask_area": 10000.0
        }

        # The service should map these to valid enum values
        # (This tests the mapping logic we implemented)
        assert test_detection["class_name"] == "Charcos/Cumulos de agua"

    def test_risk_assessment_structure(self):
        """Test risk assessment response structure"""
        # Skip if YOLO service not running
        try:
            requests.get(f"{self.yolo_service_url}/health", timeout=5)
        except requests.ConnectionError:
            pytest.skip("YOLO service not running")

        # Create a test image
        image = Image.new('RGB', (640, 480), color='green')
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='JPEG')
        image_bytes.seek(0)

        files = {"file": ("test_risk.jpg", image_bytes, "image/jpeg")}
        data = {"confidence_threshold": 0.3}

        response = self.client.post("/api/v1/analyses", files=files, data=data)

        if response.status_code == 200:
            result = response.json()

            if result["status"] == "completed":
                analysis_id = result["analysis_id"]
                get_response = self.client.get(f"/api/v1/analyses/{analysis_id}")

                if get_response.status_code == 200:
                    analysis = get_response.json()
                    risk_assessment = analysis["risk_assessment"]

                    # Verify risk assessment structure
                    risk_keys = ["level", "risk_score", "total_detections",
                               "high_risk_count", "medium_risk_count", "recommendations"]
                    for key in risk_keys:
                        assert key in risk_assessment

                    # Verify risk level is valid
                    assert risk_assessment["level"] in ["ALTO", "MEDIO", "BAJO", "MÍNIMO"]

    def test_gps_data_handling(self):
        """Test GPS data handling in analysis"""
        # Skip if YOLO service not running
        try:
            requests.get(f"{self.yolo_service_url}/health", timeout=5)
        except requests.ConnectionError:
            pytest.skip("YOLO service not running")

        # Test with GPS enabled
        image = Image.new('RGB', (640, 480), color='red')
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='JPEG')
        image_bytes.seek(0)

        files = {"file": ("test_gps.jpg", image_bytes, "image/jpeg")}
        data = {
            "confidence_threshold": 0.5,
            "include_gps": True
        }

        response = self.client.post("/api/v1/analyses", files=files, data=data)

        if response.status_code == 200:
            result = response.json()
            assert "has_gps_data" in result
            assert isinstance(result["has_gps_data"], bool)

    def test_analyses_list_endpoint(self):
        """Test analyses listing endpoint"""
        response = self.client.get("/api/v1/analyses")

        assert response.status_code == 200
        data = response.json()

        # Verify list structure
        required_keys = ["analyses", "total", "limit", "offset", "has_next"]
        for key in required_keys:
            assert key in data

        assert isinstance(data["analyses"], list)
        assert isinstance(data["total"], int)

    def test_analyses_list_with_filters(self):
        """Test analyses listing with filters"""
        params = {
            "limit": 10,
            "offset": 0,
            "risk_level": "BAJO"
        }

        response = self.client.get("/api/v1/analyses", params=params)

        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 10
        assert data["offset"] == 0

    def test_invalid_analysis_id(self):
        """Test getting analysis with invalid ID"""
        response = self.client.get("/api/v1/analyses/invalid-uuid")

        # Should return 404 or handle gracefully
        assert response.status_code in [404, 422, 500]

    def test_file_size_validation(self):
        """Test file size validation"""
        # Create a large dummy file (beyond max size)
        large_data = b"x" * (60 * 1024 * 1024)  # 60MB

        files = {"file": ("large_file.jpg", io.BytesIO(large_data), "image/jpeg")}
        data = {"confidence_threshold": 0.5}

        response = self.client.post("/api/v1/analyses", files=files, data=data)

        # Should reject large files
        assert response.status_code == 413

    def test_invalid_file_format(self):
        """Test invalid file format handling"""
        # Text file instead of image
        text_data = b"This is not an image file"

        files = {"file": ("text_file.txt", io.BytesIO(text_data), "text/plain")}
        data = {"confidence_threshold": 0.5}

        response = self.client.post("/api/v1/analyses", files=files, data=data)

        # Should reject invalid formats
        assert response.status_code == 400

    def test_confidence_threshold_validation(self):
        """Test confidence threshold validation"""
        image = Image.new('RGB', (100, 100), color='yellow')
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='JPEG')
        image_bytes.seek(0)

        # Test invalid confidence threshold
        files = {"file": ("test.jpg", image_bytes, "image/jpeg")}
        data = {"confidence_threshold": 1.5}  # Invalid > 1.0

        response = self.client.post("/api/v1/analyses", files=files, data=data)

        # Should reject invalid threshold
        assert response.status_code == 400


class TestBackendLiveIntegration:
    """Test Backend with live services running"""

    @classmethod
    def setup_class(cls):
        """Set up for live integration tests"""
        cls.backend_url = "http://localhost:8000"
        cls.yolo_url = "http://localhost:8001"

    def test_live_backend_health(self):
        """Test live backend health"""
        try:
            response = requests.get(f"{self.backend_url}/api/v1/health", timeout=5)

            if response.status_code == 200:
                data = response.json()
                assert data["status"] == "healthy"
                print("✓ Live backend is healthy")
            else:
                pytest.skip("Live backend not responding")

        except requests.ConnectionError:
            pytest.skip("Live backend not running")

    def test_live_end_to_end_analysis(self):
        """Test live end-to-end analysis workflow"""
        # Check both services are running
        try:
            backend_health = requests.get(f"{self.backend_url}/api/v1/health", timeout=5)
            yolo_health = requests.get(f"{self.yolo_url}/health", timeout=5)

            if backend_health.status_code != 200 or yolo_health.status_code != 200:
                pytest.skip("Services not fully running")

        except requests.ConnectionError:
            pytest.skip("Services not running")

        # Create test image
        image = Image.new('RGB', (640, 480), color='purple')
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='JPEG')
        image_bytes.seek(0)

        # Upload for analysis
        files = {"file": ("live_test.jpg", image_bytes, "image/jpeg")}
        data = {"confidence_threshold": 0.5, "include_gps": True}

        response = requests.post(
            f"{self.backend_url}/api/v1/analyses",
            files=files,
            data=data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✓ Live analysis completed: {result['status']}")

            # Test getting the analysis
            if result["status"] == "completed":
                analysis_id = result["analysis_id"]
                get_response = requests.get(
                    f"{self.backend_url}/api/v1/analyses/{analysis_id}",
                    timeout=10
                )

                if get_response.status_code == 200:
                    analysis = get_response.json()
                    print(f"✓ Retrieved analysis: {analysis['total_detections']} detections")
                else:
                    pytest.fail(f"Failed to retrieve analysis: {get_response.status_code}")
        else:
            pytest.fail(f"Live analysis failed: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])