"""
Tests for YOLO Service Client timeout and retry logic
"""

import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException

from src.core.services.yolo_service import YOLOServiceClient


@pytest.mark.asyncio
async def test_timeout_configuration():
    """Test that timeout is properly configured"""
    client = YOLOServiceClient()

    assert client.timeout.connect == 5.0
    assert client.timeout.read == 30.0
    assert client.timeout.write == 10.0
    assert client.timeout.pool == 5.0


@pytest.mark.asyncio
async def test_connection_pooling_configuration():
    """Test that connection pooling is properly configured"""
    client = YOLOServiceClient()

    assert client.limits.max_connections == 100
    assert client.limits.max_keepalive_connections == 20


@pytest.mark.asyncio
async def test_detect_retries_on_timeout():
    """Test that detect_image retries on timeout"""
    client = YOLOServiceClient()

    with patch.object(client, '_call_yolo_detect') as mock_call:
        # Simulate 2 timeouts, then success
        response_mock = MagicMock()
        response_mock.json.return_value = {
            "status": "completed",
            "detections": [],
            "total_detections": 0,
            "processing_time_ms": 1500
        }

        mock_call.side_effect = [
            httpx.TimeoutException("Timeout 1"),
            httpx.TimeoutException("Timeout 2"),
            response_mock
        ]

        result = await client.detect_image(b"fake_data", "test.jpg")

        assert result["success"] == True
        assert mock_call.call_count == 3  # 1 initial + 2 retries


@pytest.mark.asyncio
async def test_detect_retries_on_connect_error():
    """Test that detect_image retries on connection error"""
    client = YOLOServiceClient()

    with patch.object(client, '_call_yolo_detect') as mock_call:
        # Simulate connection error, then success
        response_mock = MagicMock()
        response_mock.json.return_value = {
            "status": "completed",
            "detections": [],
            "total_detections": 0
        }

        mock_call.side_effect = [
            httpx.ConnectError("Connection refused"),
            response_mock
        ]

        result = await client.detect_image(b"fake_data", "test.jpg")

        assert result["success"] == True
        assert mock_call.call_count == 2  # 1 initial + 1 retry


@pytest.mark.asyncio
async def test_detect_fails_after_max_retries():
    """Test that detect_image fails after 3 retry attempts"""
    client = YOLOServiceClient()

    with patch.object(client, '_call_yolo_detect') as mock_call:
        # Simulate persistent timeout
        mock_call.side_effect = httpx.TimeoutException("Persistent timeout")

        with pytest.raises(HTTPException) as exc_info:
            await client.detect_image(b"fake_data", "test.jpg")

        assert exc_info.value.status_code == 504
        assert "timeout" in exc_info.value.detail.lower()
        assert mock_call.call_count == 3  # Max retries


@pytest.mark.asyncio
async def test_detect_does_not_retry_on_http_error():
    """Test that detect_image does NOT retry on HTTP 4xx/5xx errors"""
    client = YOLOServiceClient()

    with patch.object(client, '_call_yolo_detect') as mock_call:
        # Simulate HTTP 400 error (should not retry)
        http_error = httpx.HTTPStatusError(
            "Bad Request",
            request=MagicMock(),
            response=MagicMock(status_code=400, text="Invalid image format")
        )
        mock_call.side_effect = http_error

        with pytest.raises(HTTPException) as exc_info:
            await client.detect_image(b"fake_data", "test.jpg")

        assert exc_info.value.status_code == 400
        assert mock_call.call_count == 1  # No retries on HTTP errors


@pytest.mark.asyncio
async def test_detect_validates_empty_image_data():
    """Test that detect_image validates empty image data"""
    client = YOLOServiceClient()

    with pytest.raises(ValueError) as exc_info:
        await client.detect_image(b"", "test.jpg")

    assert "image_data es requerido" in str(exc_info.value)


@pytest.mark.asyncio
async def test_health_check_with_timeout():
    """Test health check has proper timeout"""
    client = YOLOServiceClient()

    with patch('httpx.AsyncClient') as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "healthy"}
        mock_response.raise_for_status = MagicMock()

        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        result = await client.health_check()

        assert result["status"] == "healthy"
        # Verify timeout was set to 10 seconds
        mock_client.assert_called_once()
        call_args = mock_client.call_args
        assert call_args.kwargs.get("timeout")


@pytest.mark.asyncio
async def test_get_available_models_with_timeout():
    """Test get_available_models has proper timeout"""
    client = YOLOServiceClient()

    with patch('httpx.AsyncClient') as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "available_models": ["yolo11n-seg.pt"],
            "current_model": "yolo11n-seg.pt"
        }
        mock_response.raise_for_status = MagicMock()

        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        result = await client.get_available_models()

        assert "available_models" in result
        assert "current_model" in result


@pytest.mark.asyncio
async def test_detect_logs_context_on_error():
    """Test that detect_image logs contextual information on errors"""
    client = YOLOServiceClient()

    with patch.object(client, '_call_yolo_detect') as mock_call:
        mock_call.side_effect = httpx.TimeoutException("Timeout")

        with patch('src.core.services.yolo_service.logger') as mock_logger:
            with pytest.raises(HTTPException):
                await client.detect_image(b"test_data", "test_image.jpg")

            # Verify error logging was called with context
            mock_logger.error.assert_called()
            call_args = mock_logger.error.call_args

            # Check that extra context was provided
            assert 'extra' in call_args.kwargs
            extra = call_args.kwargs['extra']
            assert 'filename' in extra
            assert extra['filename'] == "test_image.jpg"
