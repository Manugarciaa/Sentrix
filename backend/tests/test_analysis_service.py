"""
Comprehensive tests for AnalysisService
Tests for backend/src/services/analysis_service.py
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import uuid
import httpx

from src.services.analysis_service import (
    AnalysisService,
    map_risk_level_to_db
)
from src.exceptions import (
    ImageProcessingException,
    YOLOServiceException,
    YOLOTimeoutException,
    DatabaseException
)


# ============================================
# Test map_risk_level_to_db helper function
# ============================================

def test_map_risk_level_to_db_for_analysis_alto():
    """Test mapping ALTO to 'high' for analysis table"""
    assert map_risk_level_to_db("ALTO", for_analysis=True) == "high"


def test_map_risk_level_to_db_for_analysis_medio():
    """Test mapping MEDIO to 'medium' for analysis table"""
    assert map_risk_level_to_db("MEDIO", for_analysis=True) == "medium"


def test_map_risk_level_to_db_for_analysis_bajo():
    """Test mapping BAJO to 'low' for analysis table"""
    assert map_risk_level_to_db("BAJO", for_analysis=True) == "low"


def test_map_risk_level_to_db_for_analysis_minimo():
    """Test mapping MÍNIMO to 'minimal' for analysis table"""
    assert map_risk_level_to_db("MÍNIMO", for_analysis=True) == "minimal"


def test_map_risk_level_to_db_for_analysis_unknown():
    """Test mapping unknown value defaults to 'low' for analysis"""
    assert map_risk_level_to_db("UNKNOWN", for_analysis=True) == "low"


def test_map_risk_level_to_db_for_detection_alto():
    """Test mapping ALTO to 'ALTO' for detections table"""
    assert map_risk_level_to_db("ALTO", for_analysis=False) == "ALTO"


def test_map_risk_level_to_db_for_detection_medio():
    """Test mapping MEDIO to 'MEDIO' for detections table"""
    assert map_risk_level_to_db("MEDIO", for_analysis=False) == "MEDIO"


def test_map_risk_level_to_db_for_detection_bajo():
    """Test mapping BAJO to 'BAJO' for detections table"""
    assert map_risk_level_to_db("BAJO", for_analysis=False) == "BAJO"


def test_map_risk_level_to_db_for_detection_minimo():
    """Test mapping MÍNIMO to 'BAJO' for detections table"""
    assert map_risk_level_to_db("MÍNIMO", for_analysis=False) == "BAJO"


def test_map_risk_level_to_db_for_detection_unknown():
    """Test mapping unknown value defaults to 'BAJO' for detections"""
    assert map_risk_level_to_db("UNKNOWN", for_analysis=False) == "BAJO"


# ============================================
# Fixtures
# ============================================

@pytest.fixture
def mock_supabase_manager():
    """Mock SupabaseManager with common methods"""
    manager = Mock()
    manager.client = Mock()
    manager.upload_image = Mock(return_value={
        "status": "success",
        "public_url": "https://storage.example.com/image.jpg",
        "file_path": "images/test.jpg"
    })
    manager.upload_dual_images = Mock(return_value={
        "status": "success",
        "original": {
            "public_url": "https://storage.example.com/original.jpg",
            "file_path": "images/original.jpg",
            "size_bytes": 1024
        },
        "processed": {
            "public_url": "https://storage.example.com/processed.jpg",
            "file_path": "images/processed.jpg",
            "size_bytes": 1024
        }
    })
    manager.insert_analysis = Mock(return_value={"status": "success"})
    manager.delete_image = Mock(return_value={"status": "success"})
    return manager


@pytest.fixture
def mock_yolo_client():
    """Mock YOLOServiceClient"""
    client = Mock()
    client.detect_image = AsyncMock(return_value={
        "success": True,
        "detections": [
            {
                "class_name": "larva",
                "confidence": 0.95,
                "bbox": [100, 100, 200, 200]
            }
        ],
        "location": {
            "has_location": True,
            "latitude": -34.603722,
            "longitude": -58.381592,
            "altitude_meters": 25.0,
            "location_source": "EXIF_GPS"
        },
        "camera_info": {
            "camera_make": "Apple",
            "camera_model": "iPhone 13",
            "camera_datetime": "2025-10-16T10:30:00"
        },
        "processing_time_ms": 150
    })
    return client


@pytest.fixture
def analysis_service(mock_supabase_manager, mock_yolo_client):
    """Create AnalysisService with mocked dependencies"""
    service = AnalysisService()
    service.supabase = mock_supabase_manager
    service.yolo_client = mock_yolo_client
    return service


@pytest.fixture
def sample_image_data():
    """Sample image data for testing"""
    return b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00" * 1000


# ============================================
# AnalysisService.__init__ Tests
# ============================================

def test_analysis_service_initialization():
    """Test AnalysisService initializes with required dependencies"""
    with patch('src.services.analysis_service.SupabaseManager'), \
         patch('src.services.analysis_service.YOLOServiceClient'):
        service = AnalysisService()
        assert service.supabase is not None
        assert service.yolo_client is not None


# ============================================
# process_image_analysis Tests
# ============================================

@pytest.mark.asyncio
async def test_process_image_analysis_success(analysis_service, sample_image_data):
    """Test successful image analysis processing"""
    # Mock the supabase table updates
    mock_table = Mock()
    mock_table.update = Mock(return_value=mock_table)
    mock_table.eq = Mock(return_value=mock_table)
    mock_table.execute = Mock(return_value=Mock(data=[{}]))

    analysis_service.supabase.client.table = Mock(return_value=mock_table)

    with patch('src.services.analysis_service.prepare_image_for_processing', return_value=(sample_image_data, "test.jpg")), \
         patch('src.services.analysis_service.calculate_content_signature', return_value={"sha256": "abc123", "size_bytes": 1024}), \
         patch('src.services.analysis_service.check_image_duplicate', return_value={"is_duplicate": False, "should_store_separately": True}), \
         patch('src.services.analysis_service.should_store_image', return_value=False), \
         patch('src.services.analysis_service.generate_standardized_filename', return_value="SENTRIX_20251016_test.jpg"), \
         patch('src.services.analysis_service.create_filename_variations', return_value={
             "original": "test.jpg",
             "standardized": "SENTRIX_20251016_test.jpg",
             "processed": "SENTRIX_20251016_test_processed.jpg"
         }):

        result = await analysis_service.process_image_analysis(
            image_data=sample_image_data,
            filename="test.jpg",
            confidence_threshold=0.5,
            include_gps=True
        )

        assert result["status"] == "completed"
        assert "analysis_id" in result
        assert result["total_detections"] == 1
        assert result["has_gps_data"] is True
        assert result["camera_detected"] == "Apple"


@pytest.mark.asyncio
async def test_process_image_analysis_with_manual_gps(analysis_service, sample_image_data):
    """Test image analysis with manual GPS coordinates"""
    # Mock supabase table updates
    mock_table = Mock()
    mock_table.update = Mock(return_value=mock_table)
    mock_table.eq = Mock(return_value=mock_table)
    mock_table.execute = Mock(return_value=Mock(data=[{}]))
    analysis_service.supabase.client.table = Mock(return_value=mock_table)

    with patch('src.services.analysis_service.prepare_image_for_processing', return_value=(sample_image_data, "test.jpg")), \
         patch('src.services.analysis_service.calculate_content_signature', return_value={"sha256": "abc123", "size_bytes": 1024}), \
         patch('src.services.analysis_service.check_image_duplicate', return_value={"is_duplicate": False}), \
         patch('src.services.analysis_service.should_store_image', return_value=False), \
         patch('src.services.analysis_service.generate_standardized_filename', return_value="SENTRIX_20251016_test.jpg"), \
         patch('src.services.analysis_service.create_filename_variations', return_value={
             "original": "test.jpg",
             "standardized": "SENTRIX_20251016_test.jpg",
             "processed": "SENTRIX_20251016_test_processed.jpg"
         }):

        result = await analysis_service.process_image_analysis(
            image_data=sample_image_data,
            filename="test.jpg",
            confidence_threshold=0.5,
            include_gps=False,
            manual_latitude=-34.603722,
            manual_longitude=-58.381592
        )

        assert result["status"] == "completed"
        assert result["has_gps_data"] is True


@pytest.mark.asyncio
async def test_process_image_analysis_yolo_failure(analysis_service, sample_image_data):
    """Test handling of YOLO service failure"""
    analysis_service.yolo_client.detect_image = AsyncMock(return_value={
        "success": False,
        "error": "Model not loaded"
    })

    with patch('src.services.analysis_service.prepare_image_for_processing', return_value=(sample_image_data, "test.jpg")), \
         patch('src.services.analysis_service.calculate_content_signature', return_value={"sha256": "abc123", "size_bytes": 1024}), \
         patch('src.services.analysis_service.check_image_duplicate', return_value={"is_duplicate": False}), \
         patch('src.services.analysis_service.should_store_image', return_value=False):

        result = await analysis_service.process_image_analysis(
            image_data=sample_image_data,
            filename="test.jpg"
        )

        assert result["status"] == "failed"
        assert "error" in result


@pytest.mark.asyncio
async def test_process_image_analysis_yolo_timeout(analysis_service, sample_image_data):
    """Test handling of YOLO service timeout"""
    analysis_service.yolo_client.detect_image = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

    with patch('src.services.analysis_service.prepare_image_for_processing', return_value=(sample_image_data, "test.jpg")), \
         patch('src.services.analysis_service.calculate_content_signature', return_value={"sha256": "abc123", "size_bytes": 1024}), \
         patch('src.services.analysis_service.check_image_duplicate', return_value={"is_duplicate": False}), \
         patch('src.services.analysis_service.should_store_image', return_value=False), \
         pytest.raises(YOLOTimeoutException):

        await analysis_service.process_image_analysis(
            image_data=sample_image_data,
            filename="test.jpg"
        )


@pytest.mark.asyncio
async def test_process_image_analysis_yolo_http_error(analysis_service, sample_image_data):
    """Test handling of YOLO HTTP errors"""
    mock_response = Mock()
    mock_response.status_code = 500
    analysis_service.yolo_client.detect_image = AsyncMock(
        side_effect=httpx.HTTPStatusError("Server error", request=Mock(), response=mock_response)
    )

    with patch('src.services.analysis_service.prepare_image_for_processing', return_value=(sample_image_data, "test.jpg")), \
         patch('src.services.analysis_service.calculate_content_signature', return_value={"sha256": "abc123", "size_bytes": 1024}), \
         patch('src.services.analysis_service.check_image_duplicate', return_value={"is_duplicate": False}), \
         patch('src.services.analysis_service.should_store_image', return_value=False), \
         pytest.raises(YOLOServiceException):

        await analysis_service.process_image_analysis(
            image_data=sample_image_data,
            filename="test.jpg"
        )


@pytest.mark.asyncio
async def test_process_image_analysis_yolo_connection_error(analysis_service, sample_image_data):
    """Test handling of YOLO connection errors"""
    analysis_service.yolo_client.detect_image = AsyncMock(
        side_effect=httpx.ConnectError("Connection refused")
    )

    with patch('src.services.analysis_service.prepare_image_for_processing', return_value=(sample_image_data, "test.jpg")), \
         patch('src.services.analysis_service.calculate_content_signature', return_value={"sha256": "abc123", "size_bytes": 1024}), \
         patch('src.services.analysis_service.check_image_duplicate', return_value={"is_duplicate": False}), \
         patch('src.services.analysis_service.should_store_image', return_value=False), \
         pytest.raises(YOLOServiceException):

        await analysis_service.process_image_analysis(
            image_data=sample_image_data,
            filename="test.jpg"
        )


@pytest.mark.asyncio
async def test_process_image_analysis_database_insert_failure(analysis_service, sample_image_data):
    """Test handling of database insertion failure with cleanup"""
    analysis_service.supabase.insert_analysis = Mock(return_value={"status": "error", "message": "DB error"})

    with patch('src.services.analysis_service.prepare_image_for_processing', return_value=(sample_image_data, "test.jpg")), \
         patch('src.services.analysis_service.calculate_content_signature', return_value={"sha256": "abc123", "size_bytes": 1024}), \
         patch('src.services.analysis_service.check_image_duplicate', return_value={"is_duplicate": False}), \
         patch('src.services.analysis_service.should_store_image', return_value=False), \
         patch('src.services.analysis_service.generate_standardized_filename', return_value="SENTRIX_20251016_test.jpg"), \
         patch('src.services.analysis_service.create_filename_variations', return_value={
             "original": "test.jpg",
             "standardized": "SENTRIX_20251016_test.jpg",
             "processed": "SENTRIX_20251016_test_processed.jpg"
         }):

        result = await analysis_service.process_image_analysis(
            image_data=sample_image_data,
            filename="test.jpg"
        )

        assert result["status"] == "failed"
        assert "error" in result
        # Verify cleanup was called
        analysis_service.supabase.delete_image.assert_called()


@pytest.mark.asyncio
async def test_process_image_analysis_missing_yolo_field(analysis_service, sample_image_data):
    """Test handling of missing optional field in YOLO response (handled gracefully)"""
    # Mock supabase table updates
    mock_table = Mock()
    mock_table.update = Mock(return_value=mock_table)
    mock_table.eq = Mock(return_value=mock_table)
    mock_table.execute = Mock(return_value=Mock(data=[{}]))
    analysis_service.supabase.client.table = Mock(return_value=mock_table)

    analysis_service.yolo_client.detect_image = AsyncMock(return_value={
        "success": True,
        # Missing 'detections' field - should be handled gracefully with .get()
        "processing_time_ms": 100
    })

    with patch('src.services.analysis_service.prepare_image_for_processing', return_value=(sample_image_data, "test.jpg")), \
         patch('src.services.analysis_service.calculate_content_signature', return_value={"sha256": "abc123", "size_bytes": 1024}), \
         patch('src.services.analysis_service.check_image_duplicate', return_value={"is_duplicate": False}), \
         patch('src.services.analysis_service.should_store_image', return_value=False), \
         patch('src.services.analysis_service.generate_standardized_filename', return_value="SENTRIX_20251016_test.jpg"), \
         patch('src.services.analysis_service.create_filename_variations', return_value={
             "original": "test.jpg",
             "standardized": "SENTRIX_20251016_test.jpg",
             "processed": "SENTRIX_20251016_test_processed.jpg"
         }):

        result = await analysis_service.process_image_analysis(
            image_data=sample_image_data,
            filename="test.jpg"
        )

        # Should complete successfully with 0 detections
        assert result["status"] == "completed"
        assert result["total_detections"] == 0


@pytest.mark.asyncio
async def test_process_image_analysis_no_gps(analysis_service, sample_image_data):
    """Test image analysis without GPS data"""
    # Mock supabase table updates
    mock_table = Mock()
    mock_table.update = Mock(return_value=mock_table)
    mock_table.eq = Mock(return_value=mock_table)
    mock_table.execute = Mock(return_value=Mock(data=[{}]))
    analysis_service.supabase.client.table = Mock(return_value=mock_table)

    analysis_service.yolo_client.detect_image = AsyncMock(return_value={
        "success": True,
        "detections": [{"class_name": "larva", "confidence": 0.95}],
        "location": {"has_location": False},
        "processing_time_ms": 150
    })

    with patch('src.services.analysis_service.prepare_image_for_processing', return_value=(sample_image_data, "test.jpg")), \
         patch('src.services.analysis_service.calculate_content_signature', return_value={"sha256": "abc123", "size_bytes": 1024}), \
         patch('src.services.analysis_service.check_image_duplicate', return_value={"is_duplicate": False}), \
         patch('src.services.analysis_service.should_store_image', return_value=False), \
         patch('src.services.analysis_service.generate_standardized_filename', return_value="SENTRIX_20251016_test.jpg"), \
         patch('src.services.analysis_service.create_filename_variations', return_value={
             "original": "test.jpg",
             "standardized": "SENTRIX_20251016_test.jpg",
             "processed": "SENTRIX_20251016_test_processed.jpg"
         }):

        result = await analysis_service.process_image_analysis(
            image_data=sample_image_data,
            filename="test.jpg",
            include_gps=False
        )

        assert result["status"] == "completed"
        assert result["has_gps_data"] is False


# ============================================
# get_analysis_by_id Tests
# ============================================

@pytest.mark.asyncio
async def test_get_analysis_by_id_success(analysis_service):
    """Test successful retrieval of analysis by ID"""
    analysis_id = str(uuid.uuid4())

    mock_table = Mock()
    mock_table.select = Mock(return_value=mock_table)
    mock_table.eq = Mock(return_value=mock_table)
    mock_table.execute = Mock(return_value=Mock(data=[{
        "id": analysis_id,
        "image_url": "https://example.com/image.jpg",
        "total_detections": 5,
        "has_gps_data": True,
        "google_maps_url": "https://maps.google.com/?q=1,2"
    }]))

    analysis_service.supabase.client.table = Mock(return_value=mock_table)

    result = await analysis_service.get_analysis_by_id(analysis_id)

    assert result is not None
    assert result["id"] == analysis_id
    assert result["total_detections"] == 5


@pytest.mark.asyncio
async def test_get_analysis_by_id_not_found(analysis_service):
    """Test retrieval of non-existent analysis"""
    mock_table = Mock()
    mock_table.select = Mock(return_value=mock_table)
    mock_table.eq = Mock(return_value=mock_table)
    mock_table.execute = Mock(return_value=Mock(data=[]))

    analysis_service.supabase.client.table = Mock(return_value=mock_table)

    result = await analysis_service.get_analysis_by_id("nonexistent-id")

    assert result is None


@pytest.mark.asyncio
async def test_get_analysis_by_id_database_error(analysis_service):
    """Test handling of database error in get_analysis_by_id"""
    mock_table = Mock()
    mock_table.select = Mock(return_value=mock_table)
    mock_table.eq = Mock(return_value=mock_table)
    mock_table.execute = Mock(side_effect=Exception("Database error"))

    analysis_service.supabase.client.table = Mock(return_value=mock_table)

    with pytest.raises(DatabaseException):
        await analysis_service.get_analysis_by_id("test-id")


# ============================================
# _get_recent_analyses_for_deduplication Tests
# ============================================

@pytest.mark.asyncio
async def test_get_recent_analyses_for_deduplication_success(analysis_service):
    """Test successful retrieval of recent analyses"""
    mock_table = Mock()
    mock_table.select = Mock(return_value=mock_table)
    mock_table.order = Mock(return_value=mock_table)
    mock_table.limit = Mock(return_value=mock_table)
    mock_table.execute = Mock(return_value=Mock(data=[
        {"id": "1", "content_hash": "abc123"},
        {"id": "2", "content_hash": "def456"}
    ]))

    analysis_service.supabase.client.table = Mock(return_value=mock_table)

    result = await analysis_service._get_recent_analyses_for_deduplication()

    assert len(result) == 2
    assert result[0]["id"] == "1"


@pytest.mark.asyncio
async def test_get_recent_analyses_for_deduplication_error(analysis_service):
    """Test graceful handling of error (returns empty list)"""
    mock_table = Mock()
    mock_table.select = Mock(return_value=mock_table)
    mock_table.order = Mock(return_value=mock_table)
    mock_table.limit = Mock(return_value=mock_table)
    mock_table.execute = Mock(side_effect=Exception("Database error"))

    analysis_service.supabase.client.table = Mock(return_value=mock_table)

    result = await analysis_service._get_recent_analyses_for_deduplication()

    # Should return empty list instead of raising
    assert result == []


# ============================================
# _handle_duplicate_image Tests
# ============================================

@pytest.mark.asyncio
async def test_handle_duplicate_image_success(analysis_service):
    """Test successful handling of duplicate image"""
    duplicate_check = {
        "is_duplicate": True,
        "duplicate_analysis_id": "original-id",
        "reference_image_url": "https://example.com/original.jpg",
        "confidence": 0.95,
        "duplicate_type": "exact"
    }

    content_signature = {
        "sha256": "abc123",
        "size_bytes": 2048
    }

    with patch('src.services.analysis_service.generate_standardized_filename', return_value="SENTRIX_DUP_test.jpg"), \
         patch('src.services.analysis_service.create_filename_variations', return_value={
             "original": "test.jpg",
             "standardized": "SENTRIX_DUP_test.jpg",
             "processed": "SENTRIX_DUP_test_processed.jpg"
         }):

        result = await analysis_service._handle_duplicate_image(
            duplicate_check,
            "test.jpg",
            "test_processed.jpg",
            content_signature
        )

        assert result["status"] == "completed"
        assert result["is_duplicate"] is True
        assert result["storage_saved_bytes"] == 2048
        assert result["duplicate_confidence"] == 0.95


@pytest.mark.asyncio
async def test_handle_duplicate_image_insert_failure(analysis_service):
    """Test handling of database insert failure for duplicate"""
    analysis_service.supabase.insert_analysis = Mock(return_value={
        "status": "error",
        "message": "Insert failed"
    })

    duplicate_check = {
        "duplicate_analysis_id": "original-id",
        "reference_image_url": "https://example.com/original.jpg",
        "confidence": 0.95,
        "duplicate_type": "exact"
    }

    content_signature = {"sha256": "abc123", "size_bytes": 2048}

    with patch('src.services.analysis_service.generate_standardized_filename', return_value="SENTRIX_DUP_test.jpg"), \
         patch('src.services.analysis_service.create_filename_variations', return_value={
             "processed": "SENTRIX_DUP_test_processed.jpg"
         }):

        result = await analysis_service._handle_duplicate_image(
            duplicate_check,
            "test.jpg",
            "test_processed.jpg",
            content_signature
        )

        assert result["status"] == "failed"
        assert "error" in result


# ============================================
# get_deduplication_stats Tests
# ============================================

def test_get_deduplication_stats_success(analysis_service):
    """Test successful retrieval of deduplication stats"""
    mock_table = Mock()

    # Mock total analyses query
    total_mock = Mock()
    total_mock.select = Mock(return_value=total_mock)
    total_mock.execute = Mock(return_value=Mock(count=100))

    # Mock duplicates query
    duplicates_mock = Mock()
    duplicates_mock.select = Mock(return_value=duplicates_mock)
    duplicates_mock.eq = Mock(return_value=duplicates_mock)
    duplicates_mock.execute = Mock(return_value=Mock(
        count=20,
        data=[
            {"id": "1", "storage_saved_bytes": 1024},
            {"id": "2", "storage_saved_bytes": 2048}
        ]
    ))

    call_count = [0]
    def table_side_effect(*args):
        call_count[0] += 1
        if call_count[0] == 1:
            return total_mock
        else:
            return duplicates_mock

    analysis_service.supabase.client.table = Mock(side_effect=table_side_effect)

    result = analysis_service.get_deduplication_stats()

    assert result["total_analyses"] == 100
    assert result["duplicate_references"] == 20
    assert result["deduplication_rate"] == 20.0
    assert result["storage_saved_bytes"] == 3072


def test_get_deduplication_stats_error(analysis_service):
    """Test graceful handling of error in deduplication stats"""
    mock_table = Mock()
    mock_table.select = Mock(side_effect=Exception("Database error"))

    analysis_service.supabase.client.table = Mock(return_value=mock_table)

    result = analysis_service.get_deduplication_stats()

    # Should return default stats instead of raising
    assert "error" in result
    assert result["total_analyses"] == 0


# ============================================
# list_analyses Tests
# ============================================

@pytest.mark.asyncio
async def test_list_analyses_no_filters(analysis_service):
    """Test listing analyses without filters"""
    # Mock the main analyses query
    mock_analyses_table = Mock()
    mock_analyses_table.select = Mock(return_value=mock_analyses_table)
    mock_analyses_table.range = Mock(return_value=mock_analyses_table)
    mock_analyses_table.order = Mock(return_value=mock_analyses_table)
    mock_analyses_table.execute = Mock(return_value=Mock(data=[
        {"id": "1", "total_detections": 5},
        {"id": "2", "total_detections": 3}
    ], count=2))

    # Mock the count query
    mock_count_table = Mock()
    mock_count_table.select = Mock(return_value=mock_count_table)
    mock_count_table.execute = Mock(return_value=Mock(count=2))

    # Mock the detections query
    mock_detections_table = Mock()
    mock_detections_table.select = Mock(return_value=mock_detections_table)
    mock_detections_table.in_ = Mock(return_value=mock_detections_table)
    mock_detections_table.execute = Mock(return_value=Mock(data=[]))

    call_count = [0]
    def table_side_effect(name):
        call_count[0] += 1
        if name == 'analyses':
            if call_count[0] <= 2:
                return mock_analyses_table
            else:
                return mock_count_table
        else:  # detections
            return mock_detections_table

    analysis_service.supabase.client.table = Mock(side_effect=table_side_effect)

    result = await analysis_service.list_analyses(limit=10, offset=0)

    assert len(result["analyses"]) == 2
    assert result["total"] == 2
    assert result["has_next"] is False


@pytest.mark.asyncio
async def test_list_analyses_with_filters(analysis_service):
    """Test listing analyses with filters"""
    # Mock the main analyses query
    mock_analyses_table = Mock()
    mock_analyses_table.select = Mock(return_value=mock_analyses_table)
    mock_analyses_table.eq = Mock(return_value=mock_analyses_table)
    mock_analyses_table.range = Mock(return_value=mock_analyses_table)
    mock_analyses_table.order = Mock(return_value=mock_analyses_table)
    mock_analyses_table.execute = Mock(return_value=Mock(data=[
        {"id": "1", "has_gps_data": True, "risk_level": "high"}
    ], count=1))

    # Mock the count query
    mock_count_table = Mock()
    mock_count_table.select = Mock(return_value=mock_count_table)
    mock_count_table.eq = Mock(return_value=mock_count_table)
    mock_count_table.execute = Mock(return_value=Mock(count=1))

    # Mock the detections query
    mock_detections_table = Mock()
    mock_detections_table.select = Mock(return_value=mock_detections_table)
    mock_detections_table.in_ = Mock(return_value=mock_detections_table)
    mock_detections_table.execute = Mock(return_value=Mock(data=[]))

    call_count = [0]
    def table_side_effect(name):
        call_count[0] += 1
        if name == 'analyses':
            if call_count[0] <= 2:
                return mock_analyses_table
            else:
                return mock_count_table
        else:
            return mock_detections_table

    analysis_service.supabase.client.table = Mock(side_effect=table_side_effect)

    result = await analysis_service.list_analyses(
        limit=10,
        offset=0,
        has_gps=True,
        risk_level="high"
    )

    assert len(result["analyses"]) == 1
    assert result["analyses"][0]["has_gps_data"] is True


@pytest.mark.asyncio
async def test_list_analyses_pagination(analysis_service):
    """Test pagination in list_analyses"""
    # Mock the main analyses query
    mock_analyses_table = Mock()
    mock_analyses_table.select = Mock(return_value=mock_analyses_table)
    mock_analyses_table.range = Mock(return_value=mock_analyses_table)
    mock_analyses_table.order = Mock(return_value=mock_analyses_table)
    mock_analyses_table.execute = Mock(return_value=Mock(data=[
        {"id": str(i), "total_detections": i} for i in range(10)
    ], count=50))

    # Mock the count query
    mock_count_table = Mock()
    mock_count_table.select = Mock(return_value=mock_count_table)
    mock_count_table.execute = Mock(return_value=Mock(count=50))

    # Mock the detections query
    mock_detections_table = Mock()
    mock_detections_table.select = Mock(return_value=mock_detections_table)
    mock_detections_table.in_ = Mock(return_value=mock_detections_table)
    mock_detections_table.execute = Mock(return_value=Mock(data=[]))

    call_count = [0]
    def table_side_effect(name):
        call_count[0] += 1
        if name == 'analyses':
            if call_count[0] <= 2:
                return mock_analyses_table
            else:
                return mock_count_table
        else:
            return mock_detections_table

    analysis_service.supabase.client.table = Mock(side_effect=table_side_effect)

    result = await analysis_service.list_analyses(limit=10, offset=0)

    assert result["limit"] == 10
    assert result["offset"] == 0
    assert result["has_next"] is True  # 50 total, showing 0-9, has more


@pytest.mark.asyncio
async def test_list_analyses_database_error(analysis_service):
    """Test handling of database error in list_analyses"""
    mock_table = Mock()
    mock_table.select = Mock(return_value=mock_table)
    mock_table.range = Mock(return_value=mock_table)
    mock_table.order = Mock(return_value=mock_table)
    mock_table.execute = Mock(side_effect=Exception("Database error"))

    analysis_service.supabase.client.table = Mock(return_value=mock_table)

    with pytest.raises(DatabaseException):
        await analysis_service.list_analyses()


# ============================================
# get_heatmap_data Tests
# ============================================

@pytest.mark.asyncio
async def test_get_heatmap_data_no_filters(analysis_service):
    """Test getting heatmap data without filters"""
    # Mock analyses query
    mock_analyses_query = Mock()
    mock_analyses_query.select = Mock(return_value=mock_analyses_query)
    mock_analyses_query.not_ = Mock()
    mock_analyses_query.not_.is_ = Mock(return_value=mock_analyses_query)
    mock_analyses_query.order = Mock(return_value=mock_analyses_query)
    mock_analyses_query.limit = Mock(return_value=mock_analyses_query)
    mock_analyses_query.execute = Mock(return_value=Mock(data=[
        {"id": "1", "google_maps_url": "https://maps.google.com/?q=1,2", "risk_level": "high"},
        {"id": "2", "google_maps_url": "https://maps.google.com/?q=3,4", "risk_level": "low"}
    ]))

    # Mock detections query
    mock_detections_query = Mock()
    mock_detections_query.select = Mock(return_value=mock_detections_query)
    mock_detections_query.in_ = Mock(return_value=mock_detections_query)
    mock_detections_query.execute = Mock(return_value=Mock(data=[
        {"analysis_id": "1", "breeding_site_type": "container", "risk_level": "high"},
        {"analysis_id": "2", "breeding_site_type": "tire", "risk_level": "low"}
    ]))

    # Mock table() to return different queries based on table name
    def table_side_effect(table_name):
        if table_name == "analyses":
            return mock_analyses_query
        elif table_name == "detections":
            return mock_detections_query
        return Mock()

    analysis_service.supabase.client.table = Mock(side_effect=table_side_effect)

    result = await analysis_service.get_heatmap_data(limit=1000)

    assert result["status"] == "success"
    assert result["count"] == 2
    assert len(result["data"]) == 2


@pytest.mark.asyncio
async def test_get_heatmap_data_with_filters(analysis_service):
    """Test getting heatmap data with risk level filter"""
    # Mock analyses query
    mock_analyses_query = Mock()
    mock_analyses_query.select = Mock(return_value=mock_analyses_query)
    mock_analyses_query.not_ = Mock()
    mock_analyses_query.not_.is_ = Mock(return_value=mock_analyses_query)
    mock_analyses_query.eq = Mock(return_value=mock_analyses_query)
    mock_analyses_query.order = Mock(return_value=mock_analyses_query)
    mock_analyses_query.limit = Mock(return_value=mock_analyses_query)
    mock_analyses_query.execute = Mock(return_value=Mock(data=[
        {"id": "1", "google_maps_url": "https://maps.google.com/?q=1,2", "risk_level": "high"}
    ]))

    # Mock detections query
    mock_detections_query = Mock()
    mock_detections_query.select = Mock(return_value=mock_detections_query)
    mock_detections_query.in_ = Mock(return_value=mock_detections_query)
    mock_detections_query.execute = Mock(return_value=Mock(data=[
        {"analysis_id": "1", "breeding_site_type": "container", "risk_level": "high"}
    ]))

    # Mock table() to return different queries based on table name
    def table_side_effect(table_name):
        if table_name == "analyses":
            return mock_analyses_query
        elif table_name == "detections":
            return mock_detections_query
        return Mock()

    analysis_service.supabase.client.table = Mock(side_effect=table_side_effect)

    result = await analysis_service.get_heatmap_data(limit=1000, risk_level="ALTO")

    assert result["status"] == "success"
    assert result["count"] == 1


@pytest.mark.asyncio
async def test_get_heatmap_data_database_error(analysis_service):
    """Test handling of database error in get_heatmap_data"""
    mock_query = Mock()
    mock_query.select = Mock(return_value=mock_query)
    mock_query.not_ = Mock()
    mock_query.not_.is_ = Mock(side_effect=Exception("Database error"))

    analysis_service.supabase.client.table = Mock(return_value=mock_query)

    with pytest.raises(DatabaseException):
        await analysis_service.get_heatmap_data()


# ============================================
# get_map_statistics Tests
# ============================================

@pytest.mark.asyncio
async def test_get_map_statistics_success(analysis_service):
    """Test successful retrieval of map statistics"""
    mock_query = Mock()
    mock_query.select = Mock(return_value=mock_query)
    mock_query.execute = Mock(return_value=Mock(data=[
        {"risk_level": "high", "total_detections": 10, "google_maps_url": "url1"},
        {"risk_level": "low", "total_detections": 5, "google_maps_url": "url2"}
    ]))

    analysis_service.supabase.client.table = Mock(return_value=mock_query)

    result = await analysis_service.get_map_statistics()

    assert result["status"] == "success"
    assert result["total_analyses"] == 2
    assert result["total_detections"] == 15


@pytest.mark.asyncio
async def test_get_map_statistics_empty_data(analysis_service):
    """Test map statistics with no data"""
    mock_query = Mock()
    mock_query.select = Mock(return_value=mock_query)
    mock_query.execute = Mock(return_value=Mock(data=[]))

    analysis_service.supabase.client.table = Mock(return_value=mock_query)

    result = await analysis_service.get_map_statistics()

    assert result["total_analyses"] == 0
    assert result["total_detections"] == 0


@pytest.mark.asyncio
async def test_get_map_statistics_database_error(analysis_service):
    """Test handling of database error in get_map_statistics"""
    mock_query = Mock()
    mock_query.select = Mock(return_value=mock_query)
    mock_query.execute = Mock(side_effect=Exception("Database error"))

    analysis_service.supabase.client.table = Mock(return_value=mock_query)

    with pytest.raises(DatabaseException):
        await analysis_service.get_map_statistics()


# ============================================
# Additional Coverage Tests for Missing Lines
# ============================================

@pytest.mark.asyncio
async def test_process_image_with_processed_base64_success(analysis_service, mock_yolo_client):
    """Test processing image with base64 encoded processed image from YOLO"""
    import base64

    # Create mock processed image data
    processed_image_bytes = b"processed_image_data"
    processed_image_base64 = base64.b64encode(processed_image_bytes).decode('utf-8')

    mock_yolo_client.detect_image = AsyncMock(return_value={
        "success": True,
        "detections": [],
        "total_detections": 0,
        "location": None,
        "camera_info": None,
        "processing_time_ms": 100,
        "processed_image_base64": processed_image_base64
    })

    # Mock dual upload success
    analysis_service.supabase.upload_dual_images = Mock(return_value={
        "status": "success",
        "original": {
            "public_url": "https://storage.example.com/original.jpg",
            "file_path": "images/original.jpg"
        },
        "processed": {
            "public_url": "https://storage.example.com/processed.jpg",
            "file_path": "images/processed.jpg"
        }
    })

    analysis_service.supabase.insert_analysis = Mock(return_value={"status": "success"})

    # Mock deduplication check
    with patch.object(analysis_service, '_get_recent_analyses_for_deduplication', new_callable=AsyncMock) as mock_dedup:
        mock_dedup.return_value = []

        result = await analysis_service.process_image_analysis(
            image_data=b"test_image_data",
            filename="test.jpg"
        )

        assert result["status"] == "completed"
        assert result["image_urls"]["processed"] is not None
        analysis_service.supabase.upload_dual_images.assert_called_once()


@pytest.mark.asyncio
async def test_process_image_with_invalid_base64(analysis_service, mock_yolo_client):
    """Test handling of invalid base64 encoded processed image"""
    mock_yolo_client.detect_image = AsyncMock(return_value={
        "success": True,
        "detections": [],
        "total_detections": 0,
        "location": None,
        "camera_info": None,
        "processing_time_ms": 100,
        "processed_image_base64": "invalid_base64!!!"
    })

    # Should fallback to single upload
    analysis_service.supabase.upload_image = Mock(return_value={
        "status": "success",
        "public_url": "https://storage.example.com/image.jpg",
        "file_path": "images/test.jpg"
    })

    analysis_service.supabase.insert_analysis = Mock(return_value={"status": "success"})

    # Mock deduplication check
    with patch.object(analysis_service, '_get_recent_analyses_for_deduplication', new_callable=AsyncMock) as mock_dedup:
        mock_dedup.return_value = []

        result = await analysis_service.process_image_analysis(
            image_data=b"test_image_data",
            filename="test.jpg"
        )

        assert result["status"] == "completed"
        # Should use single upload fallback
        analysis_service.supabase.upload_image.assert_called_once()


@pytest.mark.asyncio
async def test_process_image_single_upload_fallback(analysis_service, mock_yolo_client):
    """Test fallback to single upload when no processed image available"""
    mock_yolo_client.detect_image = AsyncMock(return_value={
        "success": True,
        "detections": [],
        "total_detections": 0,
        "location": None,
        "camera_info": None,
        "processing_time_ms": 100,
        "processed_image_base64": None
    })

    analysis_service.supabase.upload_image = Mock(return_value={
        "status": "success",
        "public_url": "https://storage.example.com/image.jpg",
        "file_path": "images/test.jpg"
    })

    analysis_service.supabase.insert_analysis = Mock(return_value={"status": "success"})

    with patch.object(analysis_service, '_get_recent_analyses_for_deduplication', new_callable=AsyncMock) as mock_dedup:
        mock_dedup.return_value = []

        result = await analysis_service.process_image_analysis(
            image_data=b"test_image_data",
            filename="test.jpg"
        )

        assert result["status"] == "completed"
        assert result["image_urls"]["processed"] is None
        analysis_service.supabase.upload_image.assert_called_once()


@pytest.mark.asyncio
async def test_process_image_upload_failure_fallback(analysis_service, mock_yolo_client):
    """Test fallback URLs when upload fails"""
    mock_yolo_client.detect_image = AsyncMock(return_value={
        "success": True,
        "detections": [],
        "total_detections": 0,
        "location": None,
        "camera_info": None,
        "processing_time_ms": 100
    })

    # Upload fails
    analysis_service.supabase.upload_image = Mock(return_value={
        "status": "error",
        "message": "Upload failed"
    })

    analysis_service.supabase.insert_analysis = Mock(return_value={"status": "success"})

    with patch.object(analysis_service, '_get_recent_analyses_for_deduplication', new_callable=AsyncMock) as mock_dedup:
        mock_dedup.return_value = []

        result = await analysis_service.process_image_analysis(
            image_data=b"test_image_data",
            filename="test.jpg"
        )

        assert result["status"] == "completed"
        # Should use temp fallback URL
        assert "temp/" in result["image_urls"]["original"]


@pytest.mark.asyncio
async def test_process_image_db_insert_failure_cleanup(analysis_service, mock_yolo_client):
    """Test cleanup of uploaded images when DB insert fails"""
    mock_yolo_client.detect_image = AsyncMock(return_value={
        "success": True,
        "detections": [],
        "total_detections": 0,
        "location": None,
        "camera_info": None,
        "processing_time_ms": 100
    })

    # Upload succeeds
    analysis_service.supabase.upload_image = Mock(return_value={
        "status": "success",
        "public_url": "https://storage.example.com/image.jpg",
        "file_path": "images/test.jpg"
    })

    # DB insert fails
    analysis_service.supabase.insert_analysis = Mock(return_value={
        "status": "error",
        "message": "DB insert failed"
    })

    # Mock delete_image method
    analysis_service.supabase.delete_image = Mock()

    with patch.object(analysis_service, '_get_recent_analyses_for_deduplication', new_callable=AsyncMock) as mock_dedup:
        mock_dedup.return_value = []

        result = await analysis_service.process_image_analysis(
            image_data=b"test_image_data",
            filename="test.jpg"
        )

        assert result["status"] == "failed"
        assert "Database insertion failed" in result["error"]
        # Should cleanup uploaded image
        analysis_service.supabase.delete_image.assert_called_once()


@pytest.mark.asyncio
async def test_process_image_db_insert_failure_dual_cleanup(analysis_service, mock_yolo_client):
    """Test cleanup of dual uploaded images when DB insert fails"""
    import base64

    processed_image_base64 = base64.b64encode(b"processed").decode('utf-8')

    mock_yolo_client.detect_image = AsyncMock(return_value={
        "success": True,
        "detections": [],
        "total_detections": 0,
        "location": None,
        "camera_info": None,
        "processing_time_ms": 100,
        "processed_image_base64": processed_image_base64
    })

    # Dual upload succeeds
    analysis_service.supabase.upload_dual_images = Mock(return_value={
        "status": "success",
        "original": {
            "public_url": "https://storage.example.com/original.jpg",
            "file_path": "images/original.jpg"
        },
        "processed": {
            "public_url": "https://storage.example.com/processed.jpg",
            "file_path": "images/processed.jpg"
        }
    })

    # DB insert fails
    analysis_service.supabase.insert_analysis = Mock(return_value={
        "status": "error",
        "message": "DB insert failed"
    })

    # Mock delete_image method
    analysis_service.supabase.delete_image = Mock()

    with patch.object(analysis_service, '_get_recent_analyses_for_deduplication', new_callable=AsyncMock) as mock_dedup:
        mock_dedup.return_value = []

        result = await analysis_service.process_image_analysis(
            image_data=b"test_image_data",
            filename="test.jpg"
        )

        assert result["status"] == "failed"
        # Should cleanup both images
        assert analysis_service.supabase.delete_image.call_count == 2


@pytest.mark.asyncio
async def test_process_image_with_gps_metadata_update(analysis_service, mock_yolo_client):
    """Test GPS metadata update after analysis creation"""
    mock_yolo_client.detect_image = AsyncMock(return_value={
        "success": True,
        "detections": [],
        "total_detections": 0,
        "location": {
            "has_location": True,
            "latitude": 40.7128,
            "longitude": -74.0060,
            "altitude_meters": 10.5,
            "location_source": "EXIF_GPS"
        },
        "camera_info": None,
        "processing_time_ms": 100
    })

    analysis_service.supabase.upload_image = Mock(return_value={
        "status": "success",
        "public_url": "https://storage.example.com/image.jpg",
        "file_path": "images/test.jpg"
    })

    analysis_service.supabase.insert_analysis = Mock(return_value={"status": "success"})

    # Mock GPS update
    mock_update = Mock()
    mock_update.eq = Mock(return_value=mock_update)
    mock_update.execute = Mock(return_value=Mock(data=[{"id": "test-id"}]))
    analysis_service.supabase.client.table = Mock(return_value=Mock(update=Mock(return_value=mock_update)))

    with patch.object(analysis_service, '_get_recent_analyses_for_deduplication', new_callable=AsyncMock) as mock_dedup:
        mock_dedup.return_value = []

        result = await analysis_service.process_image_analysis(
            image_data=b"test_image_data",
            filename="test.jpg",
            include_gps=True
        )

        assert result["status"] == "completed"
        assert result["has_gps_data"] is True
        # Verify GPS update was called
        analysis_service.supabase.client.table.assert_called()


@pytest.mark.asyncio
async def test_process_image_with_camera_metadata_update(analysis_service, mock_yolo_client):
    """Test camera metadata update after analysis creation"""
    mock_yolo_client.detect_image = AsyncMock(return_value={
        "success": True,
        "detections": [],
        "total_detections": 0,
        "location": None,
        "camera_info": {
            "camera_make": "Canon",
            "camera_model": "EOS R5",
            "camera_datetime": "2025-01-15T10:30:00"
        },
        "processing_time_ms": 100
    })

    analysis_service.supabase.upload_image = Mock(return_value={
        "status": "success",
        "public_url": "https://storage.example.com/image.jpg",
        "file_path": "images/test.jpg"
    })

    analysis_service.supabase.insert_analysis = Mock(return_value={"status": "success"})

    # Mock camera update
    mock_update = Mock()
    mock_update.eq = Mock(return_value=mock_update)
    mock_update.execute = Mock(return_value=Mock(data=[{"id": "test-id"}]))
    analysis_service.supabase.client.table = Mock(return_value=Mock(update=Mock(return_value=mock_update)))

    with patch.object(analysis_service, '_get_recent_analyses_for_deduplication', new_callable=AsyncMock) as mock_dedup:
        mock_dedup.return_value = []

        result = await analysis_service.process_image_analysis(
            image_data=b"test_image_data",
            filename="test.jpg"
        )

        assert result["status"] == "completed"
        assert result["camera_detected"] == "Canon"


@pytest.mark.asyncio
async def test_process_image_keyerror_exception(analysis_service, mock_yolo_client):
    """Test handling of KeyError in YOLO response"""
    # Make detect_image raise KeyError directly
    mock_yolo_client.detect_image = AsyncMock(side_effect=KeyError("detections"))

    with patch.object(analysis_service, '_get_recent_analyses_for_deduplication', new_callable=AsyncMock) as mock_dedup:
        mock_dedup.return_value = []

        with pytest.raises(YOLOServiceException) as exc_info:
            await analysis_service.process_image_analysis(
                image_data=b"test_image_data",
                filename="test.jpg"
            )

        assert "Missing required field" in str(exc_info.value)


@pytest.mark.asyncio
async def test_process_image_valueerror_exception(analysis_service, mock_yolo_client):
    """Test handling of ValueError during processing"""
    mock_yolo_client.detect_image = AsyncMock(side_effect=ValueError("Invalid confidence threshold"))

    with patch.object(analysis_service, '_get_recent_analyses_for_deduplication', new_callable=AsyncMock) as mock_dedup:
        mock_dedup.return_value = []

        with pytest.raises(ImageProcessingException) as exc_info:
            await analysis_service.process_image_analysis(
                image_data=b"test_image_data",
                filename="test.jpg"
            )

        assert "Invalid value" in str(exc_info.value)


@pytest.mark.asyncio
async def test_process_image_generic_exception(analysis_service, mock_yolo_client):
    """Test handling of generic exceptions"""
    mock_yolo_client.detect_image = AsyncMock(side_effect=RuntimeError("Unexpected error"))

    with patch.object(analysis_service, '_get_recent_analyses_for_deduplication', new_callable=AsyncMock) as mock_dedup:
        mock_dedup.return_value = []

        with pytest.raises(ImageProcessingException) as exc_info:
            await analysis_service.process_image_analysis(
                image_data=b"test_image_data",
                filename="test.jpg"
            )

        assert "Error procesando análisis" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_analysis_by_id_keyerror(analysis_service):
    """Test handling of KeyError in get_analysis_by_id"""
    # Mock response with missing field
    mock_response = Mock()
    mock_response.data = [{}]  # Missing required 'id' field

    mock_table = Mock()
    mock_table.select = Mock(return_value=mock_table)
    mock_table.eq = Mock(return_value=mock_table)
    mock_table.execute = Mock(return_value=mock_response)

    analysis_service.supabase.client.table = Mock(return_value=mock_table)

    with pytest.raises(DatabaseException) as exc_info:
        await analysis_service.get_analysis_by_id("test-id")

    assert "Missing required field" in str(exc_info.value)


@pytest.mark.asyncio
async def test_list_analyses_with_user_filter(analysis_service):
    """Test list_analyses with user_id filter"""
    mock_analyses_query = Mock()
    mock_analyses_query.select = Mock(return_value=mock_analyses_query)
    mock_analyses_query.eq = Mock(return_value=mock_analyses_query)
    mock_analyses_query.range = Mock(return_value=mock_analyses_query)
    mock_analyses_query.order = Mock(return_value=mock_analyses_query)
    mock_analyses_query.execute = Mock(return_value=Mock(data=[
        {"id": "1", "user_id": "user-123", "total_detections": 5}
    ]))

    mock_count_query = Mock()
    mock_count_query.select = Mock(return_value=mock_count_query)
    mock_count_query.eq = Mock(return_value=mock_count_query)
    mock_count_response = Mock()
    mock_count_response.count = 1  # Set as attribute, not in constructor
    mock_count_query.execute = Mock(return_value=mock_count_response)

    # Track calls to table("analyses")
    analyses_table_calls = [0]

    def table_side_effect(table_name):
        if table_name == "analyses":
            # First call for data, second for count
            analyses_table_calls[0] += 1
            if analyses_table_calls[0] == 1:
                return mock_analyses_query
            else:
                return mock_count_query
        elif table_name == "detections":
            detections_query = Mock()
            detections_query.select = Mock(return_value=detections_query)
            detections_query.in_ = Mock(return_value=detections_query)
            detections_query.execute = Mock(return_value=Mock(data=[]))
            return detections_query

    analysis_service.supabase.client.table = Mock(side_effect=table_side_effect)

    result = await analysis_service.list_analyses(user_id="user-123")

    assert result["total"] == 1
    assert len(result["analyses"]) == 1


@pytest.mark.asyncio
async def test_list_analyses_with_has_gps_filter(analysis_service):
    """Test list_analyses with has_gps filter"""
    mock_analyses_query = Mock()
    mock_analyses_query.select = Mock(return_value=mock_analyses_query)
    mock_analyses_query.eq = Mock(return_value=mock_analyses_query)
    mock_analyses_query.range = Mock(return_value=mock_analyses_query)
    mock_analyses_query.order = Mock(return_value=mock_analyses_query)
    mock_analyses_query.execute = Mock(return_value=Mock(data=[
        {"id": "1", "has_gps_data": True, "total_detections": 3}
    ]))

    mock_count_query = Mock()
    mock_count_query.select = Mock(return_value=mock_count_query)
    mock_count_query.eq = Mock(return_value=mock_count_query)
    mock_count_response = Mock()
    mock_count_response.count = 1  # Set as attribute, not in constructor
    mock_count_query.execute = Mock(return_value=mock_count_response)

    # Track calls to table("analyses")
    analyses_table_calls = [0]

    def table_side_effect(table_name):
        if table_name == "analyses":
            analyses_table_calls[0] += 1
            if analyses_table_calls[0] == 1:
                return mock_analyses_query
            else:
                return mock_count_query
        elif table_name == "detections":
            detections_query = Mock()
            detections_query.select = Mock(return_value=detections_query)
            detections_query.in_ = Mock(return_value=detections_query)
            detections_query.execute = Mock(return_value=Mock(data=[]))
            return detections_query

    analysis_service.supabase.client.table = Mock(side_effect=table_side_effect)

    result = await analysis_service.list_analyses(has_gps=True)

    assert result["total"] == 1


@pytest.mark.asyncio
async def test_list_analyses_with_detections_map(analysis_service):
    """Test list_analyses includes detections when has_gps is true"""
    mock_analyses_query = Mock()
    mock_analyses_query.select = Mock(return_value=mock_analyses_query)
    mock_analyses_query.range = Mock(return_value=mock_analyses_query)
    mock_analyses_query.order = Mock(return_value=mock_analyses_query)
    mock_analyses_query.execute = Mock(return_value=Mock(data=[
        {"id": "1", "has_gps_data": True, "total_detections": 2}
    ]))

    mock_count_query = Mock()
    mock_count_query.select = Mock(return_value=mock_count_query)
    mock_count_response = Mock()
    mock_count_response.count = 1  # Set as attribute, not in constructor
    mock_count_query.execute = Mock(return_value=mock_count_response)

    mock_detections_query = Mock()
    mock_detections_query.select = Mock(return_value=mock_detections_query)
    mock_detections_query.in_ = Mock(return_value=mock_detections_query)
    mock_detections_query.execute = Mock(return_value=Mock(data=[
        {"analysis_id": "1", "id": "det-1"},
        {"analysis_id": "1", "id": "det-2"}
    ]))

    # Track calls to table("analyses")
    analyses_table_calls = [0]

    def table_side_effect(table_name):
        if table_name == "analyses":
            analyses_table_calls[0] += 1
            if analyses_table_calls[0] == 1:
                return mock_analyses_query
            else:
                return mock_count_query
        elif table_name == "detections":
            return mock_detections_query

    analysis_service.supabase.client.table = Mock(side_effect=table_side_effect)

    result = await analysis_service.list_analyses()

    assert len(result["analyses"]) == 1
    assert len(result["analyses"][0]["detections"]) == 1  # Only first detection


@pytest.mark.asyncio
async def test_list_analyses_keyerror_exception(analysis_service):
    """Test handling of KeyError in list_analyses"""
    mock_query = Mock()
    mock_query.select = Mock(return_value=mock_query)
    mock_query.range = Mock(return_value=mock_query)
    mock_query.order = Mock(return_value=mock_query)
    mock_query.execute = Mock(return_value=Mock(data=[{}]))  # Missing 'id' field

    analysis_service.supabase.client.table = Mock(return_value=mock_query)

    with pytest.raises(DatabaseException) as exc_info:
        await analysis_service.list_analyses()

    assert "Missing required field" in str(exc_info.value)


@pytest.mark.asyncio
async def test_list_analyses_valueerror_exception(analysis_service):
    """Test handling of ValueError in list_analyses"""
    mock_query = Mock()
    mock_query.select = Mock(side_effect=ValueError("Invalid value"))

    analysis_service.supabase.client.table = Mock(return_value=mock_query)

    with pytest.raises(DatabaseException) as exc_info:
        await analysis_service.list_analyses()

    assert "Invalid value" in str(exc_info.value)
