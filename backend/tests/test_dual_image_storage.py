"""
Comprehensive tests for dual image storage system
Pruebas exhaustivas para el sistema de almacenamiento dual de imágenes
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from io import BytesIO
from pathlib import Path
import json


from src.utils.supabase_client import SupabaseManager
from src.services.analysis_service import AnalysisService


class TestDualImageStorage(unittest.TestCase):
    """Test cases for dual image storage functionality"""

    def setUp(self):
        """Set up test environment"""
        # Create mock Supabase client
        self.mock_supabase_client = Mock()
        self.mock_storage = Mock()
        self.mock_supabase_client.storage = self.mock_storage

        # Create test image data
        self.test_image_data = b"fake_image_data_original"
        self.test_processed_data = b"fake_image_data_processed"
        self.test_filename = "SENTRIX_20250926_143052_IPHONE15_abc123de.jpg"

        # Setup SupabaseManager with mocked client
        self.supabase_manager = SupabaseManager()
        self.supabase_manager._client = self.mock_supabase_client

    def test_upload_single_image_success(self):
        """Test successful single image upload"""
        # Mock successful upload response
        mock_response = Mock()
        mock_response.status_code = 200
        self.mock_storage.from_().upload.return_value = mock_response
        self.mock_storage.from_().get_public_url.return_value = "https://supabase.com/image123.jpg"

        result = self.supabase_manager.upload_image(
            image_data=self.test_image_data,
            filename=self.test_filename
        )

        self.assertEqual(result["status"], "success")
        self.assertIn("public_url", result)
        self.assertIn("file_path", result)
        self.assertIn("size_bytes", result)
        self.assertEqual(result["size_bytes"], len(self.test_image_data))

    def test_upload_single_image_failure(self):
        """Test failed single image upload"""
        # Mock failed upload response
        mock_response = Mock()
        mock_response.status_code = 500
        self.mock_storage.from_().upload.return_value = mock_response

        result = self.supabase_manager.upload_image(
            image_data=self.test_image_data,
            filename=self.test_filename
        )

        self.assertEqual(result["status"], "error")
        self.assertIn("Upload failed", result["message"])

    def test_upload_dual_images_success(self):
        """Test successful dual image upload"""
        # Mock successful upload responses
        mock_response = Mock()
        mock_response.status_code = 200
        self.mock_storage.from_().upload.return_value = mock_response
        self.mock_storage.from_().get_public_url.side_effect = [
            "https://supabase.com/original123.jpg",
            "https://supabase.com/processed123.jpg"
        ]

        result = self.supabase_manager.upload_dual_images(
            original_data=self.test_image_data,
            processed_data=self.test_processed_data,
            base_filename=self.test_filename
        )

        self.assertEqual(result["status"], "success")
        self.assertIn("original", result)
        self.assertIn("processed", result)

        # Check original image data
        self.assertIn("public_url", result["original"])
        self.assertIn("file_path", result["original"])
        self.assertIn("size_bytes", result["original"])

        # Check processed image data
        self.assertIn("public_url", result["processed"])
        self.assertIn("file_path", result["processed"])
        self.assertIn("size_bytes", result["processed"])

    def test_upload_dual_images_original_fails(self):
        """Test dual upload when original image upload fails"""
        # Mock failed original upload
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        self.mock_storage.from_().upload.return_value = mock_response_fail

        result = self.supabase_manager.upload_dual_images(
            original_data=self.test_image_data,
            processed_data=self.test_processed_data,
            base_filename=self.test_filename
        )

        self.assertEqual(result["status"], "error")
        self.assertIn("Upload failed", result["message"])

    def test_upload_dual_images_processed_fails_with_cleanup(self):
        """Test dual upload when processed fails and original is cleaned up"""
        # Mock original success, processed failure
        upload_call_count = 0

        def mock_upload_side_effect(*args, **kwargs):
            nonlocal upload_call_count
            upload_call_count += 1

            mock_response = Mock()
            if upload_call_count == 1:  # Original succeeds
                mock_response.status_code = 200
            else:  # Processed fails
                mock_response.status_code = 500
            return mock_response

        self.mock_storage.from_().upload.side_effect = mock_upload_side_effect
        self.mock_storage.from_().get_public_url.return_value = "https://supabase.com/original123.jpg"

        # Mock delete method
        self.mock_storage.from_().remove.return_value = True

        result = self.supabase_manager.upload_dual_images(
            original_data=self.test_image_data,
            processed_data=self.test_processed_data,
            base_filename=self.test_filename
        )

        self.assertEqual(result["status"], "error")
        # Verify cleanup was called
        self.mock_storage.from_().remove.assert_called_once()

    def test_delete_image_success(self):
        """Test successful image deletion"""
        self.mock_storage.from_().remove.return_value = True

        result = self.supabase_manager.delete_image("test_file_path.jpg")

        self.assertEqual(result["status"], "success")
        self.mock_storage.from_().remove.assert_called_once_with(["test_file_path.jpg"])

    def test_delete_image_failure(self):
        """Test failed image deletion"""
        self.mock_storage.from_().remove.return_value = False

        result = self.supabase_manager.delete_image("test_file_path.jpg")

        self.assertEqual(result["status"], "error")

    def test_content_type_detection(self):
        """Test content type detection for different file extensions"""
        test_cases = [
            (".jpg", "image/jpeg"),
            (".jpeg", "image/jpeg"),
            (".png", "image/png"),
            (".gif", "image/gif"),
            (".webp", "image/webp"),
            (".tiff", "image/tiff"),
            (".bmp", "image/bmp"),
            (".unknown", "image/jpeg")  # Default
        ]

        for extension, expected_content_type in test_cases:
            with self.subTest(extension=extension):
                content_type = self.supabase_manager._get_content_type(extension)
                self.assertEqual(content_type, expected_content_type)

    def test_bytesio_image_upload(self):
        """Test uploading image from BytesIO object"""
        # Create BytesIO object
        image_bytes = BytesIO(self.test_image_data)

        # Mock successful upload
        mock_response = Mock()
        mock_response.status_code = 200
        self.mock_storage.from_().upload.return_value = mock_response
        self.mock_storage.from_().get_public_url.return_value = "https://supabase.com/image123.jpg"

        result = self.supabase_manager.upload_image(
            image_data=image_bytes,
            filename=self.test_filename
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["size_bytes"], len(self.test_image_data))


class TestDualImageStorageIntegration(unittest.TestCase):
    """Integration tests for dual image storage with analysis service"""

    def setUp(self):
        """Set up integration test environment"""
        # Mock SupabaseManager and YOLOServiceClient
        self.mock_supabase = Mock()
        self.mock_yolo_client = Mock()

        # Create analysis service with mocked dependencies
        self.analysis_service = AnalysisService()
        self.analysis_service.supabase = self.mock_supabase
        self.analysis_service.yolo_client = self.mock_yolo_client

        # Test data
        self.test_image_data = b"fake_image_data"
        self.test_filename = "IMG_1234.jpg"

    @patch('sys.path')
    @patch('sentrix_shared.file_utils.generate_standardized_filename')
    @patch('sentrix_shared.file_utils.create_filename_variations')
    async def test_process_image_with_dual_storage(self, mock_variations, mock_standardized, mock_path):
        """Test complete image processing with dual storage"""
        # Mock standardized filename generation
        mock_standardized.return_value = "SENTRIX_20250926_143052_IPHONE15_abc123de.jpg"
        mock_variations.return_value = {
            'original': self.test_filename,
            'standardized': "SENTRIX_20250926_143052_IPHONE15_abc123de.jpg",
            'processed': "SENTRIX_PROC_20250926_143052_IPHONE15_abc123de.jpg",
            'thumbnail': "SENTRIX_20250926_143052_IPHONE15_abc123de_thumb.jpg",
            'analysis_id': "test-analysis-id",
            'timestamp': "2025-09-26T14:30:52"
        }

        # Mock YOLO service response
        mock_yolo_response = {
            "success": True,
            "detections": [
                {
                    "class_name": "Basura",
                    "confidence": 0.85,
                    "risk_level": "ALTO"
                }
            ],
            "location": {
                "has_location": True,
                "latitude": -34.603722,
                "longitude": -58.381592
            },
            "camera_info": {
                "camera_make": "Apple",
                "camera_model": "iPhone 15"
            },
            "processing_time_ms": 1500,
            "processed_image_data": b"fake_processed_image_data"
        }
        self.mock_yolo_client.detect_image.return_value = mock_yolo_response

        # Mock successful dual image upload
        mock_upload_result = {
            "status": "success",
            "original": {
                "file_path": "original_abc123.jpg",
                "public_url": "https://supabase.com/original_abc123.jpg",
                "size_bytes": 1024
            },
            "processed": {
                "file_path": "processed_abc123.jpg",
                "public_url": "https://supabase.com/processed_abc123.jpg",
                "size_bytes": 1200
            }
        }
        self.mock_supabase.upload_dual_images.return_value = mock_upload_result

        # Mock successful database insertion
        self.mock_supabase.insert_analysis.return_value = {"status": "success"}

        # Mock database update calls
        mock_db_response = Mock()
        mock_db_response.data = [{"id": "test-analysis-id"}]
        self.mock_supabase.client.table().update().eq().execute.return_value = mock_db_response

        # Test the complete process
        with patch('src.services.analysis_service.prepare_image_for_processing') as mock_prepare:
            mock_prepare.return_value = (self.test_image_data, self.test_filename)

            result = await self.analysis_service.process_image_analysis(
                image_data=self.test_image_data,
                filename=self.test_filename,
                confidence_threshold=0.5,
                include_gps=True
            )

        # Verify result structure
        self.assertEqual(result["status"], "completed")
        self.assertIn("image_urls", result)
        self.assertIn("filenames", result)
        self.assertIn("filename_variations", result)

        # Verify image URLs
        self.assertEqual(result["image_urls"]["original"], "https://supabase.com/original_abc123.jpg")
        self.assertEqual(result["image_urls"]["processed"], "https://supabase.com/processed_abc123.jpg")

        # Verify filenames
        self.assertEqual(result["filenames"]["original"], self.test_filename)
        self.assertEqual(result["filenames"]["standardized"], "SENTRIX_20250926_143052_IPHONE15_abc123de.jpg")

        # Verify service calls
        self.mock_yolo_client.detect_image.assert_called_once()
        self.mock_supabase.upload_dual_images.assert_called_once()
        self.mock_supabase.insert_analysis.assert_called_once()

    async def test_process_image_upload_failure_cleanup(self):
        """Test that failed uploads trigger proper cleanup"""
        # Mock YOLO service success
        mock_yolo_response = {
            "success": True,
            "detections": [],
            "location": None,
            "camera_info": None,
            "processing_time_ms": 1000
        }
        self.mock_yolo_client.detect_image.return_value = mock_yolo_response

        # Mock failed image upload
        self.mock_supabase.upload_image.return_value = {
            "status": "error",
            "message": "Upload failed"
        }

        with patch('src.services.analysis_service.prepare_image_for_processing') as mock_prepare:
            mock_prepare.return_value = (self.test_image_data, self.test_filename)
            with patch('sentrix_shared.file_utils.generate_standardized_filename') as mock_standardized:
                mock_standardized.return_value = "test_filename.jpg"
                with patch('sentrix_shared.file_utils.create_filename_variations') as mock_variations:
                    mock_variations.return_value = {'standardized': 'test.jpg'}

                    result = await self.analysis_service.process_image_analysis(
                        image_data=self.test_image_data,
                        filename=self.test_filename
                    )

        # Should still complete but with temp URLs
        self.assertEqual(result["status"], "completed")
        self.assertTrue(result["image_urls"]["original"].startswith("temp/"))


class TestImageStorageEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for image storage"""

    def setUp(self):
        self.supabase_manager = SupabaseManager()
        self.mock_client = Mock()
        self.supabase_manager._client = self.mock_client

    def test_upload_empty_image_data(self):
        """Test uploading empty image data"""
        result = self.supabase_manager.upload_image(
            image_data=b"",
            filename="empty.jpg"
        )

        # Should handle empty data gracefully
        self.assertIn("status", result)

    def test_upload_very_large_filename(self):
        """Test uploading with very long filename"""
        long_filename = "a" * 1000 + ".jpg"
        test_data = b"test_image_data"

        # Mock successful upload
        mock_response = Mock()
        mock_response.status_code = 200
        self.mock_client.storage.from_().upload.return_value = mock_response
        self.mock_client.storage.from_().get_public_url.return_value = "https://test.com/image.jpg"

        result = self.supabase_manager.upload_image(
            image_data=test_data,
            filename=long_filename
        )

        # Should generate UUID-based filename to avoid length issues
        self.assertEqual(result["status"], "success")

    def test_upload_special_characters_filename(self):
        """Test uploading with special characters in filename"""
        special_filename = "test@#$%^&*()image.jpg"
        test_data = b"test_image_data"

        # Mock successful upload
        mock_response = Mock()
        mock_response.status_code = 200
        self.mock_client.storage.from_().upload.return_value = mock_response
        self.mock_client.storage.from_().get_public_url.return_value = "https://test.com/image.jpg"

        result = self.supabase_manager.upload_image(
            image_data=test_data,
            filename=special_filename
        )

        # Should handle special characters by generating UUID-based filename
        self.assertEqual(result["status"], "success")

    def test_network_timeout_simulation(self):
        """Test handling of network timeouts"""
        # Mock network timeout
        self.mock_client.storage.from_().upload.side_effect = Exception("Network timeout")

        result = self.supabase_manager.upload_image(
            image_data=b"test_data",
            filename="test.jpg"
        )

        self.assertEqual(result["status"], "error")
        self.assertIn("Network timeout", result["message"])


if __name__ == '__main__':
    # Run all tests with high verbosity
    unittest.main(verbosity=2)