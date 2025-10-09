"""
Performance and load tests for the new image processing system
Pruebas de rendimiento y carga para el nuevo sistema de procesamiento de imágenes
"""

import unittest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch
import psutil
import gc
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.analysis_service import AnalysisService
from utils.supabase_client import SupabaseManager


class TestPerformanceMetrics(unittest.TestCase):
    """Test performance metrics for image processing operations"""

    def setUp(self):
        """Set up performance test environment"""
        self.analysis_service = AnalysisService()
        self.test_image_data = b"fake_image_data" * 1000  # 15KB test image
        self.small_image_data = b"small_image" * 10       # ~100B test image
        self.large_image_data = b"large_image_data" * 100000  # ~1.5MB test image

    def measure_memory_usage(self, func, *args, **kwargs):
        """Measure memory usage of a function"""
        gc.collect()  # Clean up before measurement
        process = psutil.Process()

        memory_before = process.memory_info().rss / 1024 / 1024  # MB

        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = memory_after - memory_before
        execution_time = end_time - start_time

        return {
            'result': result,
            'execution_time': execution_time,
            'memory_delta': memory_delta,
            'memory_before': memory_before,
            'memory_after': memory_after
        }

    def test_filename_generation_performance(self):
        """Test performance of filename generation under load"""
        from shared.file_utils import generate_standardized_filename

        # Test data
        camera_info = {
            "camera_make": "Apple",
            "camera_model": "iPhone 15"
        }
        gps_data = {
            "has_gps": True,
            "latitude": -34.603722,
            "longitude": -58.381592
        }

        # Measure performance for bulk generation
        def generate_bulk_filenames():
            filenames = []
            for i in range(1000):
                filename = generate_standardized_filename(
                    original_filename=f"IMG_{i:04d}.jpg",
                    camera_info=camera_info,
                    gps_data=gps_data
                )
                filenames.append(filename)
            return filenames

        metrics = self.measure_memory_usage(generate_bulk_filenames)

        # Performance assertions
        self.assertLess(metrics['execution_time'], 2.0, "Filename generation should complete in under 2 seconds")
        self.assertLess(metrics['memory_delta'], 50, "Memory usage should be under 50MB")
        self.assertEqual(len(metrics['result']), 1000, "Should generate exactly 1000 filenames")

        # Verify all filenames are unique
        self.assertEqual(len(set(metrics['result'])), 1000, "All filenames should be unique")

    def test_supabase_client_connection_pooling(self):
        """Test Supabase client performance with multiple connections"""
        supabase_manager = SupabaseManager()

        def create_multiple_clients():
            clients = []
            for i in range(100):
                # This should reuse the same client instance
                client = supabase_manager.client
                clients.append(client)
            return clients

        metrics = self.measure_memory_usage(create_multiple_clients)

        # Should reuse connections efficiently
        self.assertLess(metrics['execution_time'], 1.0, "Client creation should be fast")
        self.assertLess(metrics['memory_delta'], 10, "Memory usage should be minimal for connection reuse")

    async def test_concurrent_yolo_requests_simulation(self):
        """Test simulated concurrent YOLO requests performance"""
        # Mock YOLO client to avoid actual network calls
        with patch.object(self.analysis_service, 'yolo_client') as mock_yolo_client, \
             patch.object(self.analysis_service, 'supabase') as mock_supabase, \
             patch('services.analysis_service.prepare_image_for_processing') as mock_prepare, \
             patch('services.analysis_service.generate_standardized_filename') as mock_standardized, \
             patch('services.analysis_service.create_filename_variations') as mock_variations:

            # Setup mocks for performance testing
            mock_prepare.return_value = (self.test_image_data, "test.jpg")
            mock_standardized.return_value = "standardized.jpg"
            mock_variations.return_value = {'standardized': 'test.jpg'}

            # Mock quick YOLO response
            mock_yolo_client.detect_image.return_value = {
                "success": True,
                "detections": [],
                "location": None,
                "camera_info": None,
                "processing_time_ms": 100
            }

            # Mock quick storage operations
            mock_supabase.upload_image.return_value = {
                "status": "success",
                "public_url": "https://test.com/image.jpg"
            }
            mock_supabase.insert_analysis.return_value = {"status": "success"}

            # Test concurrent processing
            async def process_single_image(image_id):
                return await self.analysis_service.process_image_analysis(
                    image_data=self.test_image_data,
                    filename=f"test_image_{image_id}.jpg"
                )

            # Measure concurrent performance
            start_time = time.time()

            # Process 50 images concurrently
            tasks = [process_single_image(i) for i in range(50)]
            results = await asyncio.gather(*tasks)

            end_time = time.time()
            total_time = end_time - start_time

            # Performance assertions
            self.assertLess(total_time, 5.0, "50 concurrent requests should complete in under 5 seconds")
            self.assertEqual(len(results), 50, "All requests should complete")

            # Verify all results are successful
            successful_results = [r for r in results if r.get("status") == "completed"]
            self.assertEqual(len(successful_results), 50, "All requests should be successful")

    def test_memory_leak_detection(self):
        """Test for memory leaks in repeated operations"""
        from shared.file_utils import generate_standardized_filename, parse_standardized_filename

        # Baseline memory measurement
        gc.collect()
        process = psutil.Process()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Perform repeated operations
        for cycle in range(10):
            filenames = []

            # Generate and parse many filenames
            for i in range(100):
                filename = generate_standardized_filename(
                    original_filename=f"test_{i}.jpg",
                    camera_info={"camera_make": "Test", "camera_model": "Camera"},
                    gps_data={"has_gps": True, "latitude": 0.0, "longitude": 0.0}
                )
                filenames.append(filename)

                # Parse it back
                parsed = parse_standardized_filename(filename)
                self.assertTrue(parsed['is_standardized'])

            # Clean up
            del filenames
            gc.collect()

            # Check memory growth
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_growth = current_memory - baseline_memory

            # Memory should not grow significantly (allow 10MB growth max)
            self.assertLess(memory_growth, 10,
                f"Cycle {cycle}: Memory growth ({memory_growth:.2f}MB) exceeds threshold")

    def test_large_image_processing_performance(self):
        """Test performance with various image sizes"""
        test_cases = [
            ("small", self.small_image_data),
            ("medium", self.test_image_data),
            ("large", self.large_image_data)
        ]

        with patch.object(self.analysis_service, 'yolo_client') as mock_yolo_client, \
             patch.object(self.analysis_service, 'supabase') as mock_supabase, \
             patch('services.analysis_service.prepare_image_for_processing') as mock_prepare, \
             patch('services.analysis_service.generate_standardized_filename') as mock_standardized, \
             patch('services.analysis_service.create_filename_variations') as mock_variations:

            # Setup mocks
            mock_standardized.return_value = "test.jpg"
            mock_variations.return_value = {'standardized': 'test.jpg'}
            mock_yolo_client.detect_image.return_value = {
                "success": True,
                "detections": [],
                "location": None,
                "camera_info": None
            }
            mock_supabase.upload_image.return_value = {
                "status": "success",
                "public_url": "https://test.com/image.jpg"
            }
            mock_supabase.insert_analysis.return_value = {"status": "success"}

            performance_results = {}

            for size_name, image_data in test_cases:
                mock_prepare.return_value = (image_data, f"{size_name}.jpg")

                async def process_image():
                    return await self.analysis_service.process_image_analysis(
                        image_data=image_data,
                        filename=f"{size_name}_test.jpg"
                    )

                # Measure performance
                start_time = time.time()
                result = asyncio.run(process_image())
                end_time = time.time()

                processing_time = end_time - start_time
                performance_results[size_name] = {
                    'processing_time': processing_time,
                    'image_size': len(image_data),
                    'success': result.get('status') == 'completed'
                }

                # Performance assertions based on image size
                if size_name == "small":
                    self.assertLess(processing_time, 0.5, "Small images should process quickly")
                elif size_name == "medium":
                    self.assertLess(processing_time, 1.0, "Medium images should process reasonably fast")
                elif size_name == "large":
                    self.assertLess(processing_time, 3.0, "Large images should still process in reasonable time")

                self.assertTrue(performance_results[size_name]['success'],
                    f"{size_name} image processing should succeed")

    def test_database_operation_performance(self):
        """Test database operation performance"""
        supabase_manager = SupabaseManager()

        # Mock database operations
        with patch.object(supabase_manager, 'client') as mock_client:
            mock_table = Mock()
            mock_client.table.return_value = mock_table
            mock_table.insert.return_value.execute.return_value.data = [{"id": "test"}]
            mock_table.update.return_value.eq.return_value.execute.return_value.data = [{"id": "test"}]
            mock_table.select.return_value.eq.return_value.execute.return_value.data = [{"id": "test"}]

            # Measure bulk database operations
            def perform_bulk_db_operations():
                results = []
                for i in range(100):
                    # Simulate analysis insertion
                    result = supabase_manager.insert_analysis({
                        "id": f"analysis_{i}",
                        "image_filename": f"image_{i}.jpg",
                        "total_detections": i % 5
                    })
                    results.append(result)
                return results

            metrics = self.measure_memory_usage(perform_bulk_db_operations)

            # Database operations should be efficient
            self.assertLess(metrics['execution_time'], 2.0,
                "100 database operations should complete in under 2 seconds")
            self.assertLess(metrics['memory_delta'], 20,
                "Database operations should not consume excessive memory")
            self.assertEqual(len(metrics['result']), 100,
                "All database operations should complete")


class TestLoadTesting(unittest.TestCase):
    """Load testing for the image processing system"""

    def setUp(self):
        self.analysis_service = AnalysisService()
        self.test_image_data = b"load_test_image_data" * 500  # ~10KB

    async def test_sustained_load_processing(self):
        """Test sustained load with continuous image processing"""
        with patch.object(self.analysis_service, 'yolo_client') as mock_yolo_client, \
             patch.object(self.analysis_service, 'supabase') as mock_supabase, \
             patch('services.analysis_service.prepare_image_for_processing') as mock_prepare, \
             patch('services.analysis_service.generate_standardized_filename') as mock_standardized, \
             patch('services.analysis_service.create_filename_variations') as mock_variations:

            # Setup mocks
            mock_prepare.return_value = (self.test_image_data, "load_test.jpg")
            mock_standardized.return_value = "standardized_load_test.jpg"
            mock_variations.return_value = {'standardized': 'load_test.jpg'}
            mock_yolo_client.detect_image.return_value = {
                "success": True,
                "detections": [],
                "location": None,
                "camera_info": None
            }
            mock_supabase.upload_image.return_value = {
                "status": "success",
                "public_url": "https://test.com/image.jpg"
            }
            mock_supabase.insert_analysis.return_value = {"status": "success"}

            # Test sustained load
            batch_size = 20
            num_batches = 5
            total_requests = batch_size * num_batches

            processing_times = []

            for batch in range(num_batches):
                batch_start_time = time.time()

                # Process batch concurrently
                tasks = []
                for i in range(batch_size):
                    request_id = batch * batch_size + i
                    task = self.analysis_service.process_image_analysis(
                        image_data=self.test_image_data,
                        filename=f"load_test_{request_id}.jpg"
                    )
                    tasks.append(task)

                # Wait for batch completion
                results = await asyncio.gather(*tasks)
                batch_end_time = time.time()

                batch_time = batch_end_time - batch_start_time
                processing_times.append(batch_time)

                # Verify all requests in batch succeeded
                successful = sum(1 for r in results if r.get('status') == 'completed')
                self.assertEqual(successful, batch_size,
                    f"Batch {batch}: All {batch_size} requests should succeed")

                # Small delay between batches to simulate realistic usage
                await asyncio.sleep(0.1)

            # Analyze performance across batches
            avg_batch_time = statistics.mean(processing_times)
            max_batch_time = max(processing_times)
            min_batch_time = min(processing_times)

            # Performance assertions
            self.assertLess(avg_batch_time, 3.0,
                f"Average batch time ({avg_batch_time:.2f}s) should be under 3 seconds")
            self.assertLess(max_batch_time, 5.0,
                f"Max batch time ({max_batch_time:.2f}s) should be under 5 seconds")

            # Performance should be consistent (max shouldn't be more than 3x min)
            performance_variance = max_batch_time / min_batch_time if min_batch_time > 0 else 1
            self.assertLess(performance_variance, 3.0,
                "Performance should be relatively consistent across batches")

    def test_concurrent_user_simulation(self):
        """Simulate multiple concurrent users"""

        async def simulate_user_session(user_id, num_images=5):
            """Simulate a user uploading multiple images"""
            results = []

            with patch.object(self.analysis_service, 'yolo_client') as mock_yolo_client, \
                 patch.object(self.analysis_service, 'supabase') as mock_supabase, \
                 patch('services.analysis_service.prepare_image_for_processing') as mock_prepare, \
                 patch('services.analysis_service.generate_standardized_filename') as mock_standardized, \
                 patch('services.analysis_service.create_filename_variations') as mock_variations:

                # Setup mocks
                mock_prepare.return_value = (self.test_image_data, f"user_{user_id}.jpg")
                mock_standardized.return_value = f"standardized_user_{user_id}.jpg"
                mock_variations.return_value = {'standardized': f'user_{user_id}.jpg'}
                mock_yolo_client.detect_image.return_value = {
                    "success": True,
                    "detections": [],
                    "location": None,
                    "camera_info": None
                }
                mock_supabase.upload_image.return_value = {
                    "status": "success",
                    "public_url": f"https://test.com/user_{user_id}_image.jpg"
                }
                mock_supabase.insert_analysis.return_value = {"status": "success"}

                for image_num in range(num_images):
                    try:
                        result = await self.analysis_service.process_image_analysis(
                            image_data=self.test_image_data,
                            filename=f"user_{user_id}_image_{image_num}.jpg"
                        )
                        results.append(result)

                        # Simulate user thinking time
                        await asyncio.sleep(0.1)

                    except Exception as e:
                        results.append({"status": "error", "error": str(e)})

            return {
                "user_id": user_id,
                "results": results,
                "success_count": sum(1 for r in results if r.get('status') == 'completed'),
                "total_images": num_images
            }

        async def run_concurrent_users():
            # Simulate 10 concurrent users, each uploading 3 images
            num_users = 10
            images_per_user = 3

            start_time = time.time()

            # Create user sessions
            user_tasks = [
                simulate_user_session(user_id, images_per_user)
                for user_id in range(num_users)
            ]

            # Run all user sessions concurrently
            user_results = await asyncio.gather(*user_tasks)

            end_time = time.time()
            total_time = end_time - start_time

            return {
                "total_time": total_time,
                "user_results": user_results,
                "total_requests": num_users * images_per_user
            }

        # Run the concurrent user simulation
        results = asyncio.run(run_concurrent_users())

        # Analyze results
        total_successful = sum(user['success_count'] for user in results['user_results'])
        total_requests = results['total_requests']
        success_rate = total_successful / total_requests if total_requests > 0 else 0

        # Performance assertions
        self.assertLess(results['total_time'], 10.0,
            "Concurrent user simulation should complete in under 10 seconds")
        self.assertGreaterEqual(success_rate, 0.95,
            f"Success rate ({success_rate:.2%}) should be at least 95%")

        # Verify each user completed their session
        for user_result in results['user_results']:
            self.assertGreaterEqual(user_result['success_count'], 2,
                f"User {user_result['user_id']} should complete at least 2 out of 3 images")


class TestPerformanceBenchmarks(unittest.TestCase):
    """Benchmark tests to establish performance baselines"""

    def test_filename_generation_benchmark(self):
        """Benchmark filename generation performance"""
        from shared.file_utils import generate_standardized_filename

        # Benchmark different scenarios
        scenarios = [
            ("simple", {"original_filename": "test.jpg"}),
            ("with_camera", {
                "original_filename": "IMG_1234.jpg",
                "camera_info": {"camera_make": "Apple", "camera_model": "iPhone 15"}
            }),
            ("with_gps", {
                "original_filename": "IMG_1234.jpg",
                "gps_data": {"has_gps": True, "latitude": -34.603722, "longitude": -58.381592}
            }),
            ("full_metadata", {
                "original_filename": "IMG_1234.jpg",
                "camera_info": {"camera_make": "Apple", "camera_model": "iPhone 15"},
                "gps_data": {"has_gps": True, "latitude": -34.603722, "longitude": -58.381592}
            })
        ]

        benchmark_results = {}

        for scenario_name, kwargs in scenarios:
            # Measure performance for 1000 iterations
            start_time = time.time()

            for i in range(1000):
                filename = generate_standardized_filename(**kwargs)
                self.assertTrue(filename.startswith("SENTRIX_"))

            end_time = time.time()
            total_time = end_time - start_time
            operations_per_second = 1000 / total_time

            benchmark_results[scenario_name] = {
                'total_time': total_time,
                'ops_per_second': operations_per_second
            }

            # Baseline performance expectations
            self.assertGreater(operations_per_second, 500,
                f"{scenario_name}: Should generate at least 500 filenames per second")

        # Print benchmark results for reference
        print("\n=== Filename Generation Benchmarks ===")
        for scenario, results in benchmark_results.items():
            print(f"{scenario}: {results['ops_per_second']:.0f} ops/sec")


if __name__ == '__main__':
    # Run performance tests with high verbosity
    unittest.main(verbosity=2)