"""
Integration tests for YOLO service client
Tests de integración para el cliente del servicio YOLO
"""

import pytest
import httpx
from unittest.mock import AsyncMock, patch, Mock
from fastapi import HTTPException

from app.services.yolo_service import YOLOServiceClient
from app.config import get_settings


class TestYOLOServiceClientHealthCheck:
    """Test YOLO service health check functionality"""

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check"""
        mock_response = {
            "status": "healthy",
            "model_loaded": True,
            "gpu_available": True,
            "version": "2.0.0",
            "uptime_seconds": 12345
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock()
            mock_client.return_value.__aenter__.return_value.get.return_value.json.return_value = mock_response
            mock_client.return_value.__aenter__.return_value.get.return_value.raise_for_status = Mock()

            client = YOLOServiceClient("http://localhost:8001")
            result = await client.health_check()

            assert result == mock_response
            mock_client.return_value.__aenter__.return_value.get.assert_called_once_with("http://localhost:8001/health")

    @pytest.mark.asyncio
    async def test_health_check_connection_error(self):
        """Test health check with connection error"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))

            client = YOLOServiceClient("http://localhost:8001")

            with pytest.raises(HTTPException) as exc_info:
                await client.health_check()

            assert exc_info.value.status_code == 503
            assert "Cannot connect to YOLO service" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_health_check_timeout(self):
        """Test health check with timeout"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

            client = YOLOServiceClient("http://localhost:8001")

            with pytest.raises(HTTPException) as exc_info:
                await client.health_check()

            assert exc_info.value.status_code == 504
            assert "timeout" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_health_check_http_error(self):
        """Test health check with HTTP error"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Server error", request=Mock(), response=Mock()
            )
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            client = YOLOServiceClient("http://localhost:8001")

            with pytest.raises(HTTPException) as exc_info:
                await client.health_check()

            assert exc_info.value.status_code == 503


class TestYOLOServiceClientDetection:
    """Test YOLO service detection functionality"""

    @pytest.mark.asyncio
    async def test_detect_image_with_file_data(self):
        """Test detection with binary image data"""
        mock_yolo_response = {
            "success": True,
            "processing_time_ms": 1234,
            "model_version": "yolo11s-v1",
            "detections": [
                {
                    "class": "Basura",
                    "confidence": 0.75,
                    "risk_level": "MEDIO",
                    "polygon": [[100, 100], [200, 200]],
                    "mask_area": 10000.0
                }
            ],
            "risk_assessment": {
                "level": "MEDIO",
                "high_risk_sites": 0,
                "medium_risk_sites": 1
            }
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = mock_yolo_response
            mock_response.raise_for_status = Mock()
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

            client = YOLOServiceClient("http://localhost:8001")
            image_data = b"fake_image_data"

            result = await client.detect_image(
                image_data=image_data,
                confidence_threshold=0.6,
                include_gps=True
            )

            assert result["success"] is True
            assert result["yolo_response"] == mock_yolo_response
            assert "parsed_data" in result

            # Verify the POST call was made correctly
            call_args = mock_client.return_value.__aenter__.return_value.post.call_args
            assert call_args[0][0] == "http://localhost:8001/detect"
            assert "files" in call_args[1]
            assert call_args[1]["data"]["confidence_threshold"] == 0.6
            assert call_args[1]["data"]["include_gps"] is True

    @pytest.mark.asyncio
    async def test_detect_image_with_url(self):
        """Test detection with image URL"""
        mock_yolo_response = {
            "success": True,
            "detections": [],
            "risk_assessment": {"level": "BAJO"}
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = mock_yolo_response
            mock_response.raise_for_status = Mock()
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

            client = YOLOServiceClient("http://localhost:8001")

            result = await client.detect_image(
                image_url="https://example.com/test.jpg",
                model="custom_model.pt",
                confidence_threshold=0.7
            )

            assert result["success"] is True
            assert result["yolo_response"] == mock_yolo_response

            # Verify the POST call
            call_args = mock_client.return_value.__aenter__.return_value.post.call_args
            assert call_args[1]["data"]["image_url"] == "https://example.com/test.jpg"
            assert call_args[1]["data"]["model"] == "custom_model.pt"
            assert call_args[1]["data"]["confidence_threshold"] == 0.7

    @pytest.mark.asyncio
    async def test_detect_image_missing_input(self):
        """Test detection without image data or URL"""
        client = YOLOServiceClient("http://localhost:8001")

        with pytest.raises(ValueError) as exc_info:
            await client.detect_image()

        assert "Either image_data or image_url must be provided" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_detect_image_invalid_response(self):
        """Test detection with invalid YOLO response format"""
        invalid_response = {
            "success": True,
            # Missing required fields like 'detections'
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = invalid_response
            mock_response.raise_for_status = Mock()
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

            client = YOLOServiceClient("http://localhost:8001")

            with pytest.raises(HTTPException) as exc_info:
                await client.detect_image(image_data=b"test")

            assert exc_info.value.status_code == 500
            assert "Internal error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_detect_image_http_error(self):
        """Test detection with HTTP error from YOLO service"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.text = "Bad request"
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Bad request", request=Mock(), response=mock_response
            )
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

            client = YOLOServiceClient("http://localhost:8001")

            with pytest.raises(HTTPException) as exc_info:
                await client.detect_image(image_data=b"test")

            assert exc_info.value.status_code == 400
            assert "YOLO service error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_detect_image_connection_error(self):
        """Test detection with connection error"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.ConnectError("Connection failed")
            )

            client = YOLOServiceClient("http://localhost:8001")

            with pytest.raises(HTTPException) as exc_info:
                await client.detect_image(image_data=b"test")

            assert exc_info.value.status_code == 503
            assert "Cannot connect to YOLO service" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_detect_image_timeout(self):
        """Test detection with timeout"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.TimeoutException("Timeout")
            )

            client = YOLOServiceClient("http://localhost:8001")

            with pytest.raises(HTTPException) as exc_info:
                await client.detect_image(image_data=b"test")

            assert exc_info.value.status_code == 504
            assert "timeout" in str(exc_info.value.detail).lower()


class TestYOLOServiceClientConvenienceMethods:
    """Test convenience methods"""

    @pytest.mark.asyncio
    async def test_detect_image_from_url(self):
        """Test detect_image_from_url convenience method"""
        mock_result = {"success": True, "yolo_response": {}, "parsed_data": {}}

        client = YOLOServiceClient("http://localhost:8001")

        with patch.object(client, 'detect_image', return_value=mock_result) as mock_detect:
            result = await client.detect_image_from_url(
                "https://example.com/test.jpg",
                model="test_model.pt",
                confidence_threshold=0.8,
                include_gps=False
            )

            assert result == mock_result
            mock_detect.assert_called_once_with(
                image_url="https://example.com/test.jpg",
                model="test_model.pt",
                confidence_threshold=0.8,
                include_gps=False
            )

    @pytest.mark.asyncio
    async def test_detect_image_from_file(self):
        """Test detect_image_from_file convenience method"""
        mock_result = {"success": True, "yolo_response": {}, "parsed_data": {}}

        client = YOLOServiceClient("http://localhost:8001")

        with patch.object(client, 'detect_image', return_value=mock_result) as mock_detect:
            image_data = b"test_image_data"
            result = await client.detect_image_from_file(
                image_data,
                filename="test.jpg",
                model="test_model.pt",
                confidence_threshold=0.9
            )

            assert result == mock_result
            mock_detect.assert_called_once_with(
                image_data=image_data,
                model="test_model.pt",
                confidence_threshold=0.9,
                include_gps=True  # Default value
            )


class TestYOLOServiceClientConfiguration:
    """Test client configuration"""

    def test_client_initialization_default(self):
        """Test client initialization with default settings"""
        settings = get_settings()
        client = YOLOServiceClient()

        assert client.base_url == settings.yolo_service_url
        assert client.timeout == 60.0

    def test_client_initialization_custom(self):
        """Test client initialization with custom settings"""
        client = YOLOServiceClient(
            base_url="http://custom:9000",
            timeout=120.0
        )

        assert client.base_url == "http://custom:9000"
        assert client.timeout == 120.0

    def test_singleton_instance(self):
        """Test that yolo_client singleton is properly configured"""
        from app.services.yolo_service import yolo_client

        assert isinstance(yolo_client, YOLOServiceClient)
        assert yolo_client.base_url is not None
        assert yolo_client.timeout > 0


class TestYOLOServiceIntegration:
    """Integration tests that could work with real YOLO service"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_yolo_service_health(self):
        """
        Integration test with real YOLO service (only runs if service is available)
        This test requires the YOLO service to be running on localhost:8001
        """
        client = YOLOServiceClient("http://localhost:8001")

        try:
            result = await client.health_check()
            # If we get here, the service is running
            assert "status" in result
            print(f"YOLO service is running: {result}")
        except HTTPException as e:
            if e.status_code == 503:
                pytest.skip("YOLO service not available for integration test")
            else:
                raise

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_yolo_service_detection(self, sample_image_data):
        """
        Integration test with real detection (only runs if service is available)
        """
        client = YOLOServiceClient("http://localhost:8001")

        try:
            result = await client.detect_image(
                image_data=sample_image_data,
                confidence_threshold=0.5,
                include_gps=True
            )

            # If we get here, the service processed our request
            assert result["success"] is True
            assert "yolo_response" in result
            assert "parsed_data" in result
            print(f"Detection successful: {len(result['yolo_response'].get('detections', []))} detections")

        except HTTPException as e:
            if e.status_code in [503, 504]:
                pytest.skip("YOLO service not available for integration test")
            else:
                raise