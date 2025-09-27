"""
Comprehensive tests for YOLO-Backend integration with new image processing
Pruebas exhaustivas para la integración YOLO-Backend con nuevo procesamiento de imágenes
"""

import unittest
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import os
from io import BytesIO
from pathlib import Path
import json
import base64
import asyncio

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.services.yolo_service import YOLOServiceClient
from services.analysis_service import AnalysisService


class TestYOLOBackendIntegration(unittest.TestCase):
    """Test cases for YOLO-Backend integration"""

    def setUp(self):
        """Set up test environment"""
        self.yolo_client = YOLOServiceClient()
        self.test_image_data = self._create_test_image_data()
        self.test_filename = "IMG_1234.jpg"

    def _create_test_image_data(self):
        """Create realistic test image data"""
        # Create a small test image (1x1 pixel JPG)
        return base64.b64decode(
            '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k='
        )

    @patch('httpx.AsyncClient')
    async def test_yolo_detect_image_success(self, mock_client_class):
        """Test successful YOLO image detection"""
        # Mock successful YOLO response
        mock_response_data = {
            "analysis_id": "test-analysis-123",
            "status": "completed",
            "detections": [
                {
                    "class_name": "Basura",
                    "class_id": 0,
                    "confidence": 0.85,
                    "risk_level": "ALTO",
                    "breeding_site_type": "agua_estancada",
                    "polygon": [[100, 200], [150, 200], [150, 250], [100, 250]],
                    "mask_area": 2500.0
                }
            ],
            "total_detections": 1,
            "risk_assessment": {
                "overall_risk": "ALTO",
                "risk_score": 0.85
            },
            "location": {
                "has_location": True,
                "latitude": -34.603722,
                "longitude": -58.381592,
                "altitude_meters": 25.0,
                "location_source": "EXIF_GPS"
            },
            "camera_info": {
                "camera_make": "Apple",
                "camera_model": "iPhone 15",
                "camera_datetime": "2025:09:26 14:30:52"
            },
            "processing_time_ms": 1500,
            "model_used": "dengue_production_v2",
            "confidence_threshold": 0.5
        }

        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_client.post.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client_class.return_value = mock_client

        # Test detection
        result = await self.yolo_client.detect_image(
            image_data=self.test_image_data,
            filename=self.test_filename,
            confidence_threshold=0.5,
            include_gps=True
        )

        # Verify result structure
        self.assertTrue(result["success"])
        self.assertEqual(result["analysis_id"], "test-analysis-123")
        self.assertEqual(result["status"], "completed")
        self.assertEqual(len(result["detections"]), 1)
        self.assertEqual(result["total_detections"], 1)
        self.assertIn("risk_assessment", result)
        self.assertIn("location", result)
        self.assertIn("camera_info", result)

        # Verify detection details
        detection = result["detections"][0]
        self.assertEqual(detection["class_name"], "Basura")
        self.assertEqual(detection["confidence"], 0.85)
        self.assertEqual(detection["risk_level"], "ALTO")

    @patch('httpx.AsyncClient')
    async def test_yolo_detect_image_with_processed_image(self, mock_client_class):
        """Test YOLO detection that returns processed image data"""
        # Mock response with processed image
        mock_response_data = {
            "analysis_id": "test-analysis-123",
            "status": "completed",
            "detections": [],
            "total_detections": 0,
            "processing_time_ms": 1000,
            "processed_image_base64": base64.b64encode(b"processed_image_data").decode('utf-8')
        }

        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_client.post.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client_class.return_value = mock_client

        result = await self.yolo_client.detect_image(
            image_data=self.test_image_data,
            filename=self.test_filename
        )

        self.assertTrue(result["success"])
        # Note: processed_image_base64 would need to be handled in the actual implementation

    @patch('httpx.AsyncClient')
    async def test_yolo_connection_error(self, mock_client_class):
        """Test YOLO service connection error handling"""
        import httpx

        # Mock connection error
        mock_client = Mock()
        mock_client.post.side_effect = httpx.ConnectError("Connection failed")
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client_class.return_value = mock_client

        with self.assertRaises(Exception) as context:
            await self.yolo_client.detect_image(
                image_data=self.test_image_data,
                filename=self.test_filename
            )

        self.assertIn("Cannot connect to YOLO service", str(context.exception))

    @patch('httpx.AsyncClient')
    async def test_yolo_timeout_error(self, mock_client_class):
        """Test YOLO service timeout handling"""
        import httpx

        # Mock timeout error
        mock_client = Mock()
        mock_client.post.side_effect = httpx.TimeoutException("Request timeout")
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client_class.return_value = mock_client

        with self.assertRaises(Exception) as context:
            await self.yolo_client.detect_image(
                image_data=self.test_image_data,
                filename=self.test_filename
            )

        self.assertIn("YOLO service timeout", str(context.exception))

    @patch('httpx.AsyncClient')
    async def test_yolo_http_error_response(self, mock_client_class):
        """Test YOLO service HTTP error response handling"""
        import httpx

        # Mock HTTP error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"

        mock_client = Mock()
        mock_client.post.side_effect = httpx.HTTPStatusError(
            "Server error", request=Mock(), response=mock_response
        )
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client_class.return_value = mock_client

        with self.assertRaises(Exception) as context:
            await self.yolo_client.detect_image(
                image_data=self.test_image_data,
                filename=self.test_filename
            )

        self.assertIn("YOLO service error", str(context.exception))

    async def test_yolo_health_check(self):
        """Test YOLO service health check"""
        with patch('httpx.AsyncClient') as mock_client_class:
            # Mock successful health check
            mock_client = Mock()
            mock_response = Mock()
            mock_response.json.return_value = {
                "status": "healthy",
                "version": "1.0.0",
                "model_loaded": True
            }
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            result = await self.yolo_client.health_check()

            self.assertIn("status", result)
            self.assertEqual(result["status"], "healthy")

    async def test_yolo_get_available_models(self):
        """Test getting available models from YOLO service"""
        with patch('httpx.AsyncClient') as mock_client_class:
            # Mock models response
            mock_client = Mock()
            mock_response = Mock()
            mock_response.json.return_value = {
                "available_models": [
                    "dengue_production_v2",
                    "yolo11n-seg",
                    "yolo11s-seg"
                ],
                "current_model": "dengue_production_v2",
                "model_info": {
                    "size_mb": 87.2,
                    "classes": ["Basura", "Agua_estancada", "Contenedor"]
                }
            }
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            result = await self.yolo_client.get_available_models()

            self.assertIn("available_models", result)
            self.assertIn("current_model", result)
            self.assertEqual(len(result["available_models"]), 3)


class TestCompleteImageProcessingWorkflow(unittest.TestCase):
    """Integration tests for complete image processing workflow"""

    def setUp(self):
        """Set up complete workflow test environment"""
        self.analysis_service = AnalysisService()
        self.test_image_data = self._create_test_image_data()
        self.test_filename = "IMG_1234.jpg"

    def _create_test_image_data(self):
        """Create test image data"""
        return base64.b64decode(
            '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k='
        )

    @patch('services.analysis_service.prepare_image_for_processing')
    @patch('services.analysis_service.generate_standardized_filename')
    @patch('services.analysis_service.create_filename_variations')
    async def test_complete_workflow_success(self, mock_variations, mock_standardized, mock_prepare):
        """Test complete successful workflow from image upload to storage"""
        # Mock image preparation
        mock_prepare.return_value = (self.test_image_data, self.test_filename)

        # Mock filename generation
        standardized_filename = "SENTRIX_20250926_143052_IPHONE15_LATn34p604_LONn58p382_abc123de.jpg"
        mock_standardized.return_value = standardized_filename
        mock_variations.return_value = {
            'original': self.test_filename,
            'standardized': standardized_filename,
            'processed': f"SENTRIX_PROC_{standardized_filename}",
            'thumbnail': standardized_filename.replace('.jpg', '_thumb.jpg'),
            'analysis_id': "test-analysis-id",
            'timestamp': "2025-09-26T14:30:52"
        }

        # Mock YOLO service
        mock_yolo_response = {
            "success": True,
            "detections": [
                {
                    "class_name": "Basura",
                    "class_id": 0,
                    "confidence": 0.87,
                    "risk_level": "ALTO",
                    "polygon": [[100, 200], [150, 200], [150, 250], [100, 250]],
                    "mask_area": 2500.0
                }
            ],
            "total_detections": 1,
            "location": {
                "has_location": True,
                "latitude": -34.603722,
                "longitude": -58.381592,
                "location_source": "EXIF_GPS"
            },
            "camera_info": {
                "camera_make": "Apple",
                "camera_model": "iPhone 15"
            },
            "processing_time_ms": 1500,
            "processed_image_data": b"processed_image_binary_data"
        }

        # Mock services
        with patch.object(self.analysis_service, 'yolo_client') as mock_yolo_client, \
             patch.object(self.analysis_service, 'supabase') as mock_supabase:

            mock_yolo_client.detect_image.return_value = mock_yolo_response

            # Mock successful dual image upload
            mock_supabase.upload_dual_images.return_value = {
                "status": "success",
                "original": {
                    "file_path": "original_abc123.jpg",
                    "public_url": "https://supabase.com/storage/v1/object/public/images/original_abc123.jpg",
                    "size_bytes": len(self.test_image_data)
                },
                "processed": {
                    "file_path": "processed_abc123.jpg",
                    "public_url": "https://supabase.com/storage/v1/object/public/images/processed_abc123.jpg",
                    "size_bytes": len(mock_yolo_response["processed_image_data"])
                }
            }

            # Mock successful database operations
            mock_supabase.insert_analysis.return_value = {"status": "success"}

            # Mock database update operations
            mock_db_response = Mock()
            mock_db_response.data = [{"id": "test-analysis-id"}]
            mock_supabase.client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_db_response

            # Execute complete workflow
            result = await self.analysis_service.process_image_analysis(
                image_data=self.test_image_data,
                filename=self.test_filename,
                confidence_threshold=0.5,
                include_gps=True
            )

            # Verify complete result
            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["total_detections"], 1)
            self.assertTrue(result["has_gps_data"])
            self.assertEqual(result["camera_detected"], "Apple")

            # Verify image URLs
            self.assertIn("image_urls", result)
            self.assertEqual(
                result["image_urls"]["original"],
                "https://supabase.com/storage/v1/object/public/images/original_abc123.jpg"
            )
            self.assertEqual(
                result["image_urls"]["processed"],
                "https://supabase.com/storage/v1/object/public/images/processed_abc123.jpg"
            )

            # Verify filename standardization
            self.assertIn("filenames", result)
            self.assertEqual(result["filenames"]["original"], self.test_filename)
            self.assertEqual(result["filenames"]["standardized"], standardized_filename)

            # Verify service calls
            mock_yolo_client.detect_image.assert_called_once_with(
                image_data=self.test_image_data,
                filename=self.test_filename,
                confidence_threshold=0.5,
                include_gps=True
            )
            mock_supabase.upload_dual_images.assert_called_once()
            mock_supabase.insert_analysis.assert_called_once()

    async def test_workflow_yolo_failure(self):
        """Test workflow when YOLO service fails"""
        with patch.object(self.analysis_service, 'yolo_client') as mock_yolo_client, \
             patch('services.analysis_service.prepare_image_for_processing') as mock_prepare:

            mock_prepare.return_value = (self.test_image_data, self.test_filename)
            mock_yolo_client.detect_image.return_value = {"success": False}

            result = await self.analysis_service.process_image_analysis(
                image_data=self.test_image_data,
                filename=self.test_filename
            )

            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["error"], "YOLO processing failed")

    async def test_workflow_storage_failure_with_rollback(self):
        """Test workflow when storage fails and rollback occurs"""
        with patch.object(self.analysis_service, 'yolo_client') as mock_yolo_client, \
             patch.object(self.analysis_service, 'supabase') as mock_supabase, \
             patch('services.analysis_service.prepare_image_for_processing') as mock_prepare, \
             patch('services.analysis_service.generate_standardized_filename') as mock_standardized, \
             patch('services.analysis_service.create_filename_variations') as mock_variations:

            # Setup mocks
            mock_prepare.return_value = (self.test_image_data, self.test_filename)
            mock_standardized.return_value = "test_filename.jpg"
            mock_variations.return_value = {'standardized': 'test.jpg', 'processed': 'test_proc.jpg'}

            # Mock successful YOLO
            mock_yolo_client.detect_image.return_value = {
                "success": True,
                "detections": [],
                "location": None,
                "camera_info": None
            }

            # Mock successful image upload
            mock_supabase.upload_image.return_value = {
                "status": "success",
                "file_path": "test_abc123.jpg",
                "public_url": "https://supabase.com/test.jpg"
            }

            # Mock failed database insertion
            mock_supabase.insert_analysis.return_value = {
                "status": "error",
                "message": "Database insertion failed"
            }

            result = await self.analysis_service.process_image_analysis(
                image_data=self.test_image_data,
                filename=self.test_filename
            )

            # Should fail and trigger cleanup
            self.assertEqual(result["status"], "failed")
            self.assertEqual(result["error"], "Database insertion failed")

            # Verify cleanup was called
            mock_supabase.delete_image.assert_called_once()


class TestImageProcessingEdgeCases(unittest.TestCase):
    """Test edge cases in image processing workflow"""

    def setUp(self):
        self.analysis_service = AnalysisService()

    async def test_very_large_image_processing(self):
        """Test processing of very large images"""
        # Create large fake image data (10MB)
        large_image_data = b"x" * (10 * 1024 * 1024)

        with patch.object(self.analysis_service, 'yolo_client') as mock_yolo_client, \
             patch.object(self.analysis_service, 'supabase') as mock_supabase, \
             patch('services.analysis_service.prepare_image_for_processing') as mock_prepare:

            mock_prepare.return_value = (large_image_data, "large_image.jpg")
            mock_yolo_client.detect_image.return_value = {
                "success": True,
                "detections": [],
                "location": None,
                "camera_info": None
            }

            # Should handle large images without crashing
            result = await self.analysis_service.process_image_analysis(
                image_data=large_image_data,
                filename="large_image.jpg"
            )

            # Verify it doesn't crash
            self.assertIn("status", result)

    async def test_malformed_image_data(self):
        """Test processing of malformed image data"""
        malformed_data = b"this_is_not_an_image"

        with patch('services.analysis_service.prepare_image_for_processing') as mock_prepare:
            # Simulate preparation failure
            mock_prepare.side_effect = Exception("Invalid image format")

            with self.assertRaises(Exception):
                await self.analysis_service.process_image_analysis(
                    image_data=malformed_data,
                    filename="malformed.jpg"
                )

    async def test_concurrent_image_processing(self):
        """Test multiple concurrent image processing requests"""
        test_data = b"test_image_data"

        with patch.object(self.analysis_service, 'yolo_client') as mock_yolo_client, \
             patch.object(self.analysis_service, 'supabase') as mock_supabase, \
             patch('services.analysis_service.prepare_image_for_processing') as mock_prepare, \
             patch('services.analysis_service.generate_standardized_filename') as mock_standardized, \
             patch('services.analysis_service.create_filename_variations') as mock_variations:

            # Setup mocks
            mock_prepare.return_value = (test_data, "test.jpg")
            mock_standardized.return_value = "test_standardized.jpg"
            mock_variations.return_value = {'standardized': 'test.jpg'}
            mock_yolo_client.detect_image.return_value = {
                "success": True,
                "detections": [],
                "location": None,
                "camera_info": None
            }
            mock_supabase.upload_image.return_value = {"status": "success", "public_url": "test.jpg"}
            mock_supabase.insert_analysis.return_value = {"status": "success"}

            # Process multiple images concurrently
            tasks = []
            for i in range(5):
                task = self.analysis_service.process_image_analysis(
                    image_data=test_data,
                    filename=f"test_{i}.jpg"
                )
                tasks.append(task)

            results = await asyncio.gather(*tasks)

            # All should complete successfully
            for result in results:
                self.assertEqual(result["status"], "completed")


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)