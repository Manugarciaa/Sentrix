"""
Test suite for YOLO Service FastAPI server
Tests para servidor FastAPI del servicio YOLO
"""

import pytest
import os
import sys
import tempfile
import requests
import io
from PIL import Image
from fastapi.testclient import TestClient

# Add src to path
from server import app


class TestYOLOServiceAPI:
    """Test YOLO Service FastAPI endpoints"""

    @classmethod
    def setup_class(cls):
        """Set up test class"""
        cls.client = TestClient(app)
        cls.test_image_path = "test_images/imagen_test.jpg"

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Verify health response structure
        required_keys = ["status", "service", "version", "timestamp", "model_available", "model_path"]
        for key in required_keys:
            assert key in data

        assert data["status"] == "healthy"
        assert data["service"] == "yolo-dengue-detection"
        assert data["version"] == "1.0.0"
        assert isinstance(data["model_available"], bool)

    def test_models_endpoint(self):
        """Test models listing endpoint"""
        response = self.client.get("/models")

        assert response.status_code == 200
        data = response.json()

        # Verify models response structure
        assert "available_models" in data
        assert "current_model" in data
        assert isinstance(data["available_models"], list)

    def test_detect_endpoint_with_test_image(self):
        """Test detection endpoint with test image"""
        if not os.path.exists(self.test_image_path):
            pytest.skip("Test image not found")

        with open(self.test_image_path, "rb") as image_file:
            files = {"file": ("test_image.jpg", image_file, "image/jpeg")}
            data = {
                "confidence_threshold": 0.5,
                "include_gps": True
            }

            response = self.client.post("/detect", files=files, data=data)

        assert response.status_code == 200
        result = response.json()

        # Verify response structure
        required_keys = ["analysis_id", "status", "detections", "total_detections",
                        "risk_assessment", "processing_time_ms", "model_used", "confidence_threshold"]
        for key in required_keys:
            assert key in result

        assert result["status"] == "completed"
        assert isinstance(result["detections"], list)
        assert isinstance(result["total_detections"], int)
        assert isinstance(result["processing_time_ms"], int)
        assert result["confidence_threshold"] == 0.5

    def test_detect_endpoint_validation(self):
        """Test detection endpoint input validation"""
        # Test without file
        response = self.client.post("/detect", data={"confidence_threshold": 0.5})
        assert response.status_code == 422  # Validation error

        # Test with invalid confidence threshold
        if os.path.exists(self.test_image_path):
            with open(self.test_image_path, "rb") as image_file:
                files = {"file": ("test_image.jpg", image_file, "image/jpeg")}
                data = {"confidence_threshold": 1.5}  # Invalid > 1.0

                response = self.client.post("/detect", files=files, data=data)

            assert response.status_code == 400

    def test_detect_endpoint_different_formats(self):
        """Test detection with different image formats"""
        formats_to_test = [
            ("image/jpeg", "test.jpg"),
            ("image/png", "test.png"),
            ("image/tiff", "test.tiff")
        ]

        for content_type, filename in formats_to_test:
            # Create a simple test image
            image = Image.new('RGB', (100, 100), color='red')
            image_bytes = io.BytesIO()
            format_name = filename.split('.')[-1].upper()
            if format_name == 'JPG':
                format_name = 'JPEG'

            image.save(image_bytes, format=format_name)
            image_bytes.seek(0)

            files = {"file": (filename, image_bytes, content_type)}
            data = {"confidence_threshold": 0.5}

            response = self.client.post("/detect", files=files, data=data)

            # Should accept valid image formats
            assert response.status_code == 200

    def test_detect_endpoint_invalid_format(self):
        """Test detection with invalid file format"""
        # Create a text file
        text_content = b"This is not an image"
        files = {"file": ("test.txt", io.BytesIO(text_content), "text/plain")}
        data = {"confidence_threshold": 0.5}

        response = self.client.post("/detect", files=files, data=data)

        # Should reject invalid format
        assert response.status_code == 400

    def test_detect_endpoint_confidence_thresholds(self):
        """Test detection with different confidence thresholds"""
        if not os.path.exists(self.test_image_path):
            pytest.skip("Test image not found")

        thresholds = [0.1, 0.3, 0.5, 0.7, 0.9]

        for threshold in thresholds:
            with open(self.test_image_path, "rb") as image_file:
                files = {"file": ("test_image.jpg", image_file, "image/jpeg")}
                data = {"confidence_threshold": threshold}

                response = self.client.post("/detect", files=files, data=data)

            assert response.status_code == 200
            result = response.json()
            assert result["confidence_threshold"] == threshold

    def test_detect_endpoint_gps_options(self):
        """Test detection with GPS options"""
        if not os.path.exists(self.test_image_path):
            pytest.skip("Test image not found")

        # Test with GPS enabled
        with open(self.test_image_path, "rb") as image_file:
            files = {"file": ("test_image.jpg", image_file, "image/jpeg")}
            data = {"confidence_threshold": 0.5, "include_gps": True}

            response = self.client.post("/detect", files=files, data=data)

        assert response.status_code == 200
        result_with_gps = response.json()

        # Test with GPS disabled
        with open(self.test_image_path, "rb") as image_file:
            files = {"file": ("test_image.jpg", image_file, "image/jpeg")}
            data = {"confidence_threshold": 0.5, "include_gps": False}

            response = self.client.post("/detect", files=files, data=data)

        assert response.status_code == 200
        result_without_gps = response.json()

        # Both should succeed but may have different location data
        assert result_with_gps["status"] == "completed"
        assert result_without_gps["status"] == "completed"

    def test_detect_endpoint_response_structure(self):
        """Test detection response structure in detail"""
        if not os.path.exists(self.test_image_path):
            pytest.skip("Test image not found")

        with open(self.test_image_path, "rb") as image_file:
            files = {"file": ("test_image.jpg", image_file, "image/jpeg")}
            data = {"confidence_threshold": 0.3, "include_gps": True}

            response = self.client.post("/detect", files=files, data=data)

        assert response.status_code == 200
        result = response.json()

        # Test risk assessment structure
        risk_assessment = result["risk_assessment"]
        risk_keys = ["overall_risk", "risk_score", "level", "total_detections", "recommendations"]
        for key in risk_keys:
            assert key in risk_assessment

        # Test detections structure (if any)
        if result["detections"]:
            detection = result["detections"][0]
            detection_keys = ["class_name", "class_id", "confidence", "risk_level",
                            "breeding_site_type", "polygon", "mask_area"]
            for key in detection_keys:
                assert key in detection

        # Test location structure (if available)
        if "location" in result and result["location"]:
            location = result["location"]
            assert "has_location" in location

        # Test camera info structure (if available)
        if "camera_info" in result and result["camera_info"]:
            camera_info = result["camera_info"]
            camera_keys = ["camera_make", "camera_model", "camera_datetime"]
            # At least one camera field should be present
            assert any(key in camera_info for key in camera_keys)

    def test_api_performance(self):
        """Test API performance metrics"""
        if not os.path.exists(self.test_image_path):
            pytest.skip("Test image not found")

        import time

        start_time = time.time()

        with open(self.test_image_path, "rb") as image_file:
            files = {"file": ("test_image.jpg", image_file, "image/jpeg")}
            data = {"confidence_threshold": 0.5}

            response = self.client.post("/detect", files=files, data=data)

        end_time = time.time()
        total_time = (end_time - start_time) * 1000  # Convert to ms

        assert response.status_code == 200
        result = response.json()

        # API should respond within reasonable time (< 10 seconds)
        assert total_time < 10000, f"API took too long: {total_time:.0f}ms"

        # Processing time should be reported
        assert result["processing_time_ms"] > 0

        print(f"Total API time: {total_time:.0f}ms")
        print(f"Processing time: {result['processing_time_ms']}ms")


class TestYOLOServiceLive:
    """Test YOLO Service with live server (if running)"""

    @classmethod
    def setup_class(cls):
        """Set up for live server tests"""
        cls.base_url = "http://localhost:8001"
        cls.test_image_path = "test_images/imagen_test.jpg"

    def test_live_server_health(self):
        """Test live server health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)

            if response.status_code == 200:
                data = response.json()
                assert data["status"] == "healthy"
                print("✓ Live server is healthy")
            else:
                pytest.skip("Live server not responding")

        except requests.ConnectionError:
            pytest.skip("Live server not running")

    def test_live_server_detection(self):
        """Test live server detection endpoint"""
        if not os.path.exists(self.test_image_path):
            pytest.skip("Test image not found")

        try:
            with open(self.test_image_path, "rb") as image_file:
                files = {"file": ("test_image.jpg", image_file, "image/jpeg")}
                data = {"confidence_threshold": 0.5, "include_gps": True}

                response = requests.post(
                    f"{self.base_url}/detect",
                    files=files,
                    data=data,
                    timeout=30
                )

            if response.status_code == 200:
                result = response.json()
                assert result["status"] == "completed"
                print(f"✓ Live detection completed - {result['total_detections']} detections")
            else:
                pytest.fail(f"Live server detection failed: {response.status_code}")

        except requests.ConnectionError:
            pytest.skip("Live server not running")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])