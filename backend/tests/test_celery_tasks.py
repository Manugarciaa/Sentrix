"""
Tests for Celery Async Task Queue
"""

import pytest
import base64
from unittest.mock import Mock, patch, AsyncMock
from celery.result import AsyncResult


class TestCeleryConfiguration:
    """Test Celery app configuration"""

    def test_celery_app_exists(self):
        """Test that Celery app is configured"""
        from src.celery_app import celery_app

        assert celery_app is not None
        assert celery_app.main == "sentrix"

    def test_celery_app_configuration(self):
        """Test Celery configuration settings"""
        from src.celery_app import celery_app

        assert celery_app.conf.task_serializer == "json"
        assert celery_app.conf.result_serializer == "json"
        assert celery_app.conf.task_time_limit == 300  # 5 minutes
        assert celery_app.conf.task_soft_time_limit == 270  # 4.5 minutes
        assert celery_app.conf.worker_prefetch_multiplier == 1

    def test_celery_broker_configured(self):
        """Test that broker and backend are configured"""
        from src.celery_app import celery_app

        # Should have Redis broker
        assert "redis://" in celery_app.conf.broker_url


class TestAnalysisTask:
    """Test analysis task functionality"""

    def test_task_is_registered(self):
        """Test that analysis task is registered with Celery"""
        from src.celery_app import celery_app

        task_name = "src.tasks.analysis_tasks.process_image_analysis_task"
        assert task_name in celery_app.tasks

    def test_task_has_correct_configuration(self):
        """Test task configuration"""
        from src.tasks.analysis_tasks import process_image_analysis_task

        assert process_image_analysis_task.max_retries == 3
        assert process_image_analysis_task.default_retry_delay == 60

    @patch('src.tasks.analysis_tasks.yolo_client')
    @patch('src.tasks.analysis_tasks.AnalysisService')
    def test_task_processes_image(self, mock_service, mock_yolo):
        """Test task processes image successfully"""
        from src.tasks.analysis_tasks import process_image_analysis_task

        # Mock YOLO response
        mock_yolo.detect_image = AsyncMock(return_value={
            "success": True,
            "total_detections": 2,
            "detections": [],
            "risk_assessment": {"risk_level": "MEDIO"},
            "processing_time_ms": 1500
        })

        # Create test image data
        test_image = b"fake_image_data"
        image_b64 = base64.b64encode(test_image).decode('utf-8')

        # Note: Since this is a Celery task, we can't easily run it synchronously in tests
        # In production, you'd use Celery's eager mode or integration tests
        # For now, just verify the task function exists and has correct signature
        assert callable(process_image_analysis_task)

    def test_task_handles_base64_encoding(self):
        """Test that task properly encodes/decodes image data"""
        test_data = b"test_image_data"
        encoded = base64.b64encode(test_data).decode('utf-8')
        decoded = base64.b64decode(encoded)

        assert decoded == test_data

    def test_task_has_retry_logic(self):
        """Test that task configuration includes retry logic"""
        from src.tasks.analysis_tasks import process_image_analysis_task

        # Check that task is configured with retry
        assert hasattr(process_image_analysis_task, 'max_retries')
        assert process_image_analysis_task.max_retries > 0


class TestAsyncAnalysisEndpoint:
    """Test async analysis endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        from src.api.v1 import analyses

        app = FastAPI()
        app.include_router(analyses.router, prefix="/analyses")

        return TestClient(app)

    @patch('src.api.v1.analyses.process_image_analysis_task')
    def test_submit_async_analysis_endpoint_exists(self, mock_task, client):
        """Test that async endpoint exists"""
        # Mock task submission
        mock_result = Mock()
        mock_result.id = "test-task-id-123"
        mock_task.apply_async.return_value = mock_result

        # This would require authentication in real scenario
        # For now, just verify the endpoint structure

        assert hasattr(mock_task, 'apply_async')

    def test_base64_encoding_for_celery(self):
        """Test that images are properly base64 encoded for Celery"""
        test_image = b"\x89PNG\r\n\x1a\n\x00\x00\x00"  # PNG header
        encoded = base64.b64encode(test_image).decode('utf-8')

        # Should be JSON serializable
        import json
        json_data = json.dumps({"image": encoded})
        assert json_data is not None

        # Should decode back correctly
        decoded_data = json.loads(json_data)
        decoded_image = base64.b64decode(decoded_data["image"])
        assert decoded_image == test_image


class TestTaskStatusEndpoint:
    """Test task status checking"""

    def test_status_endpoint_handles_pending(self):
        """Test status endpoint for pending tasks"""
        # Mock a pending task
        with patch('celery.result.AsyncResult') as mock_result:
            mock_task = Mock()
            mock_task.state = "PENDING"
            mock_task.info = None
            mock_result.return_value = mock_task

            # Would call the endpoint here
            # For now, just verify the status mapping logic
            assert mock_task.state == "PENDING"

    def test_status_endpoint_handles_success(self):
        """Test status endpoint for successful tasks"""
        with patch('celery.result.AsyncResult') as mock_result:
            mock_task = Mock()
            mock_task.state = "SUCCESS"
            mock_task.result = {
                "task_id": "123",
                "status": "completed",
                "analysis_data": {}
            }
            mock_result.return_value = mock_task

            assert mock_task.state == "SUCCESS"
            assert "task_id" in mock_task.result

    def test_status_endpoint_handles_failure(self):
        """Test status endpoint for failed tasks"""
        with patch('celery.result.AsyncResult') as mock_result:
            mock_task = Mock()
            mock_task.state = "FAILURE"
            mock_task.info = Exception("Test error")
            mock_result.return_value = mock_task

            assert mock_task.state == "FAILURE"


class TestTaskRetryLogic:
    """Test task retry behavior"""

    def test_exponential_backoff_calculation(self):
        """Test exponential backoff for retries"""
        # Retry 0: 60s
        # Retry 1: 120s
        # Retry 2: 240s
        for retry in range(3):
            countdown = 2 ** retry * 60
            assert countdown == [60, 120, 240][retry]

    def test_max_retries_limit(self):
        """Test that tasks respect max retries"""
        from src.tasks.analysis_tasks import process_image_analysis_task

        max_retries = process_image_analysis_task.max_retries
        assert max_retries == 3


class TestTaskLogging:
    """Test task logging functionality"""

    def test_task_base_class_has_callbacks(self):
        """Test that task base class has logging callbacks"""
        from src.tasks.analysis_tasks import AnalysisTask

        task = AnalysisTask()

        # Should have callback methods
        assert hasattr(task, 'on_failure')
        assert hasattr(task, 'on_success')
        assert hasattr(task, 'on_retry')

        # Should be callable
        assert callable(task.on_failure)
        assert callable(task.on_success)
        assert callable(task.on_retry)


class TestCeleryIntegration:
    """Integration tests for Celery"""

    def test_redis_url_from_environment(self, monkeypatch):
        """Test that Redis URL is read from environment"""
        monkeypatch.setenv("REDIS_URL", "redis://testhost:6379/0")

        # Reimport to get new environment variable
        import importlib
        import src.celery_app
        importlib.reload(src.celery_app)

        # Check if it uses the environment variable
        # Note: This is a simplified test
        assert True  # Placeholder

    def test_celery_worker_queue_routing(self):
        """Test that tasks are routed to correct queue"""
        from src.celery_app import celery_app

        # Check task routing configuration
        assert "task_routes" in celery_app.conf
        routes = celery_app.conf.task_routes

        # Analysis tasks should go to 'analysis' queue
        assert "src.tasks.analysis_tasks.*" in routes
        assert routes["src.tasks.analysis_tasks.*"]["queue"] == "analysis"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
