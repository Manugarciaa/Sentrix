"""
Tests for Circuit Breaker Pattern on YOLO Service
"""

import pytest
import httpx
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pybreaker import CircuitBreaker, CircuitBreakerError

from src.core.services.yolo_service import YOLOServiceClient, yolo_circuit_breaker


class TestCircuitBreaker:
    """Test circuit breaker functionality"""

    @pytest.fixture(autouse=True)
    def reset_circuit_breaker(self):
        """Reset circuit breaker before each test"""
        yolo_circuit_breaker._state = yolo_circuit_breaker.STATE_CLOSED
        yolo_circuit_breaker._fail_counter = 0
        yolo_circuit_breaker._opened_at = None
        yield
        # Reset after test
        yolo_circuit_breaker._state = yolo_circuit_breaker.STATE_CLOSED
        yolo_circuit_breaker._fail_counter = 0

    def test_circuit_breaker_configuration(self):
        """Test circuit breaker is properly configured"""
        assert yolo_circuit_breaker.fail_max == 5
        assert yolo_circuit_breaker.reset_timeout == 60
        assert yolo_circuit_breaker.name == "yolo-service"

    def test_circuit_breaker_initial_state(self):
        """Test circuit breaker starts in closed state"""
        assert yolo_circuit_breaker.current_state == "closed"
        assert yolo_circuit_breaker.fail_counter == 0

    @pytest.mark.asyncio
    async def test_successful_request_keeps_circuit_closed(self):
        """Test successful requests keep circuit closed"""
        client = YOLOServiceClient()

        with patch.object(httpx.AsyncClient, 'post', new_callable=AsyncMock) as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "detections": [],
                "total_detections": 0
            }
            mock_post.return_value = mock_response

            # Should succeed without opening circuit
            result = await client.detect_image(
                image_data=b"test_data",
                filename="test.jpg"
            )

            assert result["success"] is True
            assert yolo_circuit_breaker.current_state == "closed"

    @pytest.mark.asyncio
    async def test_circuit_opens_after_max_failures(self):
        """Test circuit opens after consecutive failures"""
        client = YOLOServiceClient()

        with patch.object(httpx.AsyncClient, 'post', new_callable=AsyncMock) as mock_post:
            # Make post raise TimeoutException
            mock_post.side_effect = httpx.TimeoutException("Timeout")

            # Try 5 times (fail_max)
            for i in range(5):
                try:
                    await client.detect_image(
                        image_data=b"test_data",
                        filename="test.jpg"
                    )
                except Exception:
                    pass  # Expected to fail

            # Circuit should be open now
            assert yolo_circuit_breaker.current_state == "open"

    @pytest.mark.asyncio
    async def test_circuit_open_fails_fast(self):
        """Test that open circuit fails immediately"""
        client = YOLOServiceClient()

        # Manually open the circuit
        yolo_circuit_breaker._state = yolo_circuit_breaker.STATE_OPEN
        import datetime
        yolo_circuit_breaker._opened_at = datetime.datetime.now()

        # This should fail immediately with CircuitBreakerError
        with pytest.raises(httpx.HTTPException) as exc_info:
            await client.detect_image(
                image_data=b"test_data",
                filename="test.jpg"
            )

        # Should return 503
        assert exc_info.value.status_code == 503
        assert "temporarily unavailable" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_http_errors_excluded_from_circuit(self):
        """Test that HTTP status errors don't count toward circuit breaker"""
        client = YOLOServiceClient()

        with patch.object(httpx.AsyncClient, 'post', new_callable=AsyncMock) as mock_post:
            # Make post raise HTTPStatusError (should be excluded)
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"

            error = httpx.HTTPStatusError(
                "Server error",
                request=Mock(),
                response=mock_response
            )
            mock_post.side_effect = error

            # Try multiple times
            for i in range(10):
                try:
                    await client.detect_image(
                        image_data=b"test_data",
                        filename="test.jpg"
                    )
                except Exception:
                    pass

            # Circuit should still be closed (HTTP errors excluded)
            assert yolo_circuit_breaker.current_state == "closed"

    @pytest.mark.asyncio
    async def test_connection_errors_count_toward_circuit(self):
        """Test that connection errors count toward circuit breaker"""
        client = YOLOServiceClient()

        with patch.object(httpx.AsyncClient, 'post', new_callable=AsyncMock) as mock_post:
            # Make post raise ConnectError
            mock_post.side_effect = httpx.ConnectError("Connection refused")

            # Try fail_max times
            for i in range(5):
                try:
                    await client.detect_image(
                        image_data=b"test_data",
                        filename="test.jpg"
                    )
                except Exception:
                    pass

            # Circuit should be open
            assert yolo_circuit_breaker.current_state == "open"


class TestCircuitBreakerHealthEndpoint:
    """Test circuit breaker health monitoring"""

    @pytest.mark.asyncio
    async def test_circuit_breaker_status_endpoint(self):
        """Test that circuit breaker status is exposed via health endpoint"""
        from fastapi.testclient import TestClient
        from src.api.v1 import health

        # Create a test router
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(health.router, prefix="/health")

        client = TestClient(app)

        response = client.get("/health/circuit-breakers")
        assert response.status_code == 200

        data = response.json()
        assert "circuit_breakers" in data
        assert "yolo_service" in data["circuit_breakers"]

        yolo_cb = data["circuit_breakers"]["yolo_service"]
        assert "name" in yolo_cb
        assert "state" in yolo_cb
        assert "fail_counter" in yolo_cb
        assert "fail_max" in yolo_cb
        assert yolo_cb["name"] == "yolo-service"
        assert yolo_cb["fail_max"] == 5

    @pytest.fixture(autouse=True)
    def reset_circuit_breaker(self):
        """Reset circuit breaker before each test"""
        yolo_circuit_breaker._state = yolo_circuit_breaker.STATE_CLOSED
        yolo_circuit_breaker._fail_counter = 0
        yolo_circuit_breaker._opened_at = None
        yield
        yolo_circuit_breaker._state = yolo_circuit_breaker.STATE_CLOSED
        yolo_circuit_breaker._fail_counter = 0


class TestCircuitBreakerLogging:
    """Test circuit breaker logging behavior"""

    @pytest.fixture(autouse=True)
    def reset_circuit_breaker(self):
        """Reset circuit breaker before each test"""
        yolo_circuit_breaker._state = yolo_circuit_breaker.STATE_CLOSED
        yolo_circuit_breaker._fail_counter = 0
        yield
        yolo_circuit_breaker._state = yolo_circuit_breaker.STATE_CLOSED
        yolo_circuit_breaker._fail_counter = 0

    def test_circuit_open_callback_logs(self, caplog):
        """Test that circuit breaker logs when opening"""
        from src.core.services.yolo_service import _on_circuit_open

        mock_breaker = Mock()
        mock_breaker.name = "yolo-service"
        mock_breaker.fail_counter = 5

        with caplog.at_level("WARNING"):
            _on_circuit_open(mock_breaker)

        # Check that warning was logged
        assert any("circuit breaker" in record.message.lower() for record in caplog.records)

    def test_circuit_close_callback_logs(self, caplog):
        """Test that circuit breaker logs when closing"""
        from src.core.services.yolo_service import _on_circuit_close

        mock_breaker = Mock()
        mock_breaker.name = "yolo-service"

        with caplog.at_level("INFO"):
            _on_circuit_close(mock_breaker)

        # Check that info was logged
        assert any("circuit breaker" in record.message.lower() for record in caplog.records)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
