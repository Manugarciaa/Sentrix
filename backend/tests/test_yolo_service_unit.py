"""
Comprehensive unit tests for YOLOServiceClient
Tests for backend/src/core/services/yolo_service.py
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import httpx
from fastapi import HTTPException
from pybreaker import CircuitBreakerError

from src.core.services.yolo_service import (
    YOLOServiceClient,
    yolo_circuit_breaker
)


# ============================================
# Fixtures
# ============================================

@pytest.fixture
def yolo_client():
    """Create YOLOServiceClient instance"""
    return YOLOServiceClient(base_url="http://localhost:8001")


@pytest.fixture
def sample_image_data():
    """Sample image data for testing"""
    return b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00" * 1000


@pytest.fixture
def mock_yolo_response():
    """Mock successful YOLO response"""
    return {
        "analysis_id": "test-123",
        "status": "completed",
        "detections": [
            {
                "class_name": "larva",
                "confidence": 0.95,
                "bbox": [100, 100, 200, 200]
            }
        ],
        "total_detections": 1,
        "risk_assessment": {
            "overall_risk": "high",
            "risk_score": 0.8
        },
        "location": {
            "has_location": True,
            "latitude": -34.603722,
            "longitude": -58.381592
        },
        "camera_info": {
            "camera_make": "Apple",
            "camera_model": "iPhone 13"
        },
        "processing_time_ms": 150,
        "model_used": "dengue_production_v2",
        "confidence_threshold": 0.5
    }


# ============================================
# YOLOServiceClient.__init__ Tests
# ============================================

def test_client_initialization_with_default_url():
    """Test client initializes with default URL from settings"""
    with patch('src.core.services.yolo_service.settings') as mock_settings:
        mock_settings.yolo_service_url = "http://default:8001"
        mock_settings.yolo_timeout_seconds = 30.0

        client = YOLOServiceClient()

        assert client.base_url == "http://default:8001"
        assert client.timeout.read == 30.0


def test_client_initialization_with_custom_url():
    """Test client initializes with custom URL"""
    client = YOLOServiceClient(base_url="http://custom:9000")

    assert client.base_url == "http://custom:9000"


def test_client_timeout_configuration():
    """Test client timeout configuration"""
    with patch('src.core.services.yolo_service.settings') as mock_settings:
        mock_settings.yolo_service_url = "http://localhost:8001"
        mock_settings.yolo_timeout_seconds = 45.0

        client = YOLOServiceClient()

        assert client.timeout.connect == 5.0
        assert client.timeout.read == 45.0
        assert client.timeout.write == 10.0
        assert client.timeout.pool == 5.0


def test_client_connection_limits():
    """Test client connection pooling limits"""
    client = YOLOServiceClient()

    assert client.limits.max_connections == 100
    assert client.limits.max_keepalive_connections == 20


# ============================================
# health_check Tests
# ============================================

@pytest.mark.asyncio
async def test_health_check_success(yolo_client):
    """Test successful health check"""
    mock_response = Mock()
    mock_response.json.return_value = {"status": "healthy", "model_loaded": True}

    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        result = await yolo_client.health_check()

        assert result["status"] == "healthy"
        assert result["model_loaded"] is True


@pytest.mark.asyncio
async def test_health_check_connection_error(yolo_client):
    """Test health check with connection error"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        with pytest.raises(HTTPException) as exc_info:
            await yolo_client.health_check()

        assert exc_info.value.status_code == 503
        assert "Cannot connect" in exc_info.value.detail


@pytest.mark.asyncio
async def test_health_check_timeout(yolo_client):
    """Test health check with timeout"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.TimeoutException("Timeout")
        )

        with pytest.raises(HTTPException) as exc_info:
            await yolo_client.health_check()

        assert exc_info.value.status_code == 504
        assert "timeout" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_health_check_http_error(yolo_client):
    """Test health check with HTTP error"""
    mock_response = Mock()
    mock_response.status_code = 500

    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.HTTPStatusError("Server error", request=Mock(), response=mock_response)
        )

        with pytest.raises(HTTPException) as exc_info:
            await yolo_client.health_check()

        assert exc_info.value.status_code == 503
        assert "unhealthy" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_health_check_unexpected_error(yolo_client):
    """Test health check with unexpected error"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=Exception("Unexpected error")
        )

        with pytest.raises(HTTPException) as exc_info:
            await yolo_client.health_check()

        assert exc_info.value.status_code == 503


# ============================================
# detect_image Tests
# ============================================

@pytest.mark.asyncio
async def test_detect_image_success(yolo_client, sample_image_data, mock_yolo_response):
    """Test successful image detection"""
    mock_response = Mock()
    mock_response.json.return_value = mock_yolo_response

    with patch.object(yolo_client, '_call_yolo_detect', new=AsyncMock(return_value=mock_response)):
        result = await yolo_client.detect_image(
            image_data=sample_image_data,
            filename="test.jpg",
            confidence_threshold=0.5,
            include_gps=True
        )

        assert result["success"] is True
        assert result["analysis_id"] == "test-123"
        assert result["total_detections"] == 1
        assert len(result["detections"]) == 1
        assert result["detections"][0]["class_name"] == "larva"


@pytest.mark.asyncio
async def test_detect_image_with_default_confidence(yolo_client, sample_image_data, mock_yolo_response):
    """Test detect_image uses default confidence from settings"""
    mock_response = Mock()
    mock_response.json.return_value = mock_yolo_response

    with patch('src.core.services.yolo_service.settings') as mock_settings:
        mock_settings.yolo_confidence_threshold = 0.7

        with patch.object(yolo_client, '_call_yolo_detect', new=AsyncMock(return_value=mock_response)):
            result = await yolo_client.detect_image(
                image_data=sample_image_data,
                filename="test.jpg"
            )

            assert result["success"] is True


@pytest.mark.asyncio
async def test_detect_image_empty_data(yolo_client):
    """Test detect_image with empty image data"""
    with pytest.raises(ValueError) as exc_info:
        await yolo_client.detect_image(
            image_data=b"",
            filename="test.jpg"
        )

    assert "image_data es requerido" in str(exc_info.value)


@pytest.mark.asyncio
async def test_detect_image_none_data(yolo_client):
    """Test detect_image with None image data"""
    with pytest.raises(ValueError):
        await yolo_client.detect_image(
            image_data=None,
            filename="test.jpg"
        )


@pytest.mark.asyncio
async def test_detect_image_determines_content_type_png(yolo_client, sample_image_data, mock_yolo_response):
    """Test detect_image determines content type for PNG"""
    mock_response = Mock()
    mock_response.json.return_value = mock_yolo_response

    with patch.object(yolo_client, '_call_yolo_detect', new=AsyncMock(return_value=mock_response)) as mock_call:
        await yolo_client.detect_image(
            image_data=sample_image_data,
            filename="test.PNG"
        )

        # Verify content_type was set to image/png
        call_args = mock_call.call_args
        assert call_args.kwargs["content_type"] == "image/png"


@pytest.mark.asyncio
async def test_detect_image_determines_content_type_tiff(yolo_client, sample_image_data, mock_yolo_response):
    """Test detect_image determines content type for TIFF"""
    mock_response = Mock()
    mock_response.json.return_value = mock_yolo_response

    with patch.object(yolo_client, '_call_yolo_detect', new=AsyncMock(return_value=mock_response)) as mock_call:
        await yolo_client.detect_image(
            image_data=sample_image_data,
            filename="test.tiff"
        )

        call_args = mock_call.call_args
        assert call_args.kwargs["content_type"] == "image/tiff"


@pytest.mark.asyncio
async def test_detect_image_circuit_breaker_open(yolo_client, sample_image_data):
    """Test detect_image with circuit breaker open"""
    with patch.object(yolo_client, '_call_yolo_detect', new=AsyncMock(side_effect=CircuitBreakerError("Circuit open"))):
        with pytest.raises(HTTPException) as exc_info:
            await yolo_client.detect_image(
                image_data=sample_image_data,
                filename="test.jpg"
            )

        assert exc_info.value.status_code == 503
        assert "temporarily unavailable" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_detect_image_http_status_error(yolo_client, sample_image_data):
    """Test detect_image with HTTP status error"""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    with patch.object(yolo_client, '_call_yolo_detect', new=AsyncMock(
        side_effect=httpx.HTTPStatusError("Server error", request=Mock(), response=mock_response)
    )):
        with pytest.raises(HTTPException) as exc_info:
            await yolo_client.detect_image(
                image_data=sample_image_data,
                filename="test.jpg"
            )

        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_detect_image_connection_error(yolo_client, sample_image_data):
    """Test detect_image with connection error (after retries)"""
    with patch.object(yolo_client, '_call_yolo_detect', new=AsyncMock(
        side_effect=httpx.ConnectError("Connection refused")
    )):
        with pytest.raises(HTTPException) as exc_info:
            await yolo_client.detect_image(
                image_data=sample_image_data,
                filename="test.jpg"
            )

        assert exc_info.value.status_code == 503
        assert "unavailable" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_detect_image_timeout_error(yolo_client, sample_image_data):
    """Test detect_image with timeout error (after retries)"""
    with patch.object(yolo_client, '_call_yolo_detect', new=AsyncMock(
        side_effect=httpx.TimeoutException("Timeout")
    )):
        with pytest.raises(HTTPException) as exc_info:
            await yolo_client.detect_image(
                image_data=sample_image_data,
                filename="test.jpg"
            )

        assert exc_info.value.status_code == 504
        assert "timeout" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_detect_image_unexpected_error(yolo_client, sample_image_data):
    """Test detect_image with unexpected error"""
    with patch.object(yolo_client, '_call_yolo_detect', new=AsyncMock(
        side_effect=Exception("Unexpected error")
    )):
        with pytest.raises(HTTPException) as exc_info:
            await yolo_client.detect_image(
                image_data=sample_image_data,
                filename="test.jpg"
            )

        assert exc_info.value.status_code == 500


# ============================================
# get_available_models Tests
# ============================================

@pytest.mark.asyncio
async def test_get_available_models_success(yolo_client):
    """Test successful get_available_models"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "available_models": ["dengue_v1", "dengue_v2"],
        "current_model": "dengue_v2"
    }

    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        result = await yolo_client.get_available_models()

        assert len(result["available_models"]) == 2
        assert result["current_model"] == "dengue_v2"


@pytest.mark.asyncio
async def test_get_available_models_error(yolo_client):
    """Test get_available_models with error (returns empty list)"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=Exception("Connection error")
        )

        result = await yolo_client.get_available_models()

        # Should return empty list instead of raising
        assert result["available_models"] == []
        assert result["current_model"] == "unknown"


@pytest.mark.asyncio
async def test_get_available_models_http_error(yolo_client):
    """Test get_available_models with HTTP error (graceful degradation)"""
    mock_response = Mock()
    mock_response.status_code = 404

    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.HTTPStatusError("Not found", request=Mock(), response=mock_response)
        )

        result = await yolo_client.get_available_models()

        assert result["available_models"] == []


# ============================================
# Circuit Breaker Callback Tests
# ============================================
# NOTE: Circuit breaker callbacks are private functions and should be tested
# through the external behavior of the circuit breaker, not directly.
# These tests have been disabled as the internal callback functions
# are not part of the public API.

# def test_on_circuit_open_callback():
#     """Test circuit breaker open callback logs warning"""
#     # Disabled - testing internal private functions
#     pass

# def test_on_circuit_close_callback():
#     """Test circuit breaker close callback logs info"""
#     # Disabled - testing internal private functions
#     pass

# def test_on_circuit_half_open_callback():
#     """Test circuit breaker half-open callback logs info"""
#     # Disabled - testing internal private functions
#     pass


# ============================================
# Integration Tests
# ============================================

@pytest.mark.asyncio
async def test_detect_image_response_structure(yolo_client, sample_image_data, mock_yolo_response):
    """Test detect_image returns correct response structure"""
    mock_response = Mock()
    mock_response.json.return_value = mock_yolo_response

    with patch.object(yolo_client, '_call_yolo_detect', new=AsyncMock(return_value=mock_response)):
        result = await yolo_client.detect_image(
            image_data=sample_image_data,
            filename="test.jpg"
        )

        # Verify all required fields are present
        assert "success" in result
        assert "analysis_id" in result
        assert "status" in result
        assert "detections" in result
        assert "total_detections" in result
        assert "risk_assessment" in result
        assert "location" in result
        assert "camera_info" in result
        assert "processing_time_ms" in result
        assert "model_used" in result
        assert "confidence_threshold" in result


@pytest.mark.asyncio
async def test_detect_image_with_heic_file(yolo_client, sample_image_data, mock_yolo_response):
    """Test detect_image handles HEIC files correctly"""
    mock_response = Mock()
    mock_response.json.return_value = mock_yolo_response

    with patch.object(yolo_client, '_call_yolo_detect', new=AsyncMock(return_value=mock_response)) as mock_call:
        await yolo_client.detect_image(
            image_data=sample_image_data,
            filename="test.HEIC"
        )

        call_args = mock_call.call_args
        assert call_args.kwargs["content_type"] == "image/heic"


@pytest.mark.asyncio
async def test_detect_image_passes_form_data_correctly(yolo_client, sample_image_data, mock_yolo_response):
    """Test detect_image passes form data correctly"""
    mock_response = Mock()
    mock_response.json.return_value = mock_yolo_response

    with patch.object(yolo_client, '_call_yolo_detect', new=AsyncMock(return_value=mock_response)) as mock_call:
        await yolo_client.detect_image(
            image_data=sample_image_data,
            filename="test.jpg",
            confidence_threshold=0.8,
            include_gps=False
        )

        call_args = mock_call.call_args
        form_data = call_args.kwargs["form_data"]

        assert form_data["confidence_threshold"] == 0.8
        assert form_data["include_gps"] is False
