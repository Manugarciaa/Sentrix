"""
Tests for health check endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import os

# Need to patch environment before importing app
with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=False):
    from app import app

client = TestClient(app)


def test_liveness_probe_always_returns_200():
    """Test that liveness probe always returns 200 OK"""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data
    assert "timestamp" in data


def test_liveness_probe_response_structure():
    """Test liveness probe response structure"""
    response = client.get("/api/v1/health")
    data = response.json()

    required_fields = ["status", "service", "version", "timestamp"]
    for field in required_fields:
        assert field in data


@pytest.mark.asyncio
async def test_readiness_probe_returns_200_when_all_healthy():
    """Test that readiness probe returns 200 when all dependencies are healthy"""
    with patch("src.api.v1.health.check_database") as mock_db, \
         patch("src.api.v1.health.check_yolo_service") as mock_yolo, \
         patch("src.api.v1.health.check_redis") as mock_redis:

        # Mock all dependencies as healthy
        mock_db.return_value = {"healthy": True, "response_time_ms": 10}
        mock_yolo.return_value = {"healthy": True, "response_time_ms": 20}
        mock_redis.return_value = {"healthy": True, "response_time_ms": 5}

        response = client.get("/api/v1/health/ready")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ready"
        assert "checks" in data
        assert data["checks"]["database"]["healthy"] == True
        assert data["checks"]["yolo_service"]["healthy"] == True
        assert data["checks"]["redis"]["healthy"] == True


@pytest.mark.asyncio
async def test_readiness_probe_returns_503_when_dependency_unhealthy():
    """Test that readiness probe returns 503 when a dependency is unhealthy"""
    with patch("src.api.v1.health.check_database") as mock_db, \
         patch("src.api.v1.health.check_yolo_service") as mock_yolo, \
         patch("src.api.v1.health.check_redis") as mock_redis:

        # Mock database as unhealthy
        mock_db.return_value = {"healthy": False, "error": "Connection refused"}
        mock_yolo.return_value = {"healthy": True, "response_time_ms": 20}
        mock_redis.return_value = {"healthy": True, "response_time_ms": 5}

        response = client.get("/api/v1/health/ready")

        assert response.status_code == 503
        data = response.json()

        assert data["status"] == "not_ready"
        assert data["checks"]["database"]["healthy"] == False


def test_readiness_probe_checks_all_dependencies():
    """Test that readiness probe checks all required dependencies"""
    response = client.get("/api/v1/health/ready")
    data = response.json()

    assert "checks" in data
    assert "database" in data["checks"]
    assert "yolo_service" in data["checks"]
    assert "redis" in data["checks"]


def test_readiness_probe_includes_response_times():
    """Test that readiness probe includes response times for each check"""
    response = client.get("/api/v1/health/ready")
    data = response.json()

    for check_name, check_data in data["checks"].items():
        assert "response_time_ms" in check_data
        assert isinstance(check_data["response_time_ms"], int)
        assert check_data["response_time_ms"] >= 0


def test_yolo_health_check_endpoint():
    """Test YOLO-specific health check endpoint"""
    response = client.get("/api/v1/health/yolo")

    # Should return 200 or 503 depending on YOLO availability
    assert response.status_code in [200, 503]

    data = response.json()
    assert "status" in data
    assert "yolo_service" in data


def test_health_check_response_has_timestamp():
    """Test that health checks include timestamp"""
    response = client.get("/api/v1/health")
    data = response.json()

    assert "timestamp" in data
    # Timestamp should be ISO format
    assert "T" in data["timestamp"]


def test_readiness_probe_response_structure():
    """Test readiness probe response structure"""
    response = client.get("/api/v1/health/ready")
    data = response.json()

    required_fields = ["status", "service", "version", "timestamp", "checks"]
    for field in required_fields:
        assert field in data


def test_liveness_endpoint_is_fast():
    """Test that liveness probe responds quickly"""
    import time
    start_time = time.time()
    response = client.get("/api/v1/health")
    duration = time.time() - start_time

    assert response.status_code == 200
    # Should respond in less than 100ms (very fast)
    assert duration < 0.1


def test_readiness_has_correct_status_values():
    """Test that readiness probe returns expected status values"""
    response = client.get("/api/v1/health/ready")
    data = response.json()

    # Status should be either "ready" or "not_ready"
    assert data["status"] in ["ready", "not_ready"]


def test_yolo_health_check_response_structure():
    """Test YOLO health check response structure"""
    response = client.get("/api/v1/health/yolo")
    data = response.json()

    required_fields = ["status", "yolo_service", "timestamp"]
    for field in required_fields:
        assert field in data


def test_health_checks_return_valid_json():
    """Test that all health check endpoints return valid JSON"""
    endpoints = [
        "/api/v1/health",
        "/api/v1/health/ready",
        "/api/v1/health/yolo"
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.headers["content-type"] == "application/json"

        # Should be parseable JSON
        data = response.json()
        assert isinstance(data, dict)


def test_readiness_probe_includes_all_check_details():
    """Test that readiness probe includes detailed information for each check"""
    response = client.get("/api/v1/health/ready")
    data = response.json()

    # Each check should have at least healthy and response_time_ms
    for check_name, check_data in data["checks"].items():
        assert "healthy" in check_data
        assert "response_time_ms" in check_data
        assert isinstance(check_data["healthy"], bool)
        assert isinstance(check_data["response_time_ms"], int)
