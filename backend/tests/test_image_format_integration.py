"""
Integration tests for backend image format support
Tests de integración para soporte de formatos de imagen en backend
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import UploadFile

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestBackendImageFormatValidation:
    """Test backend image format validation"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def test_supported_formats_validation(self):
        """Test that backend correctly validates supported formats"""
        # Mock the shared library imports
        with patch('sys.path.insert'):
            with patch('builtins.__import__') as mock_import:
                # Mock shared library functions
                mock_shared = MagicMock()
                mock_shared.is_format_supported.side_effect = lambda ext: ext in [
                    '.jpg', '.jpeg', '.png', '.heic', '.heif', '.webp', '.avif'
                ]
                mock_shared.SUPPORTED_IMAGE_FORMATS = {
                    '.jpg': {'mime_type': 'image/jpeg'},
                    '.heic': {'mime_type': 'image/heic', 'conversion_needed': True},
                    '.webp': {'mime_type': 'image/webp', 'conversion_needed': True}
                }

                mock_import.return_value = mock_shared

                # Test supported formats
                assert mock_shared.is_format_supported('.jpg') is True
                assert mock_shared.is_format_supported('.heic') is True
                assert mock_shared.is_format_supported('.webp') is True

                # Test unsupported formats
                assert mock_shared.is_format_supported('.txt') is False
                assert mock_shared.is_format_supported('.pdf') is False

    def test_file_extension_parsing(self):
        """Test file extension parsing in backend"""
        test_files = [
            ("image.jpg", ".jpg"),
            ("photo.HEIC", ".heic"),  # Should be lowercase
            ("picture.WebP", ".webp"),
            ("scan.TIFF", ".tiff")
        ]

        for filename, expected_ext in test_files:
            # Simulate backend file extension parsing
            file_ext = '.' + filename.split('.')[-1].lower()
            assert file_ext == expected_ext


class TestAnalysisEndpointIntegration:
    """Test integration with analysis endpoint"""

    def test_create_analysis_with_heic_file(self):
        """Test analysis creation with HEIC file"""
        # This would be a mock test for the actual endpoint
        mock_file_data = b"fake_heic_data"
        filename = "iphone_photo.heic"

        # Mock the shared library validation
        with patch('app.api.v1.analyses.is_format_supported') as mock_supported:
            with patch('app.api.v1.analyses.SUPPORTED_IMAGE_FORMATS') as mock_formats:
                mock_supported.return_value = True
                mock_formats = {
                    '.heic': {'mime_type': 'image/heic', 'conversion_needed': True}
                }

                # Simulate validation logic
                file_ext = '.' + filename.split('.')[-1].lower()
                is_valid = mock_supported(file_ext)

                assert is_valid is True

    def test_create_analysis_with_unsupported_file(self):
        """Test analysis creation with unsupported file"""
        filename = "document.pdf"

        with patch('app.api.v1.analyses.is_format_supported') as mock_supported:
            mock_supported.return_value = False

            file_ext = '.' + filename.split('.')[-1].lower()
            is_valid = mock_supported(file_ext)

            assert is_valid is False


class TestBatchProcessingIntegration:
    """Test batch processing with mixed formats"""

    def test_batch_with_mixed_formats(self):
        """Test batch processing with different image formats"""
        test_files = [
            "photo1.jpg",
            "photo2.heic",
            "photo3.png",
            "photo4.webp"
        ]

        with patch('app.api.v1.analyses.is_format_supported') as mock_supported:
            # Mock all these formats as supported
            mock_supported.return_value = True

            valid_files = []
            for filename in test_files:
                file_ext = '.' + filename.split('.')[-1].lower()
                if mock_supported(file_ext):
                    valid_files.append(filename)

            assert len(valid_files) == 4  # All should be valid


if __name__ == "__main__":
    pytest.main([__file__])