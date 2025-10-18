"""
E2E Integration Tests - Phase 2.1
Tests complete workflows from API to YOLO to Storage to DB
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
from fastapi.testclient import TestClient
from io import BytesIO
import uuid

from app import app
from src.utils.auth import get_current_active_user
from src.database.models.models import UserProfile


@pytest.fixture
def client():
    """Create test client with mocked authentication"""
    # Override authentication dependency
    async def mock_get_current_active_user():
        # Create a mock UserProfile object
        mock_user = Mock(spec=UserProfile)
        mock_user.id = uuid.uuid4()
        mock_user.email = "test@example.com"
        mock_user.role = "USER"
        mock_user.display_name = "Test User"
        mock_user.is_active = True
        mock_user.is_verified = True
        return mock_user

    app.dependency_overrides[get_current_active_user] = mock_get_current_active_user

    with TestClient(app) as test_client:
        yield test_client

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def image_data():
    return b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00" + b"\x00" * 500 + b"\xFF\xD9"


@pytest.mark.integration
def test_complete_analysis_workflow(client, image_data):
    """Test: upload to YOLO to storage to DB to response"""
    with patch('src.core.services.yolo_service.YOLOServiceClient.detect_image') as m_yolo, \
         patch('src.utils.supabase_client.SupabaseManager') as m_supa:

        # Mock YOLO service response
        m_yolo.return_value = {
            "success": True,
            "yolo_response": {
                "processing_time_ms": 100,
                "model_version": "test",
                "detections": [],
                "risk_assessment": {"level": "BAJO"},
                "location": {"has_location": False}
            },
            "parsed_data": {
                "analysis": {"total_detections": 0, "has_gps_data": False, "processing_time_ms": 100},
                "detections": []
            }
        }

        # Mock Supabase storage
        m_storage = MagicMock()
        m_storage.upload_image.return_value = {"status": "success", "public_url": "http://test.com/image.jpg"}
        m_storage.insert_analysis.return_value = {"status": "success", "analysis_id": "test-123"}
        m_supa.return_value = m_storage

        files = {"file": ("test.jpg", BytesIO(image_data), "image/jpeg")}
        resp = client.post("/api/v1/analyses", files=files)

        assert resp.status_code in [200, 201]
        assert m_yolo.called and m_storage.insert_analysis.called


@pytest.mark.integration
def test_list_analyses_pagination(client):
    """Test analyses list with pagination"""
    with patch('src.utils.supabase_client.SupabaseManager') as m_supa:

        m_query = Mock()
        m_query.select.return_value = m_query
        m_query.eq.return_value = m_query
        m_query.range.return_value = m_query
        m_query.order.return_value = m_query
        m_query.execute.return_value = Mock(data=[{"id": str(uuid.uuid4()), "created_at": "2025-01-01T00:00:00"}], count=1)

        m_storage = MagicMock()
        m_storage.client.table.return_value = m_query
        m_supa.return_value = m_storage

        resp = client.get("/api/v1/analyses?limit=10")
        assert resp.status_code == 200


@pytest.mark.integration
def test_heatmap_data_retrieval(client):
    """Test heatmap data endpoint"""
    with patch('src.utils.supabase_client.SupabaseManager') as m_supa:

        m_query = Mock()
        m_query.select.return_value = m_query
        m_query.not_ = Mock()
        m_query.not_.is_ = Mock(return_value=m_query)
        m_query.order.return_value = m_query
        m_query.limit.return_value = m_query
        m_query.execute.return_value = Mock(data=[{
            "analysis_latitude": -26.831314,
            "analysis_longitude": -65.195539,
            "total_detections": 1
        }])

        m_storage = MagicMock()
        m_storage.client.table.return_value = m_query
        m_supa.return_value = m_storage

        resp = client.get("/api/v1/analyses/heatmap")
        assert resp.status_code == 200


@pytest.mark.integration
def test_upload_without_auth_fails(image_data):
    """Test authentication is required when no override is present"""
    # Create a client without auth override
    with TestClient(app) as unauthenticated_client:
        files = {"file": ("test.jpg", BytesIO(image_data), "image/jpeg")}
        resp = unauthenticated_client.post("/api/v1/analyses", files=files)
        assert resp.status_code == 401
