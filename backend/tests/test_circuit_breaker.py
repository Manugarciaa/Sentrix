"""
Tests for Circuit Breaker Pattern on YOLO Service
"""

import pytest
import httpx
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pybreaker import CircuitBreaker, CircuitBreakerError, STATE_CLOSED, STATE_OPEN, STATE_HALF_OPEN

from src.core.services.yolo_service import YOLOServiceClient, yolo_circuit_breaker


class TestCircuitBreaker:
    """Test circuit breaker functionality"""

    @pytest.fixture(autouse=True)
    def reset_circuit_breaker(self):
        """Reset circuit breaker before each test"""
        yolo_circuit_breaker.close()
        yield
        # Reset after test
        yolo_circuit_breaker.close()

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
        from pybreaker import CircuitBreakerError

        # Test by directly calling the circuit breaker with a failing function
        async def failing_function():
            raise httpx.TimeoutException("Timeout")

        # Try 5 times (fail_max) to open the circuit
        for i in range(5):
            try:
                # Call through circuit breaker
                await yolo_circuit_breaker.call_async(failing_function)
            except (httpx.TimeoutException, CircuitBreakerError):
                pass  # Expected to fail (TimeoutException first 4 times, then CircuitBreakerError)

        # Circuit should be open now
        assert yolo_circuit_breaker.current_state == "open"

    @pytest.mark.asyncio
    async def test_circuit_open_fails_fast(self):
        """Test that open circuit fails immediately"""
        from fastapi import HTTPException
        client = YOLOServiceClient()

        # Manually open the circuit
        yolo_circuit_breaker.open()

        # This should fail immediately with HTTPException 503
        with pytest.raises(HTTPException) as exc_info:
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
        from pybreaker import CircuitBreakerError

        # Test by directly calling the circuit breaker with a failing function
        async def failing_connection():
            raise httpx.ConnectError("Connection refused")

        # Try fail_max times to open the circuit
        for i in range(5):
            try:
                # Call through circuit breaker
                await yolo_circuit_breaker.call_async(failing_connection)
            except (httpx.ConnectError, CircuitBreakerError):
                pass  # Expected to fail (ConnectError first 4 times, then CircuitBreakerError)

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
        # Include without prefix since the router endpoints already have /health
        app.include_router(health.router)

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
        yolo_circuit_breaker.close()
        yield
        yolo_circuit_breaker.close()


# Note: Callback logging tests removed because callbacks were intentionally
# removed from yolo_service.py to avoid compatibility issues with pybreaker.
# Circuit breaker state changes are now logged directly in the detect_image method
# when CircuitBreakerError is caught.


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
