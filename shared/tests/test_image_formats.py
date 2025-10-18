"""
Tests for image format support and conversion
Tests para soporte y conversión de formatos de imagen
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from sentrix_shared.image_formats import (
    ImageFormatConverter,
    SUPPORTED_IMAGE_FORMATS,
    is_format_supported,
    get_format_info,
    needs_conversion
)
from sentrix_shared.file_utils import validate_image_file, process_image_with_conversion


class TestImageFormatSupport:
    """Test basic image format support functions"""

    def test_is_format_supported(self):
        """Test format support detection"""
        # Supported formats
        assert is_format_supported('.jpg')
        assert is_format_supported('.jpeg')
        assert is_format_supported('.png')
        assert is_format_supported('.heic')
        assert is_format_supported('.heif')
        assert is_format_supported('.webp')

        # Case insensitive
        assert is_format_supported('.HEIC')
        assert is_format_supported('.JPG')

        # Unsupported formats (but .gif is actually supported in LEGACY_IMAGE_FORMATS)
        assert not is_format_supported('.txt')
        assert not is_format_supported('.pdf')
        assert not is_format_supported('.doc')

    def test_get_format_info(self):
        """Test format information retrieval"""
        # HEIC format
        heic_info = get_format_info('.heic')
        assert heic_info is not None
        assert heic_info['mime_type'] == 'image/heic'
        assert heic_info['conversion_needed'] is True
        assert 'iPhone' in heic_info['common_source']

        # JPEG format
        jpeg_info = get_format_info('.jpg')
        assert jpeg_info is not None
        assert jpeg_info['mime_type'] == 'image/jpeg'
        assert jpeg_info['conversion_needed'] is False

    def test_needs_conversion(self):
        """Test conversion necessity detection"""
        assert needs_conversion('.heic') is True
        assert needs_conversion('.heif') is True
        assert needs_conversion('.webp') is True
        assert needs_conversion('.avif') is True

        assert needs_conversion('.jpg') is False
        assert needs_conversion('.jpeg') is False
        assert needs_conversion('.png') is False


class TestImageFormatConverter:
    """Test ImageFormatConverter class"""

    @pytest.fixture(autouse=True)
    def setup_method_fixture(self, tmp_path):
        """Setup method using pytest tmp_path fixture"""
        self.converter = ImageFormatConverter()
        self.temp_dir = tmp_path

    def test_converter_initialization(self):
        """Test converter initialization"""
        converter = ImageFormatConverter()
        assert converter is not None

    def test_check_dependencies(self):
        """Test dependency checking"""
        converter = ImageFormatConverter()
        deps = converter.check_dependencies()

        assert isinstance(deps, dict)
        assert 'pillow' in deps
        assert 'pillow-heif' in deps

        # pillow should always be available
        assert deps['pillow'] is True

    @patch('PIL.Image')
    def test_convert_heic_to_jpeg_success(self, mock_image):
        """Test successful HEIC to JPEG conversion"""
        # Setup mocks
        mock_img = MagicMock()
        mock_img.mode = 'RGB'
        mock_img.size = (100, 100)
        mock_img.format = 'HEIC'
        mock_img.info = {}
        mock_img.save = MagicMock()
        mock_image.open.return_value = mock_img

        # Create temp files
        temp_heic = Path(self.temp_dir) / "test.heic"
        temp_heic.touch()

        with patch.object(self.converter, 'pillow_heif_available', True):
            with patch.object(self.converter, 'pillow_available', True):
                result = self.converter.convert_image(str(temp_heic), target_format='.jpg')

                assert result is not None
                # Result should be BytesIO object
                from io import BytesIO
                assert isinstance(result, BytesIO)

    @patch('PIL.Image')
    def test_convert_image_no_conversion_needed(self, mock_image):
        """Test convert_image with JPEG format (still converts to ensure consistency)"""
        # Setup mocks
        mock_img = MagicMock()
        mock_img.mode = 'RGB'
        mock_img.size = (100, 100)
        mock_img.format = 'JPEG'
        mock_img.info = {}
        mock_img.save = MagicMock()
        mock_image.open.return_value = mock_img

        # Create temp JPEG file
        temp_jpeg = Path(self.temp_dir) / "test.jpg"
        temp_jpeg.touch()

        with patch.object(self.converter, 'pillow_available', True):
            result = self.converter.convert_image(str(temp_jpeg), target_format='.jpg')

            # Should still return BytesIO even for JPEG (ensures consistent output format)
            from io import BytesIO
            assert isinstance(result, BytesIO)

    def test_convert_image_missing_dependencies(self):
        """Test convert_image with missing Pillow dependency"""
        temp_heic = Path(self.temp_dir) / "test.heic"
        temp_heic.touch()

        with patch.object(self.converter, 'pillow_available', False):
            from sentrix_shared.error_handling import ImageProcessingError

            with pytest.raises(ImageProcessingError, match="PIL/Pillow required"):
                self.converter.convert_image(str(temp_heic), target_format='.jpg')


class TestFileUtilsIntegration:
    """Test integration with file_utils"""

    @pytest.fixture(autouse=True)
    def setup_method_fixture(self, tmp_path):
        """Setup method using pytest tmp_path fixture"""
        self.temp_dir = tmp_path

    def test_validate_image_file_with_supported_format(self):
        """Test image validation with supported formats"""
        # Create temp JPEG file
        temp_jpeg = Path(self.temp_dir) / "test.jpg"
        temp_jpeg.write_bytes(b"fake_jpeg_data")

        result = validate_image_file(temp_jpeg)

        assert result['is_valid'] is True
        assert result['extension'] == '.jpg'
        assert result['conversion_needed'] is False

    def test_validate_image_file_with_heic_format(self):
        """Test image validation with HEIC format"""
        # Create temp HEIC file
        temp_heic = Path(self.temp_dir) / "test.heic"
        temp_heic.write_bytes(b"fake_heic_data")

        result = validate_image_file(temp_heic)

        assert result['extension'] == '.heic'
        assert result['conversion_needed'] is True
        assert result['format_info'] is not None
        assert result['format_info']['mime_type'] == 'image/heic'

    @patch('sentrix_shared.file_utils.ImageFormatConverter')
    def test_process_image_with_conversion_success(self, mock_converter_class):
        """Test successful image processing with conversion"""
        # Setup mock converter
        mock_converter = MagicMock()
        mock_converter_class.return_value = mock_converter
        mock_converter.convert_image.return_value = Path(self.temp_dir) / "converted.jpg"

        # Create temp HEIC file
        temp_heic = Path(self.temp_dir) / "test.heic"
        temp_heic.write_bytes(b"fake_heic_data")

        with patch('sentrix_shared.file_utils.validate_image_file') as mock_validate:
            mock_validate.return_value = {
                'is_valid': True,
                'conversion_needed': True,
                'format_info': {'mime_type': 'image/heic'}
            }

            result = process_image_with_conversion(temp_heic)

            assert result['success'] is True
            assert result['conversion_performed'] is True
            assert result['processed_path'].endswith('converted.jpg')

    def test_process_image_with_conversion_no_conversion_needed(self):
        """Test image processing without conversion needed"""
        # Create temp JPEG file
        temp_jpeg = Path(self.temp_dir) / "test.jpg"
        temp_jpeg.write_bytes(b"fake_jpeg_data")

        with patch('sentrix_shared.file_utils.validate_image_file') as mock_validate:
            mock_validate.return_value = {
                'is_valid': True,
                'conversion_needed': False,
                'format_info': {'mime_type': 'image/jpeg'}
            }

            result = process_image_with_conversion(temp_jpeg)

            assert result['success'] is True
            assert result['conversion_performed'] is False
            assert result['processed_path'] == str(temp_jpeg)


class TestHeicConversionFunction:
    """Test standalone HEIC conversion function"""

    @pytest.fixture(autouse=True)
    def setup_method_fixture(self, tmp_path):
        """Setup method using pytest tmp_path fixture"""
        self.temp_dir = tmp_path

    @patch('PIL.Image')
    def test_converter_convert_heic(self, mock_image):
        """Test converter HEIC conversion"""
        # Setup mocks
        mock_img = MagicMock()
        mock_img.mode = 'RGB'
        mock_img.size = (100, 100)
        mock_img.format = 'HEIC'
        mock_img.info = {}
        mock_img.save = MagicMock()
        mock_image.open.return_value = mock_img

        # Create temp files
        temp_heic = Path(self.temp_dir) / "test.heic"
        temp_heic.touch()

        converter = ImageFormatConverter()

        with patch.object(converter, 'pillow_heif_available', True):
            with patch.object(converter, 'pillow_available', True):
                output = converter.convert_image(str(temp_heic), target_format='.jpg')

                assert output is not None
                # Output should be BytesIO object
                from io import BytesIO
                assert isinstance(output, BytesIO)


if __name__ == "__main__":
    pytest.main([__file__])