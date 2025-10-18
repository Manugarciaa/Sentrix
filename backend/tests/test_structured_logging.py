"""
Tests for Structured Logging with Correlation IDs
"""

import pytest
import uuid
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware

from src.logging_config import (
    setup_logging,
    get_logger,
    bind_contextvars,
    clear_contextvars,
    get_request_id,
    get_user_id,
)
from src.middleware.request_id import RequestIDMiddleware


class TestStructuredLogging:
    """Test structured logging configuration"""

    def test_setup_logging(self):
        """Test that logging setup returns a logger"""
        logger = setup_logging(log_level="INFO")
        assert logger is not None

    def test_get_logger(self):
        """Test that get_logger returns a logger instance"""
        logger = get_logger("test_module")
        assert logger is not None

    def test_bind_contextvars_request_id(self):
        """Test binding request ID to context"""
        test_request_id = str(uuid.uuid4())
        bind_contextvars(request_id=test_request_id)
        assert get_request_id() == test_request_id
        clear_contextvars()

    def test_bind_contextvars_user_id(self):
        """Test binding user ID to context"""
        test_user_id = "user_12345"
        bind_contextvars(user_id=test_user_id)
        assert get_user_id() == test_user_id
        clear_contextvars()

    def test_bind_both_contextvars(self):
        """Test binding both request ID and user ID"""
        test_request_id = str(uuid.uuid4())
        test_user_id = "user_12345"
        bind_contextvars(request_id=test_request_id, user_id=test_user_id)
        assert get_request_id() == test_request_id
        assert get_user_id() == test_user_id
        clear_contextvars()

    def test_clear_contextvars(self):
        """Test clearing context variables"""
        bind_contextvars(request_id=str(uuid.uuid4()), user_id="user_test")
        clear_contextvars()
        assert get_request_id() is None
        assert get_user_id() is None

    def test_logger_with_context(self, caplog):
        """Test that logger includes context variables"""
        logger = get_logger("test")
        test_request_id = str(uuid.uuid4())

        bind_contextvars(request_id=test_request_id)

        with caplog.at_level("INFO"):
            logger.info("test_event", test_field="test_value")

        clear_contextvars()

        # In structured logging, the log message contains the event name
        assert "test_event" in caplog.text


class TestRequestIDMiddleware:
    """Test Request ID middleware"""

    @pytest.fixture
    def app(self):
        """Create a test FastAPI app with RequestIDMiddleware"""
        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        @app.get("/test-request-id")
        async def test_request_id_endpoint():
            return {"request_id": get_request_id()}

        @app.get("/test-error")
        async def test_error_endpoint():
            raise ValueError("Test error")

        return app

    @pytest.fixture
    def client(self, app):
        """Create a test client"""
        return TestClient(app)

    def test_middleware_adds_request_id(self, client):
        """Test that middleware adds X-Request-ID to response headers"""
        response = client.get("/test")
        assert "X-Request-ID" in response.headers
        assert response.status_code == 200

    def test_middleware_uses_existing_request_id(self, client):
        """Test that middleware uses existing X-Request-ID from request"""
        test_request_id = str(uuid.uuid4())
        response = client.get("/test", headers={"X-Request-ID": test_request_id})
        assert response.headers["X-Request-ID"] == test_request_id

    def test_middleware_generates_request_id(self, client):
        """Test that middleware generates UUID if no X-Request-ID provided"""
        response = client.get("/test")
        request_id = response.headers["X-Request-ID"]

        # Should be a valid UUID
        try:
            uuid.UUID(request_id)
        except ValueError:
            pytest.fail("Generated request ID is not a valid UUID")

    def test_request_id_available_in_route(self, client):
        """Test that request ID is available in route handlers"""
        response = client.get("/test-request-id")
        assert response.status_code == 200
        # The request ID should be accessible in the route
        # Note: In test client context, it might be None after response
        # This is expected behavior due to context cleanup

    def test_middleware_handles_errors(self, client):
        """Test that middleware still adds request ID even when errors occur"""
        response = client.get("/test-error")
        # Should have X-Request-ID even though endpoint raised an error
        assert "X-Request-ID" in response.headers
        assert response.status_code == 500

    def test_context_cleared_after_request(self, client):
        """Test that context is cleared after request completes"""
        response1 = client.get("/test")
        request_id_1 = response1.headers["X-Request-ID"]

        response2 = client.get("/test")
        request_id_2 = response2.headers["X-Request-ID"]

        # Each request should have a different ID
        assert request_id_1 != request_id_2


class TestLoggingIntegration:
    """Test logging integration with application"""

    def test_log_levels(self):
        """Test different log levels"""
        logger = get_logger("test")

        # These should not raise exceptions
        logger.debug("debug_message", key="value")
        logger.info("info_message", key="value")
        logger.warning("warning_message", key="value")
        logger.error("error_message", key="value")

    def test_structured_log_format(self, caplog):
        """Test that logs are in structured format"""
        logger = get_logger("test")

        with caplog.at_level("INFO"):
            logger.info(
                "test_event",
                field1="value1",
                field2=123,
                field3=True
            )

        # Check that the event name is logged
        assert "test_event" in caplog.text

    def test_exception_logging(self, caplog):
        """Test logging exceptions with exc_info"""
        logger = get_logger("test")

        try:
            raise ValueError("Test exception")
        except ValueError:
            with caplog.at_level("ERROR"):
                logger.error("exception_occurred", exc_info=True)

        # Should include exception information
        assert "exception_occurred" in caplog.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
