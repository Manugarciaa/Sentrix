"""
Comprehensive tests for standardized filename generation system
Pruebas exhaustivas para el sistema de generación de nombres estandarizados
"""

import unittest
from datetime import datetime
from pathlib import Path
import sys
import os

from sentrix_shared.file_utils import (
    generate_standardized_filename,
    parse_standardized_filename,
    create_filename_variations,
    _detect_device_code,
    _format_location_code
)


class TestStandardizedNaming(unittest.TestCase):
    """Test cases for standardized filename generation"""

    def setUp(self):
        """Set up test data"""
        self.test_timestamp = datetime(2025, 9, 26, 14, 30, 52)

        self.iphone_camera_info = {
            "camera_make": "Apple",
            "camera_model": "iPhone 15",
            "camera_datetime": "2025:09:26 14:30:52"
        }

        self.samsung_camera_info = {
            "camera_make": "Samsung",
            "camera_model": "Galaxy S21",
            "camera_datetime": "2025:09:26 14:30:52"
        }

        self.canon_camera_info = {
            "camera_make": "Canon",
            "camera_model": "EOS R5",
            "camera_datetime": "2025:09:26 14:30:52"
        }

        self.gps_data_buenos_aires = {
            "has_gps": True,
            "latitude": -34.603722,
            "longitude": -58.381592
        }

        self.gps_data_positive = {
            "has_gps": True,
            "latitude": 40.7128,
            "longitude": 74.0060
        }

    def test_generate_filename_iphone_with_gps(self):
        """Test filename generation for iPhone with GPS"""
        filename = generate_standardized_filename(
            original_filename="IMG_1234.jpg",
            camera_info=self.iphone_camera_info,
            gps_data=self.gps_data_buenos_aires,
            analysis_timestamp=self.test_timestamp
        )

        self.assertTrue(filename.startswith("SENTRIX_20250926_143052_IPHONE15"))
        self.assertIn("LATn34p604", filename)
        self.assertIn("LONn58p382", filename)
        self.assertTrue(filename.endswith(".jpg"))

    def test_generate_filename_samsung_no_gps(self):
        """Test filename generation for Samsung without GPS"""
        filename = generate_standardized_filename(
            original_filename="20250926_143052.jpg",
            camera_info=self.samsung_camera_info,
            gps_data=None,
            analysis_timestamp=self.test_timestamp
        )

        self.assertTrue(filename.startswith("SENTRIX_20250926_143052_GALAXYS21"))
        self.assertIn("NOLOC", filename)
        self.assertTrue(filename.endswith(".jpg"))

    def test_generate_filename_unknown_device(self):
        """Test filename generation for unknown device"""
        filename = generate_standardized_filename(
            original_filename="random_image.png",
            camera_info=None,
            gps_data=None,
            analysis_timestamp=self.test_timestamp
        )

        self.assertTrue(filename.startswith("SENTRIX_20250926_143052_UNKNOWN"))
        self.assertIn("NOLOC", filename)
        self.assertTrue(filename.endswith(".png"))

    def test_device_detection_patterns(self):
        """Test device detection from various patterns"""
        test_cases = [
            ("IMG_1234.jpg", "IPHONE"),
            ("20250926_143052.jpg", "ANDROID"),
            ("WA0001.jpg", "WHATSAPP"),
            ("Screenshot_20250926.png", "SCREEN"),
            ("DSC_1234.jpg", "ANDROID"),
            ("random_name.jpg", "UNKNOWN")
        ]

        for filename, expected_device in test_cases:
            with self.subTest(filename=filename):
                device = _detect_device_code(None, filename)
                self.assertEqual(device, expected_device)

    def test_camera_info_device_detection(self):
        """Test device detection from camera info"""
        test_cases = [
            ({"camera_make": "Apple", "camera_model": "iPhone 15"}, "IPHONE15"),
            ({"camera_make": "Apple", "camera_model": "iPad"}, "IPAD"),
            ({"camera_make": "Samsung", "camera_model": "Galaxy S21"}, "GALAXYS21"),
            ({"camera_make": "Canon", "camera_model": "EOS R5"}, "CANON"),
            ({"camera_make": "Unknown Make", "camera_model": "Unknown"}, "UNKNOWN")
        ]

        for camera_info, expected_device in test_cases:
            with self.subTest(camera_info=camera_info):
                device = _detect_device_code(camera_info, "test.jpg")
                self.assertEqual(device, expected_device)

    def test_gps_formatting(self):
        """Test GPS coordinate formatting"""
        test_cases = [
            ({"has_gps": True, "latitude": -34.603722, "longitude": -58.381592}, "LATn34p604_LONn58p382"),
            ({"has_gps": True, "latitude": 40.7128, "longitude": 74.0060}, "LAT40p713_LON74p006"),
            ({"has_gps": True, "latitude": 0.0, "longitude": 0.0}, "LAT0p000_LON0p000"),
            ({"has_gps": False}, "NOLOC"),
            (None, "NOLOC")
        ]

        for gps_data, expected_location in test_cases:
            with self.subTest(gps_data=gps_data):
                location = _format_location_code(gps_data)
                self.assertEqual(location, expected_location)

    def test_filename_parsing(self):
        """Test parsing of standardized filenames"""
        test_filename = "SENTRIX_20250926_143052_IPHONE15_LATn34p604_LONn58p382_abc123de.jpg"

        parsed = parse_standardized_filename(test_filename)

        self.assertTrue(parsed['is_standardized'])
        self.assertEqual(parsed['project'], 'SENTRIX')
        self.assertEqual(parsed['timestamp'], self.test_timestamp)
        self.assertEqual(parsed['device'], 'IPHONE15')
        self.assertEqual(parsed['location'], 'LATn34p604_LONn58p382')
        self.assertEqual(parsed['unique_id'], 'abc123de')
        self.assertEqual(parsed['extension'], '.jpg')
        self.assertEqual(parsed['parsing_errors'], [])

    def test_filename_parsing_invalid(self):
        """Test parsing of non-standardized filenames"""
        test_cases = [
            "IMG_1234.jpg",  # Doesn't start with SENTRIX
            "SENTRIX_invalid.jpg",  # Too few parts
            "NOTSENTRIX_20250926_143052_DEVICE.jpg"  # Wrong prefix
        ]

        for filename in test_cases:
            with self.subTest(filename=filename):
                parsed = parse_standardized_filename(filename)
                self.assertFalse(parsed['is_standardized'])
                self.assertTrue(len(parsed['parsing_errors']) > 0)

    def test_filename_variations(self):
        """Test creation of filename variations"""
        variations = create_filename_variations(
            base_filename="IMG_1234.jpg",
            camera_info=self.iphone_camera_info,
            gps_data=self.gps_data_buenos_aires
        )

        self.assertEqual(variations['original'], "IMG_1234.jpg")
        self.assertTrue(variations['standardized'].startswith("SENTRIX_"))
        self.assertTrue(variations['processed'].startswith("SENTRIX_PROC_"))
        self.assertTrue(variations['thumbnail'].endswith("_thumb.jpg"))
        self.assertIsNotNone(variations['analysis_id'])
        self.assertIsNotNone(variations['timestamp'])

    def test_extension_preservation(self):
        """Test that file extensions are preserved correctly"""
        test_cases = [
            "image.jpg",
            "image.jpeg",
            "image.png",
            "image.tiff",
            "image.heic"
        ]

        for original_filename in test_cases:
            with self.subTest(filename=original_filename):
                filename = generate_standardized_filename(
                    original_filename=original_filename,
                    analysis_timestamp=self.test_timestamp
                )
                original_ext = Path(original_filename).suffix
                self.assertTrue(filename.endswith(original_ext))

    def test_unique_ids_different(self):
        """Test that multiple calls generate different unique IDs"""
        filenames = []
        for _ in range(10):
            filename = generate_standardized_filename(
                original_filename="test.jpg",
                analysis_timestamp=self.test_timestamp
            )
            filenames.append(filename)

        # All filenames should be different due to unique IDs
        self.assertEqual(len(filenames), len(set(filenames)))

    def test_timestamp_formatting(self):
        """Test timestamp formatting in filenames"""
        filename = generate_standardized_filename(
            original_filename="test.jpg",
            analysis_timestamp=self.test_timestamp
        )

        self.assertIn("20250926_143052", filename)

    def test_edge_cases_coordinates(self):
        """Test edge cases for GPS coordinates"""
        edge_cases = [
            {"has_gps": True, "latitude": 90.0, "longitude": 180.0},  # Max values
            {"has_gps": True, "latitude": -90.0, "longitude": -180.0},  # Min values
            {"has_gps": True, "latitude": 0.000001, "longitude": 0.000001},  # Very small
        ]

        for gps_data in edge_cases:
            with self.subTest(gps_data=gps_data):
                location = _format_location_code(gps_data)
                self.assertNotEqual(location, "NOLOC")
                self.assertIn("LAT", location)
                self.assertIn("LON", location)


class TestStandardizedNamingIntegration(unittest.TestCase):
    """Integration tests for the standardized naming system"""

    def test_full_workflow_iphone_photo(self):
        """Test complete workflow for iPhone photo with GPS"""
        # Simulate iPhone photo with GPS from Buenos Aires
        original_filename = "IMG_1234.HEIC"
        camera_info = {
            "camera_make": "Apple",
            "camera_model": "iPhone 15 Pro",
            "camera_datetime": "2025:09:26 14:30:52"
        }
        gps_data = {
            "has_gps": True,
            "latitude": -34.603722,
            "longitude": -58.381592,
            "altitude": 25.0
        }
        timestamp = datetime(2025, 9, 26, 14, 30, 52)

        # Generate standardized filename
        standardized = generate_standardized_filename(
            original_filename=original_filename,
            camera_info=camera_info,
            gps_data=gps_data,
            analysis_timestamp=timestamp
        )

        # Verify structure
        self.assertTrue(standardized.startswith("SENTRIX_20250926_143052"))
        self.assertIn("IPHONE15", standardized)
        self.assertIn("LATn34p604", standardized)
        self.assertIn("LONn58p382", standardized)
        # Extensions are normalized to lowercase
        self.assertTrue(standardized.endswith(".heic"))

        # Test parsing back
        parsed = parse_standardized_filename(standardized)
        self.assertTrue(parsed['is_standardized'])
        self.assertEqual(parsed['device'], 'IPHONE15')
        self.assertEqual(parsed['timestamp'], timestamp)

        # Test variations
        variations = create_filename_variations(
            base_filename=original_filename,
            camera_info=camera_info,
            gps_data=gps_data
        )

        self.assertIn('original', variations)
        self.assertIn('standardized', variations)
        self.assertIn('processed', variations)
        self.assertIn('thumbnail', variations)

    def test_batch_processing_uniqueness(self):
        """Test that batch processing generates unique filenames"""
        # Simulate processing multiple images from same device/location
        base_data = {
            "camera_info": {
                "camera_make": "Samsung",
                "camera_model": "Galaxy S21"
            },
            "gps_data": {
                "has_gps": True,
                "latitude": -34.603722,
                "longitude": -58.381592
            }
        }

        filenames = []
        for i in range(100):  # Process 100 "identical" images
            filename = generate_standardized_filename(
                original_filename=f"IMG_{i:04d}.jpg",
                camera_info=base_data["camera_info"],
                gps_data=base_data["gps_data"],
                analysis_timestamp=datetime.now()
            )
            filenames.append(filename)

        # All should be unique due to timestamps and unique IDs
        self.assertEqual(len(filenames), len(set(filenames)))


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)