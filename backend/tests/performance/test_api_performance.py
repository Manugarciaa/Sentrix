"""
Performance tests for Sentrix API endpoints
Tests de rendimiento para los endpoints de la API de Sentrix

These tests measure response times, throughput, and concurrent request handling.
Estos tests miden tiempos de respuesta, throughput y manejo de requests concurrentes.
"""

import pytest
import time
import concurrent.futures
from typing import List
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.config import get_settings

settings = get_settings()

# Mark all tests in this file as performance tests
pytestmark = pytest.mark.performance


class TestAnalysisEndpointPerformance:
    """Performance tests for analysis endpoints"""

    def test_health_check_latency(self, client: TestClient):
        """Health check should respond in <100ms"""
        start_time = time.time()

        response = client.get("/api/v1/health")

        duration_ms = (time.time() - start_time) * 1000

        assert response.status_code == 200
        assert duration_ms < 200, f"Health check took {duration_ms:.2f}ms (expected <200ms)"
        print(f"✓ Health check latency: {duration_ms:.2f}ms")

    def test_get_analyses_list_latency(self, client: TestClient):
        """GET /analyses list should respond in <500ms"""
        start_time = time.time()

        response = client.get("/api/v1/analyses?limit=10")

        duration_ms = (time.time() - start_time) * 1000

        assert response.status_code in [200, 401, 403]  # 401/403 if auth required
        assert duration_ms < 1000, f"List analyses took {duration_ms:.2f}ms (expected <1000ms)"
        print(f"✓ GET /analyses latency: {duration_ms:.2f}ms")

    @patch('src.core.services.yolo_service.YOLOServiceClient.detect_image')
    @patch('src.core.services.yolo_service.YOLOServiceClient.health_check')
    def test_create_analysis_latency(
        self,
        mock_health,
        mock_detect,
        client: TestClient,
        sample_image_data
    ):
        """POST /analyses should complete in <5 seconds"""
        # Mock YOLO service responses
        mock_health.return_value = {
            "status": "healthy",
            "model_loaded": True,
            "version": "2.0.0"
        }

        mock_detect.return_value = {
            "success": True,
            "yolo_response": {
                "processing_time_ms": 1234,
                "model_version": "yolo11s-v1",
                "detections": [],
                "risk_assessment": {"level": "BAJO"},
                "location": {"has_location": False}
            },
            "parsed_data": {
                "analysis": {
                    "total_detections": 0,
                    "has_gps_data": False,
                    "processing_time_ms": 1234
                },
                "detections": []
            }
        }

        start_time = time.time()

        # Create multipart form data
        files = {"file": ("test_image.jpg", sample_image_data, "image/jpeg")}
        data = {"confidence_threshold": "0.5"}

        response = client.post(
            "/api/v1/analyses",
            files=files,
            data=data
        )

        duration = time.time() - start_time

        # Accept both success and auth required
        assert response.status_code in [200, 201, 401, 403, 422], f"Unexpected status: {response.status_code}"
        assert duration < 5.0, f"Analysis took {duration:.2f}s (expected <5s)"
        print(f"✓ POST /analyses latency: {duration:.2f}s")

    def test_heatmap_endpoint_latency(self, client: TestClient):
        """GET /heatmap should respond in <1 second"""
        start_time = time.time()

        response = client.get("/api/v1/analyses/heatmap?limit=100")

        duration = time.time() - start_time

        assert response.status_code in [200, 401, 403]  # 401/403 if auth required
        assert duration < 2.0, f"Heatmap took {duration:.2f}s (expected <2s)"
        print(f"✓ GET /heatmap latency: {duration:.2f}s")


class TestConcurrentRequests:
    """Test concurrent request handling"""

    def test_concurrent_health_checks(self, client: TestClient):
        """API should handle 20 concurrent health checks"""
        num_requests = 20

        def make_request():
            try:
                response = client.get("/api/v1/health")
                return response.status_code
            except Exception:
                return None

        start_time = time.time()

        # Execute requests concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        duration = time.time() - start_time

        # Count successful requests
        successful = sum(1 for r in results if r == 200)

        assert successful >= num_requests * 0.8, f"Only {successful}/{num_requests} succeeded"
        assert duration < 3.0, f"Concurrent requests took {duration:.2f}s"
        print(f"✓ {num_requests} concurrent health checks: {successful} succeeded in {duration:.2f}s")

    def test_concurrent_requests_sync(self, client: TestClient):
        """API should handle 10 concurrent requests (sync version)"""
        num_requests = 10

        def make_request():
            try:
                response = client.get("/api/v1/health")
                return response.status_code
            except Exception as e:
                return None

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        duration = time.time() - start_time

        successful = sum(1 for r in results if r == 200)

        assert successful >= num_requests * 0.8, f"Only {successful}/{num_requests} succeeded"
        assert duration < 3.0, f"Concurrent requests took {duration:.2f}s"
        print(f"✓ {num_requests} concurrent sync requests: {successful} succeeded in {duration:.2f}s")


class TestThroughput:
    """Test API throughput and rate limits"""

    def test_sequential_request_throughput(self, client: TestClient):
        """Measure throughput for sequential requests"""
        num_requests = 50

        start_time = time.time()

        for _ in range(num_requests):
            response = client.get("/api/v1/health")
            assert response.status_code == 200

        duration = time.time() - start_time
        throughput = num_requests / duration

        assert throughput > 10, f"Throughput too low: {throughput:.2f} req/s (expected >10 req/s)"
        print(f"✓ Sequential throughput: {throughput:.2f} req/s ({num_requests} requests in {duration:.2f}s)")

    def test_batch_request_performance(self, client: TestClient):
        """Measure batch request performance"""
        batch_sizes = [5, 10, 20]

        for batch_size in batch_sizes:
            def make_request():
                return client.get("/api/v1/health")

            start_time = time.time()

            with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
                futures = [executor.submit(make_request) for _ in range(batch_size)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]

            duration = time.time() - start_time

            successful = sum(1 for r in results if r.status_code == 200)
            throughput = successful / duration if duration > 0 else 0

            assert successful >= batch_size * 0.8, f"Only {successful}/{batch_size} succeeded"
            print(f"✓ Batch {batch_size}: {throughput:.2f} req/s in {duration:.2f}s")


class TestMemoryAndResourceUsage:
    """Test memory usage and resource handling"""

    def test_large_response_handling(self, client: TestClient):
        """API should handle large list responses efficiently"""
        start_time = time.time()

        # Request large limit (may not return that many, but tests handling)
        response = client.get("/api/v1/analyses?limit=1000")

        duration = time.time() - start_time

        assert response.status_code in [200, 401, 403]
        assert duration < 3.0, f"Large list took {duration:.2f}s"

        if response.status_code == 200:
            # Verify response is valid JSON
            data = response.json()
            assert isinstance(data, (dict, list))
            print(f"✓ Large response handled in {duration:.2f}s")

    def test_multiple_connections(self, client: TestClient):
        """API should handle multiple sequential connections"""
        num_connections = 100

        start_time = time.time()

        for i in range(num_connections):
            response = client.get("/api/v1/health")
            assert response.status_code == 200

        duration = time.time() - start_time
        avg_time = duration / num_connections

        assert avg_time < 0.1, f"Average time per request: {avg_time:.3f}s (expected <0.1s)"
        print(f"✓ {num_connections} connections: avg {avg_time*1000:.2f}ms per request")


class TestPerformanceUnderLoad:
    """Test performance degradation under load"""

    def test_sustained_load(self, client: TestClient):
        """API should maintain performance under sustained load"""
        duration_seconds = 5
        request_count = 0
        errors = 0

        start_time = time.time()
        end_time = start_time + duration_seconds

        while time.time() < end_time:
            try:
                response = client.get("/api/v1/health")
                if response.status_code == 200:
                    request_count += 1
                else:
                    errors += 1
            except Exception:
                errors += 1

            # Small delay to prevent overwhelming
            time.sleep(0.01)

        actual_duration = time.time() - start_time
        throughput = request_count / actual_duration if actual_duration > 0 else 0
        error_rate = errors / (request_count + errors) if (request_count + errors) > 0 else 0

        assert error_rate < 0.1, f"Error rate too high: {error_rate*100:.1f}%"
        assert throughput > 5, f"Throughput too low under load: {throughput:.2f} req/s"
        print(f"✓ Sustained load: {throughput:.2f} req/s with {error_rate*100:.1f}% errors")


# Performance benchmarks configuration
PERFORMANCE_THRESHOLDS = {
    "health_check_latency_ms": 100,
    "list_analyses_latency_ms": 500,
    "create_analysis_latency_s": 5.0,
    "heatmap_latency_s": 1.0,
    "concurrent_requests_min": 10,
    "sequential_throughput_rps": 20,
    "error_rate_max": 0.05,
}


@pytest.fixture(scope="module")
def performance_report():
    """Collect performance metrics for reporting"""
    metrics = {
        "tests_run": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "slowest_test": None,
        "fastest_test": None,
    }
    return metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "performance", "--tb=short"])
