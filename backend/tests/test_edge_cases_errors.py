"""
Comprehensive tests for edge cases and error handling
Pruebas exhaustivas para casos extremos y manejo de errores
"""

import unittest
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import os
from io import BytesIO
from pathlib import Path
import json
import asyncio
import uuid
from datetime import datetime

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from services.analysis_service import AnalysisService
from utils.supabase_client import SupabaseManager
from shared.file_utils import generate_standardized_filename, parse_standardized_filename


class TestEdgeCasesFilenameGeneration(unittest.TestCase):
    """Test edge cases in filename generation"""

    def test_empty_filename(self):
        """Test handling of empty filename"""
        result = generate_standardized_filename(
            original_filename="",
            analysis_timestamp=datetime(2025, 9, 26, 14, 30, 52)
        )

        self.assertTrue(result.startswith("SENTRIX_20250926_143052"))
        self.assertTrue(result.endswith(".jpg"))  # Default extension

    def test_filename_without_extension(self):
        """Test filename without extension"""
        result = generate_standardized_filename(
            original_filename="image_without_extension",
            analysis_timestamp=datetime(2025, 9, 26, 14, 30, 52)
        )

        self.assertTrue(result.startswith("SENTRIX_20250926_143052"))
        self.assertTrue(result.endswith(".jpg"))  # Default extension

    def test_filename_with_unicode_characters(self):
        """Test filename with unicode characters"""
        result = generate_standardized_filename(
            original_filename="测试图片_ñoño_🖼️.jpg",
            analysis_timestamp=datetime(2025, 9, 26, 14, 30, 52)
        )

        self.assertTrue(result.startswith("SENTRIX_20250926_143052"))
        self.assertTrue(result.endswith(".jpg"))

    def test_very_long_original_filename(self):
        """Test very long original filename"""
        long_filename = "a" * 500 + ".jpg"
        result = generate_standardized_filename(
            original_filename=long_filename,
            analysis_timestamp=datetime(2025, 9, 26, 14, 30, 52)
        )

        # Should still generate valid standardized name
        self.assertTrue(result.startswith("SENTRIX_20250926_143052"))
        self.assertTrue(result.endswith(".jpg"))
        self.assertLess(len(result), 300)  # Should be reasonable length

    def test_gps_coordinates_extreme_values(self):
        """Test GPS coordinates at extreme values"""
        extreme_cases = [
            {"has_gps": True, "latitude": 90.0, "longitude": 180.0},     # Maximum
            {"has_gps": True, "latitude": -90.0, "longitude": -180.0},   # Minimum
            {"has_gps": True, "latitude": 0.0, "longitude": 0.0},        # Zero
            {"has_gps": True, "latitude": 89.999999, "longitude": 179.999999},  # Near max
        ]

        for gps_data in extreme_cases:
            with self.subTest(gps_data=gps_data):
                result = generate_standardized_filename(
                    original_filename="test.jpg",
                    gps_data=gps_data,
                    analysis_timestamp=datetime(2025, 9, 26, 14, 30, 52)
                )

                self.assertIn("LAT", result)
                self.assertIn("LON", result)
                self.assertNotIn("NOLOC", result)

    def test_malformed_gps_data(self):
        """Test malformed GPS data"""
        malformed_cases = [
            {"has_gps": True, "latitude": "invalid", "longitude": -58.381592},
            {"has_gps": True, "latitude": -34.603722, "longitude": "invalid"},
            {"has_gps": True, "latitude": None, "longitude": -58.381592},
            {"has_gps": True, "latitude": -34.603722, "longitude": None},
            {"has_gps": True},  # Missing lat/lon
            {"latitude": -34.603722, "longitude": -58.381592},  # Missing has_gps
        ]

        for gps_data in malformed_cases:
            with self.subTest(gps_data=gps_data):
                # Should not crash, should fallback to NOLOC
                result = generate_standardized_filename(
                    original_filename="test.jpg",
                    gps_data=gps_data,
                    analysis_timestamp=datetime(2025, 9, 26, 14, 30, 52)
                )

                self.assertIn("NOLOC", result)

    def test_malformed_camera_info(self):
        """Test malformed camera info"""
        malformed_cases = [
            {"camera_make": None, "camera_model": "iPhone 15"},
            {"camera_make": "", "camera_model": "iPhone 15"},
            {"camera_make": "Apple", "camera_model": None},
            {"camera_make": "Apple", "camera_model": ""},
            {},  # Empty dict
            None,  # None value
            {"invalid_field": "value"},  # Invalid fields
        ]

        for camera_info in malformed_cases:
            with self.subTest(camera_info=camera_info):
                # Should not crash, should use fallback device detection
                result = generate_standardized_filename(
                    original_filename="IMG_1234.jpg",  # iPhone pattern
                    camera_info=camera_info,
                    analysis_timestamp=datetime(2025, 9, 26, 14, 30, 52)
                )

                # Should still generate valid filename
                self.assertTrue(result.startswith("SENTRIX_20250926_143052"))

    def test_parse_invalid_standardized_filenames(self):
        """Test parsing of invalid standardized filenames"""
        invalid_cases = [
            "IMG_1234.jpg",  # Regular filename
            "SENTRIX.jpg",   # Too few parts
            "NOTSENTRIX_20250926_143052_DEVICE.jpg",  # Wrong prefix
            "SENTRIX_invalid_timestamp_DEVICE.jpg",   # Invalid timestamp
            "SENTRIX_20250926_143052",  # No extension
            "",  # Empty string
            "SENTRIX_20250926_143052_DEVICE_LOCATION_ID_EXTRA_PARTS.jpg",  # Too many parts
        ]

        for filename in invalid_cases:
            with self.subTest(filename=filename):
                parsed = parse_standardized_filename(filename)
                self.assertFalse(parsed['is_standardized'])
                self.assertTrue(len(parsed['parsing_errors']) > 0)


class TestEdgeCasesImageStorage(unittest.TestCase):
    """Test edge cases in image storage"""

    def setUp(self):
        self.supabase_manager = SupabaseManager()
        self.mock_client = Mock()
        self.supabase_manager._client = self.mock_client

    def test_upload_zero_byte_image(self):
        """Test uploading zero-byte image"""
        result = self.supabase_manager.upload_image(
            image_data=b"",
            filename="empty.jpg"
        )

        # Should handle gracefully, either succeed or fail with clear message
        self.assertIn("status", result)

    def test_upload_extremely_large_image(self):
        """Test uploading extremely large image"""
        # Create 100MB fake image data
        large_data = b"x" * (100 * 1024 * 1024)

        # Mock potential storage limits
        mock_response = Mock()
        mock_response.status_code = 413  # Payload too large
        self.mock_client.storage.from_().upload.return_value = mock_response

        result = self.supabase_manager.upload_image(
            image_data=large_data,
            filename="huge_image.jpg"
        )

        self.assertEqual(result["status"], "error")
        self.assertIn("413", result["message"])

    def test_upload_with_invalid_bucket_name(self):
        """Test uploading to invalid bucket"""
        # Mock bucket not found error
        self.mock_client.storage.from_().upload.side_effect = Exception("Bucket not found")

        result = self.supabase_manager.upload_image(
            image_data=b"test_data",
            filename="test.jpg",
            bucket_name="nonexistent_bucket"
        )

        self.assertEqual(result["status"], "error")
        self.assertIn("Bucket not found", result["message"])

    def test_delete_nonexistent_image(self):
        """Test deleting nonexistent image"""
        # Mock file not found
        self.mock_client.storage.from_().remove.return_value = False

        result = self.supabase_manager.delete_image("nonexistent_file.jpg")

        self.assertEqual(result["status"], "error")

    def test_network_interruption_during_upload(self):
        """Test network interruption during upload"""
        # Mock network interruption
        self.mock_client.storage.from_().upload.side_effect = Exception("Connection reset by peer")

        result = self.supabase_manager.upload_image(
            image_data=b"test_data",
            filename="test.jpg"
        )

        self.assertEqual(result["status"], "error")
        self.assertIn("Connection reset", result["message"])

    def test_dual_upload_partial_failure_cleanup(self):
        """Test dual upload where second upload fails and cleanup occurs"""
        call_count = 0

        def mock_upload_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            mock_response = Mock()
            if call_count == 1:  # First upload succeeds
                mock_response.status_code = 200
            else:  # Second upload fails
                mock_response.status_code = 500
            return mock_response

        self.mock_client.storage.from_().upload.side_effect = mock_upload_side_effect
        self.mock_client.storage.from_().get_public_url.return_value = "https://test.com/image.jpg"
        self.mock_client.storage.from_().remove.return_value = True

        result = self.supabase_manager.upload_dual_images(
            original_data=b"original_data",
            processed_data=b"processed_data",
            base_filename="test.jpg"
        )

        self.assertEqual(result["status"], "error")
        # Verify cleanup was called
        self.mock_client.storage.from_().remove.assert_called_once()

    def test_concurrent_access_to_same_filename(self):
        """Test concurrent access to same filename"""
        # This should be handled by UUID generation, but test anyway
        filename = "test.jpg"

        # Mock successful uploads
        mock_response = Mock()
        mock_response.status_code = 200
        self.mock_client.storage.from_().upload.return_value = mock_response
        self.mock_client.storage.from_().get_public_url.return_value = "https://test.com/image.jpg"

        # Upload same filename multiple times
        results = []
        for i in range(10):
            result = self.supabase_manager.upload_image(
                image_data=f"data_{i}".encode(),
                filename=filename
            )
            results.append(result)

        # All should succeed with different actual filenames (due to UUID)
        for result in results:
            self.assertEqual(result["status"], "success")


class TestEdgeCasesYOLOIntegration(unittest.TestCase):
    """Test edge cases in YOLO integration"""

    def setUp(self):
        self.analysis_service = AnalysisService()

    async def test_yolo_service_returns_malformed_json(self):
        """Test handling of malformed JSON from YOLO service"""
        with patch.object(self.analysis_service, 'yolo_client') as mock_yolo_client:
            # Mock malformed response
            mock_yolo_client.detect_image.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

            with self.assertRaises(Exception):
                await self.analysis_service.process_image_analysis(
                    image_data=b"test_data",
                    filename="test.jpg"
                )

    async def test_yolo_service_returns_unexpected_structure(self):
        """Test handling of unexpected response structure"""
        with patch.object(self.analysis_service, 'yolo_client') as mock_yolo_client, \
             patch('services.analysis_service.prepare_image_for_processing') as mock_prepare:

            mock_prepare.return_value = (b"test_data", "test.jpg")

            # Mock unexpected response structure
            mock_yolo_client.detect_image.return_value = {
                "unexpected_field": "value",
                "missing_success_field": True
            }

            result = await self.analysis_service.process_image_analysis(
                image_data=b"test_data",
                filename="test.jpg"
            )

            # Should handle gracefully
            self.assertEqual(result["status"], "failed")

    async def test_yolo_detections_with_invalid_data(self):
        """Test handling of invalid detection data"""
        with patch.object(self.analysis_service, 'yolo_client') as mock_yolo_client, \
             patch.object(self.analysis_service, 'supabase') as mock_supabase, \
             patch('services.analysis_service.prepare_image_for_processing') as mock_prepare, \
             patch('services.analysis_service.generate_standardized_filename') as mock_standardized, \
             patch('services.analysis_service.create_filename_variations') as mock_variations:

            mock_prepare.return_value = (b"test_data", "test.jpg")
            mock_standardized.return_value = "test.jpg"
            mock_variations.return_value = {'standardized': 'test.jpg'}

            # Mock response with invalid detection data
            mock_yolo_client.detect_image.return_value = {
                "success": True,
                "detections": [
                    {
                        "class_name": None,  # Invalid
                        "confidence": "invalid_confidence",  # Invalid
                        "risk_level": "UNKNOWN_LEVEL"  # Invalid
                    },
                    {
                        "missing_required_fields": True
                    }
                ],
                "location": None,
                "camera_info": None
            }

            mock_supabase.upload_image.return_value = {
                "status": "success",
                "public_url": "https://test.com/image.jpg"
            }
            mock_supabase.insert_analysis.return_value = {"status": "success"}

            # Should handle invalid detection data gracefully
            result = await self.analysis_service.process_image_analysis(
                image_data=b"test_data",
                filename="test.jpg"
            )

            # Should still complete but with appropriate handling
            self.assertEqual(result["status"], "completed")

    async def test_yolo_timeout_handling(self):
        """Test handling of YOLO service timeout"""
        with patch.object(self.analysis_service, 'yolo_client') as mock_yolo_client:
            # Mock timeout
            mock_yolo_client.detect_image.side_effect = asyncio.TimeoutError("YOLO timeout")

            with self.assertRaises(Exception):
                await self.analysis_service.process_image_analysis(
                    image_data=b"test_data",
                    filename="test.jpg"
                )

    async def test_yolo_returns_huge_detection_count(self):
        """Test handling of unrealistically high detection count"""
        with patch.object(self.analysis_service, 'yolo_client') as mock_yolo_client, \
             patch.object(self.analysis_service, 'supabase') as mock_supabase, \
             patch('services.analysis_service.prepare_image_for_processing') as mock_prepare, \
             patch('services.analysis_service.generate_standardized_filename') as mock_standardized, \
             patch('services.analysis_service.create_filename_variations') as mock_variations:

            mock_prepare.return_value = (b"test_data", "test.jpg")
            mock_standardized.return_value = "test.jpg"
            mock_variations.return_value = {'standardized': 'test.jpg'}

            # Create huge number of detections
            huge_detections = []
            for i in range(1000):  # Unrealistically high
                huge_detections.append({
                    "class_name": f"Detection_{i}",
                    "confidence": 0.5,
                    "risk_level": "BAJO"
                })

            mock_yolo_client.detect_image.return_value = {
                "success": True,
                "detections": huge_detections,
                "total_detections": len(huge_detections),
                "location": None,
                "camera_info": None
            }

            mock_supabase.upload_image.return_value = {
                "status": "success",
                "public_url": "https://test.com/image.jpg"
            }
            mock_supabase.insert_analysis.return_value = {"status": "success"}

            result = await self.analysis_service.process_image_analysis(
                image_data=b"test_data",
                filename="test.jpg"
            )

            # Should handle large detection count
            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["total_detections"], 1000)


class TestDatabaseErrorHandling(unittest.TestCase):
    """Test database error handling"""

    def setUp(self):
        self.analysis_service = AnalysisService()

    async def test_database_connection_failure(self):
        """Test handling of database connection failure"""
        with patch.object(self.analysis_service, 'yolo_client') as mock_yolo_client, \
             patch.object(self.analysis_service, 'supabase') as mock_supabase, \
             patch('services.analysis_service.prepare_image_for_processing') as mock_prepare, \
             patch('services.analysis_service.generate_standardized_filename') as mock_standardized, \
             patch('services.analysis_service.create_filename_variations') as mock_variations:

            mock_prepare.return_value = (b"test_data", "test.jpg")
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
                "public_url": "https://test.com/image.jpg",
                "file_path": "test_path.jpg"
            }

            # Mock database connection failure
            mock_supabase.insert_analysis.side_effect = Exception("Database connection lost")
            mock_supabase.delete_image.return_value = {"status": "success"}

            with self.assertRaises(Exception):
                await self.analysis_service.process_image_analysis(
                    image_data=b"test_data",
                    filename="test.jpg"
                )

    async def test_database_constraint_violation(self):
        """Test handling of database constraint violations"""
        with patch.object(self.analysis_service, 'yolo_client') as mock_yolo_client, \
             patch.object(self.analysis_service, 'supabase') as mock_supabase, \
             patch('services.analysis_service.prepare_image_for_processing') as mock_prepare, \
             patch('services.analysis_service.generate_standardized_filename') as mock_standardized, \
             patch('services.analysis_service.create_filename_variations') as mock_variations:

            mock_prepare.return_value = (b"test_data", "test.jpg")
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
                "public_url": "https://test.com/image.jpg",
                "file_path": "test_path.jpg"
            }

            # Mock constraint violation (e.g., duplicate key)
            mock_supabase.insert_analysis.return_value = {
                "status": "error",
                "message": "duplicate key value violates unique constraint"
            }
            mock_supabase.delete_image.return_value = {"status": "success"}

            result = await self.analysis_service.process_image_analysis(
                image_data=b"test_data",
                filename="test.jpg"
            )

            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["error"], "Database insertion failed")

            # Verify cleanup was attempted
            mock_supabase.delete_image.assert_called_once()

    def test_supabase_client_creation_failure(self):
        """Test handling of Supabase client creation failure"""
        with patch('utils.supabase_client.create_client') as mock_create_client:
            mock_create_client.side_effect = Exception("Invalid credentials")

            with self.assertRaises(Exception):
                manager = SupabaseManager()
                _ = manager.client  # This should trigger client creation


class TestConcurrencyEdgeCases(unittest.TestCase):
    """Test edge cases in concurrent operations"""

    def setUp(self):
        self.analysis_service = AnalysisService()

    async def test_rapid_successive_requests_same_user(self):
        """Test rapid successive requests from same user"""
        with patch.object(self.analysis_service, 'yolo_client') as mock_yolo_client, \
             patch.object(self.analysis_service, 'supabase') as mock_supabase, \
             patch('services.analysis_service.prepare_image_for_processing') as mock_prepare, \
             patch('services.analysis_service.generate_standardized_filename') as mock_standardized, \
             patch('services.analysis_service.create_filename_variations') as mock_variations:

            mock_prepare.return_value = (b"test_data", "test.jpg")
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

            # Make 10 rapid requests with minimal delay
            tasks = []
            for i in range(10):
                task = self.analysis_service.process_image_analysis(
                    image_data=b"test_data",
                    filename=f"rapid_test_{i}.jpg"
                )
                tasks.append(task)

            # All should complete successfully
            results = await asyncio.gather(*tasks)

            for i, result in enumerate(results):
                self.assertEqual(result["status"], "completed",
                    f"Request {i} should complete successfully")

    async def test_memory_exhaustion_simulation(self):
        """Test behavior under simulated memory pressure"""
        with patch.object(self.analysis_service, 'yolo_client') as mock_yolo_client, \
             patch.object(self.analysis_service, 'supabase') as mock_supabase, \
             patch('services.analysis_service.prepare_image_for_processing') as mock_prepare, \
             patch('services.analysis_service.generate_standardized_filename') as mock_standardized, \
             patch('services.analysis_service.create_filename_variations') as mock_variations:

            mock_prepare.return_value = (b"test_data", "test.jpg")
            mock_standardized.return_value = "test.jpg"
            mock_variations.return_value = {'standardized': 'test.jpg'}

            # Simulate memory pressure by having operations occasionally fail
            call_count = 0
            def memory_pressure_side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count % 5 == 0:  # Every 5th call fails
                    raise MemoryError("Out of memory")
                return {
                    "success": True,
                    "detections": [],
                    "location": None,
                    "camera_info": None
                }

            mock_yolo_client.detect_image.side_effect = memory_pressure_side_effect

            # Try processing multiple images
            results = []
            for i in range(10):
                try:
                    result = await self.analysis_service.process_image_analysis(
                        image_data=b"test_data",
                        filename=f"memory_test_{i}.jpg"
                    )
                    results.append(result)
                except MemoryError:
                    results.append({"status": "memory_error"})

            # Some should succeed, some should fail due to memory pressure
            successful = [r for r in results if r.get("status") == "completed"]
            memory_errors = [r for r in results if r.get("status") == "memory_error"]

            self.assertGreater(len(successful), 0, "Some requests should succeed")
            self.assertGreater(len(memory_errors), 0, "Some requests should fail due to memory pressure")


if __name__ == '__main__':
    # Run all edge case tests with high verbosity
    unittest.main(verbosity=2)