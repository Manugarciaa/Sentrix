"""
Tests for enhanced exception handlers
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import os
import json

# Need to patch environment before importing app
with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=False):
    from app import app

client = TestClient(app)


def test_http_exception_has_error_id():
    """Test that HTTP exceptions include error ID"""
    response = client.get("/nonexistent-endpoint")

    assert response.status_code == 404
    data = response.json()

    assert "error" in data
    assert "id" in data["error"]
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert "type" in data["error"]
    assert "timestamp" in data["error"]

    # Verify error ID format (UUID)
    error_id = data["error"]["id"]
    assert len(error_id) == 36  # UUID format
    assert error_id.count("-") == 4  # UUID has 4 dashes


def test_http_exception_logs_context(caplog):
    """Test that HTTP exceptions log request context"""
    with caplog.at_level("WARNING"):
        response = client.get("/nonexistent-endpoint")

        assert response.status_code == 404

        # Check logs contain context
        assert any("HTTP 404" in record.message for record in caplog.records)
        # Check that extra fields were logged
        for record in caplog.records:
            if "HTTP 404" in record.message:
                assert hasattr(record, "error_id")
                assert hasattr(record, "path")
                assert hasattr(record, "method")


def test_validation_error_has_error_id_and_details():
    """Test that validation errors include error ID and details"""
    # Try to access endpoint with no file (validation should fail)
    response = client.post("/api/v1/analyses")

    # Should get error (403 auth required or 422 validation error)
    assert response.status_code in [400, 422, 405, 403]  # Depends on endpoint config

    data = response.json()
    assert "error" in data
    assert "id" in data["error"]

    # If it's a validation error, it should have details
    if response.status_code == 422:
        assert "details" in data["error"]
        assert isinstance(data["error"]["details"], list)


def test_error_ids_are_unique():
    """Test that each error gets a unique ID"""
    error_ids = []

    for i in range(5):
        response = client.get(f"/nonexistent-{i}")
        data = response.json()
        if "error" in data and "id" in data["error"]:
            error_ids.append(data["error"]["id"])

    # All IDs should be unique
    if len(error_ids) > 0:
        assert len(error_ids) == len(set(error_ids))


def test_error_response_structure_consistency():
    """Test that all error responses have consistent structure"""
    # Test 404 error
    response = client.get("/nonexistent")
    data = response.json()

    # All errors should have same structure
    assert "error" in data
    assert "id" in data["error"]
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert "type" in data["error"]
    assert "timestamp" in data["error"]

    # Verify types
    assert isinstance(data["error"]["id"], str)
    assert isinstance(data["error"]["code"], int)
    assert isinstance(data["error"]["message"], str)
    assert isinstance(data["error"]["type"], str)
    assert isinstance(data["error"]["timestamp"], str)


def test_error_timestamp_format():
    """Test that error timestamp is in ISO format"""
    response = client.get("/nonexistent")
    data = response.json()

    timestamp = data["error"]["timestamp"]

    # Should be ISO format: 2025-10-13T10:30:45.123456
    assert "T" in timestamp
    assert len(timestamp) >= 19  # At minimum: 2025-10-13T10:30:45


def test_http_error_types_preserved():
    """Test that different HTTP error codes are preserved"""
    # 404 Not Found
    response_404 = client.get("/nonexistent")
    assert response_404.status_code == 404
    assert response_404.json()["error"]["code"] == 404
    assert response_404.json()["error"]["type"] == "http_error"

    # Other error codes would be tested here if we had endpoints for them


def test_error_id_format():
    """Test that error IDs are valid UUIDs"""
    import uuid

    response = client.get("/nonexistent")
    data = response.json()

    error_id = data["error"]["id"]

    # Should be valid UUID
    try:
        uuid_obj = uuid.UUID(error_id)
        assert str(uuid_obj) == error_id
    except ValueError:
        pytest.fail(f"Error ID '{error_id}' is not a valid UUID")


def test_root_endpoint_works():
    """Test that root endpoint doesn't trigger error handlers"""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()

    # Should not be an error response
    assert "error" not in data
    assert "name" in data
    assert "version" in data


def test_health_endpoint_works():
    """Test that health endpoint doesn't trigger error handlers"""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    # Should not be an error response
    assert "error" not in data
    assert "status" in data
    assert data["status"] == "healthy"


def test_error_response_is_json():
    """Test that error responses are properly formatted JSON"""
    response = client.get("/nonexistent")

    # Should have JSON content type
    assert "application/json" in response.headers["content-type"]

    # Should be valid JSON
    try:
        data = response.json()
        assert isinstance(data, dict)
    except json.JSONDecodeError:
        pytest.fail("Error response is not valid JSON")


def test_error_message_not_empty():
    """Test that error messages are never empty"""
    response = client.get("/nonexistent")
    data = response.json()

    message = data["error"]["message"]
    assert message is not None
    assert len(message) > 0
    assert message.strip() != ""
