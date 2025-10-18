"""
Pytest configuration and fixtures for Sentrix Backend tests
Configuración de pytest y fixtures para tests del backend de Sentrix
"""

import os
import sys
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


from app import app
from src.config import get_settings

# Try to import database components (optional, not all tests need them)
try:
    from src.database import get_db
    from src.database.models.base import Base
    HAS_DATABASE = True
except ImportError:
    get_db = None
    Base = None
    HAS_DATABASE = False

# Test database URL (SQLite for tests)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine only if database is available
if HAS_DATABASE:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine = None
    TestingSessionLocal = None


def override_get_db():
    """Override database dependency for testing"""
    if not HAS_DATABASE or not TestingSessionLocal:
        raise RuntimeError("Database not configured for testing")
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    if not HAS_DATABASE:
        pytest.skip("Database not configured")

    # Create the database tables
    Base.metadata.create_all(bind=engine)

    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    yield TestingSessionLocal()

    # Clean up
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """Create a test client for FastAPI app"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for FastAPI app"""
    async with AsyncClient(app=app, base_url="http://test") as async_test_client:
        yield async_test_client


@pytest.fixture(scope="function")
def mock_yolo_service(monkeypatch):
    """Mock YOLO service responses for testing"""

    mock_detection_response = {
        "success": True,
        "processing_time_ms": 1234,
        "model_version": "yolo11s-v1",
        "source": "test_image.jpg",
        "timestamp": "2025-09-19T10:30:00.123456",
        "camera_info": {
            "camera_make": "TestCamera",
            "camera_model": "TestModel",
            "datetime_original": "2025:09:19 10:30:00",
            "software": "TestSoftware"
        },
        "location": {
            "has_location": True,
            "latitude": -26.831314,
            "longitude": -65.195539,
            "coordinates": "-26.831314,-65.195539",
            "altitude_meters": 458.2,
            "location_source": "EXIF_GPS"
        },
        "detections": [
            {
                "class_id": 0,
                "class_name": "Basura",
                "confidence": 0.75,
                "risk_level": "MEDIO",
                "polygon": [[100, 100], [200, 100], [200, 200], [100, 200]],
                "mask_area": 10000.0,
                "location": {
                    "has_location": True,
                    "latitude": -26.831314,
                    "longitude": -65.195539,
                    "backend_integration": {
                        "breeding_site_type": "Basura",
                        "verification_urls": {
                            "google_maps": "https://maps.google.com/?q=-26.831314,-65.195539"
                        }
                    }
                }
            }
        ],
        "risk_assessment": {
            "level": "MEDIO",
            "high_risk_sites": 0,
            "medium_risk_sites": 1,
            "recommendations": ["Test recommendation"]
        }
    }

    async def mock_detect_image(*args, **kwargs):
        return {
            "success": True,
            "yolo_response": mock_detection_response,
            "parsed_data": {
                "analysis": {
                    "total_detections": 1,
                    "has_gps_data": True,
                    "processing_time_ms": 1234
                },
                "detections": [
                    {
                        "class_id": 0,
                        "class_name": "Basura",
                        "confidence": 0.75,
                        "risk_level": "MEDIO",
                        "breeding_site_type": "Basura",
                        "has_location": True
                    }
                ]
            }
        }

    async def mock_health_check():
        return {
            "status": "healthy",
            "model_loaded": True,
            "gpu_available": False,
            "version": "2.0.0"
        }

    # Patch the YOLO service client methods
    try:
        from src.core.services.yolo_service import YOLOServiceClient
        monkeypatch.setattr(YOLOServiceClient, "detect_image", mock_detect_image)
        monkeypatch.setattr(YOLOServiceClient, "health_check", mock_health_check)
    except ImportError:
        # YOLO service not available, tests will need to mock directly
        pass

    return mock_detection_response


@pytest.fixture
def sample_image_data():
    """Sample image data for testing"""
    # Create a minimal valid JPEG header for testing
    jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00'
    return jpeg_header + b'\x00' * 1000  # Pad to make it look like a real image


@pytest.fixture
def sample_analysis_data():
    """Sample analysis data for testing"""
    return {
        "image_filename": "test_image.jpg",
        "has_gps_data": True,
        "total_detections": 1,
        "risk_level": "MEDIUM",
        "confidence_threshold": 0.5
    }


@pytest.fixture
def sample_detection_data():
    """Sample detection data for testing"""
    return {
        "class_id": 0,
        "class_name": "Basura",
        "confidence": 0.75,
        "risk_level": "MEDIO",
        "breeding_site_type": "Basura",
        "polygon": [[100, 100], [200, 100], [200, 200], [100, 200]],
        "mask_area": 10000.0,
        "has_location": True,
        "detection_latitude": -26.831314,
        "detection_longitude": -65.195539
    }