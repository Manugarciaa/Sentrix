"""
Integration tests for YOLO service image processing with format conversion
Tests de integración para procesamiento de imágenes con conversión de formatos
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.evaluator import assess_dengue_risk, process_image_for_detection


class TestYoloImageProcessingIntegration:
    """Test YOLO service integration with image format conversion"""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()

    def test_process_image_for_detection_jpeg(self):
        """Test processing JPEG image (no conversion needed)"""
        # Create mock JPEG file
        temp_jpeg = Path(self.temp_dir) / "test.jpg"
        temp_jpeg.write_bytes(b"fake_jpeg_content")

        with patch('src.core.evaluator.validate_image_file') as mock_validate:
            mock_validate.return_value = {
                'is_valid': True,
                'format_info': {'mime_type': 'image/jpeg', 'description': 'JPEG'},
                'conversion_needed': False
            }

            with patch('src.core.evaluator.process_image_with_conversion') as mock_process:
                mock_process.return_value = {
                    'success': True,
                    'processed_path': str(temp_jpeg),
                    'conversion_performed': False,
                    'errors': []
                }

                result = process_image_for_detection(str(temp_jpeg))

                assert result['success'] is True
                assert result['conversion_performed'] is False
                assert result['processed_path'] == str(temp_jpeg)

    def test_process_image_for_detection_heic(self):
        """Test processing HEIC image (conversion needed)"""
        # Create mock HEIC file
        temp_heic = Path(self.temp_dir) / "test.heic"
        temp_heic.write_bytes(b"fake_heic_content")

        converted_path = str(Path(self.temp_dir) / "test_converted.jpg")

        with patch('src.core.evaluator.validate_image_file') as mock_validate:
            mock_validate.return_value = {
                'is_valid': True,
                'format_info': {
                    'mime_type': 'image/heic',
                    'description': 'High Efficiency Image Container',
                    'conversion_needed': True
                },
                'conversion_needed': True
            }

            with patch('src.core.evaluator.process_image_with_conversion') as mock_process:
                mock_process.return_value = {
                    'success': True,
                    'processed_path': converted_path,
                    'conversion_performed': True,
                    'errors': []
                }

                result = process_image_for_detection(str(temp_heic))

                assert result['success'] is True
                assert result['conversion_performed'] is True
                assert result['processed_path'] == converted_path
                assert result['original_format']['mime_type'] == 'image/heic'

    def test_process_image_for_detection_invalid_file(self):
        """Test processing invalid image file"""
        temp_file = Path(self.temp_dir) / "invalid.txt"
        temp_file.write_text("not an image")

        with patch('src.core.evaluator.validate_image_file') as mock_validate:
            mock_validate.return_value = {
                'is_valid': False,
                'errors': ['Unsupported extension: .txt']
            }

            result = process_image_for_detection(str(temp_file))

            assert result['success'] is False
            assert 'Unsupported extension: .txt' in result['errors']

    def test_process_image_for_detection_conversion_error(self):
        """Test processing when conversion fails"""
        temp_heic = Path(self.temp_dir) / "test.heic"
        temp_heic.write_bytes(b"fake_heic_content")

        with patch('src.core.evaluator.validate_image_file') as mock_validate:
            mock_validate.return_value = {
                'is_valid': True,
                'format_info': {'mime_type': 'image/heic'},
                'conversion_needed': True
            }

            with patch('src.core.evaluator.process_image_with_conversion') as mock_process:
                mock_process.return_value = {
                    'success': False,
                    'errors': ['Conversion failed: Missing dependencies']
                }

                result = process_image_for_detection(str(temp_heic))

                assert result['success'] is False
                assert 'Conversion failed: Missing dependencies' in result['errors']


class TestRiskAssessmentIntegration:
    """Test risk assessment integration"""

    def test_assess_dengue_risk_basic(self):
        """Test basic risk assessment functionality"""
        detections = [
            {'class': 'Charcos/Cumulo de agua', 'confidence': 0.9},
            {'class': 'Basura', 'confidence': 0.8}
        ]

        with patch('src.core.evaluator.shared_assess_dengue_risk') as mock_assess:
            mock_assess.return_value = {
                'level': 'ALTO',
                'score': 8.5,
                'recommendations': ['Eliminar agua estancada']
            }

            result = assess_dengue_risk(detections)

            assert result['level'] == 'ALTO'
            assert result['score'] == 8.5
            assert len(result['recommendations']) > 0
            mock_assess.assert_called_once_with(detections)


if __name__ == "__main__":
    pytest.main([__file__])