"""
Tests for file validation utilities

Tests security features:
- MIME type validation
- File size limits
- Filename sanitization
"""

import pytest
import io
from fastapi import UploadFile, HTTPException
from unittest.mock import patch, MagicMock

from src.utils.file_validation import (
    sanitize_filename,
    validate_file_extension,
    validate_file_content,
    validate_uploaded_image,
    is_image_file,
    get_safe_temp_filename
)


class TestSanitizeFilename:
    """Tests for filename sanitization"""

    def test_sanitize_simple_filename(self):
        """Test sanitizing a simple valid filename"""
        result = sanitize_filename("test.jpg")
        assert result == "test.jpg"

    def test_sanitize_path_traversal(self):
        """Test preventing path traversal attacks"""
        result = sanitize_filename("../../etc/passwd.jpg")
        assert result == "etc_passwd.jpg"
        assert ".." not in result

    def test_sanitize_special_characters(self):
        """Test removing special characters"""
        result = sanitize_filename("my<script>alert('xss')</script>.jpg")
        assert "<" not in result
        assert ">" not in result
        assert "script" in result  # Letters should remain

    def test_sanitize_spaces(self):
        """Test handling spaces"""
        result = sanitize_filename("my file name.jpg")
        assert result == "my_file_name.jpg"

    def test_sanitize_hidden_file(self):
        """Test preventing hidden files"""
        result = sanitize_filename(".hidden.jpg")
        assert not result.startswith(".")
        assert result == "hidden.jpg"

    def test_sanitize_long_filename(self):
        """Test truncating very long filenames"""
        long_name = "a" * 300 + ".jpg"
        result = sanitize_filename(long_name)
        assert len(result) <= 255

    def test_sanitize_unicode_characters(self):
        """Test handling unicode characters"""
        result = sanitize_filename("café_résumé_日本.jpg")
        # Should replace non-ASCII characters
        assert result.endswith(".jpg")


class TestValidateFileExtension:
    """Tests for file extension validation"""

    def test_valid_jpg_extension(self):
        """Test accepting valid .jpg extension"""
        result = validate_file_extension("test.jpg")
        assert result == ".jpg"

    def test_valid_jpeg_extension(self):
        """Test accepting valid .jpeg extension"""
        result = validate_file_extension("test.jpeg")
        assert result == ".jpeg"

    def test_valid_png_extension(self):
        """Test accepting valid .png extension"""
        result = validate_file_extension("test.png")
        assert result == ".png"

    def test_case_insensitive(self):
        """Test extension validation is case-insensitive"""
        result = validate_file_extension("test.JPG")
        assert result == ".jpg"

    def test_invalid_extension(self):
        """Test rejecting invalid extension"""
        with pytest.raises(HTTPException) as exc_info:
            validate_file_extension("malware.exe")
        assert exc_info.value.status_code == 400
        assert "Unsupported file extension" in exc_info.value.detail

    def test_no_extension(self):
        """Test rejecting file without extension"""
        with pytest.raises(HTTPException) as exc_info:
            validate_file_extension("noextension")
        assert exc_info.value.status_code == 400
        assert "must have an extension" in exc_info.value.detail


class TestValidateFileContent:
    """Tests for file content validation"""

    @pytest.mark.asyncio
    async def test_file_too_large(self):
        """Test rejecting files that are too large"""
        # Create a file larger than max_size
        large_content = b"x" * (51 * 1024 * 1024)  # 51MB

        file = UploadFile(
            filename="large.jpg",
            file=io.BytesIO(large_content)
        )

        with pytest.raises(HTTPException) as exc_info:
            await validate_file_content(file, max_size=50 * 1024 * 1024)

        assert exc_info.value.status_code == 413
        assert "too large" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_valid_size_file(self):
        """Test accepting files within size limit"""
        # Create a small valid file
        content = b"x" * (1 * 1024 * 1024)  # 1MB

        file = UploadFile(
            filename="small.jpg",
            file=io.BytesIO(content)
        )

        # Mock python-magic to return valid MIME type
        with patch('src.utils.file_validation.magic.from_buffer', return_value='image/jpeg'):
            result = await validate_file_content(file)
            assert result == content

    @pytest.mark.asyncio
    async def test_invalid_mime_type(self):
        """Test rejecting files with invalid MIME type"""
        # Create a file with executable content
        content = b"MZ\x90\x00"  # PE executable header

        file = UploadFile(
            filename="fake.jpg",  # Pretending to be an image
            file=io.BytesIO(content)
        )

        # Mock python-magic to detect actual MIME type
        with patch('src.utils.file_validation.magic.from_buffer', return_value='application/x-msdownload'):
            with pytest.raises(HTTPException) as exc_info:
                await validate_file_content(file)

            assert exc_info.value.status_code == 400
            assert "Invalid file type" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_valid_jpeg_mime_type(self):
        """Test accepting valid JPEG MIME type"""
        # JPEG file header
        content = b"\xff\xd8\xff" + b"x" * 1000

        file = UploadFile(
            filename="image.jpg",
            file=io.BytesIO(content)
        )

        with patch('src.utils.file_validation.magic.from_buffer', return_value='image/jpeg'):
            result = await validate_file_content(file)
            assert result == content

    @pytest.mark.asyncio
    async def test_valid_png_mime_type(self):
        """Test accepting valid PNG MIME type"""
        # PNG file header
        content = b"\x89PNG\r\n\x1a\n" + b"x" * 1000

        file = UploadFile(
            filename="image.png",
            file=io.BytesIO(content)
        )

        with patch('src.utils.file_validation.magic.from_buffer', return_value='image/png'):
            result = await validate_file_content(file)
            assert result == content

    @pytest.mark.asyncio
    async def test_mime_detection_failure(self):
        """Test handling MIME detection failure"""
        content = b"corrupted data"

        file = UploadFile(
            filename="corrupt.jpg",
            file=io.BytesIO(content)
        )

        # Mock magic to raise exception
        with patch('src.utils.file_validation.magic.from_buffer', side_effect=Exception("Magic failed")):
            with pytest.raises(HTTPException) as exc_info:
                await validate_file_content(file)

            assert exc_info.value.status_code == 400
            assert "Could not determine file type" in exc_info.value.detail


class TestValidateUploadedImage:
    """Tests for complete image validation"""

    @pytest.mark.asyncio
    async def test_no_file_provided(self):
        """Test error when no file provided"""
        with pytest.raises(HTTPException) as exc_info:
            await validate_uploaded_image(None)

        assert exc_info.value.status_code == 400
        assert "No file provided" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_file_without_name(self):
        """Test error when file has no name"""
        file = UploadFile(filename="", file=io.BytesIO(b"content"))

        with pytest.raises(HTTPException) as exc_info:
            await validate_uploaded_image(file)

        assert exc_info.value.status_code == 400
        assert "no name" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_successful_validation(self):
        """Test successful complete validation"""
        content = b"\xff\xd8\xff" + b"x" * 1000  # JPEG header + data

        file = UploadFile(
            filename="test_image.jpg",
            file=io.BytesIO(content)
        )

        with patch('src.utils.file_validation.magic.from_buffer', return_value='image/jpeg'):
            result_content, safe_filename = await validate_uploaded_image(file)

            assert result_content == content
            assert safe_filename == "test_image.jpg"

    @pytest.mark.asyncio
    async def test_filename_sanitization_in_validation(self):
        """Test that filename is sanitized during validation"""
        content = b"\xff\xd8\xff" + b"x" * 1000

        file = UploadFile(
            filename="../../etc/passwd.jpg",
            file=io.BytesIO(content)
        )

        with patch('src.utils.file_validation.magic.from_buffer', return_value='image/jpeg'):
            result_content, safe_filename = await validate_uploaded_image(file)

            assert ".." not in safe_filename
            assert safe_filename == "etc_passwd.jpg"


class TestUtilityFunctions:
    """Tests for utility functions"""

    def test_is_image_file_true(self):
        """Test identifying image files"""
        assert is_image_file("test.jpg") is True
        assert is_image_file("test.png") is True
        assert is_image_file("test.JPEG") is True

    def test_is_image_file_false(self):
        """Test identifying non-image files"""
        assert is_image_file("test.exe") is False
        assert is_image_file("test.pdf") is False
        assert is_image_file("test.txt") is False

    def test_get_safe_temp_filename(self):
        """Test generating safe temporary filename"""
        result = get_safe_temp_filename("test.jpg")

        assert result.startswith("upload_")
        assert result.endswith(".jpg")
        assert len(result) > len("test.jpg")  # Includes timestamp and UUID

    def test_get_safe_temp_filename_sanitizes(self):
        """Test that temp filename is sanitized"""
        result = get_safe_temp_filename("../../etc/passwd.jpg")

        assert ".." not in result
        assert result.endswith(".jpg")


class TestSecurityScenarios:
    """Integration tests for security scenarios"""

    @pytest.mark.asyncio
    async def test_executable_disguised_as_image(self):
        """Test blocking executable disguised as image"""
        # PE executable header
        exe_content = b"MZ\x90\x00" + b"\x00" * 1000

        file = UploadFile(
            filename="malware.jpg",  # Fake extension
            file=io.BytesIO(exe_content)
        )

        # Mock to detect actual MIME type
        with patch('src.utils.file_validation.magic.from_buffer', return_value='application/x-msdownload'):
            with pytest.raises(HTTPException) as exc_info:
                await validate_uploaded_image(file)

            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_zip_bomb_size_limit(self):
        """Test blocking very large files (zip bomb scenario)"""
        # Simulate reading a huge file
        huge_size = 100 * 1024 * 1024  # 100MB

        file = UploadFile(
            filename="zipbomb.jpg",
            file=io.BytesIO(b"x" * huge_size)
        )

        with pytest.raises(HTTPException) as exc_info:
            await validate_uploaded_image(file, max_size=50 * 1024 * 1024)

        assert exc_info.value.status_code == 413

    @pytest.mark.asyncio
    async def test_path_traversal_attack(self):
        """Test preventing path traversal in filename"""
        content = b"\xff\xd8\xff" + b"x" * 1000

        file = UploadFile(
            filename="../../../etc/passwd",
            file=io.BytesIO(content)
        )

        with patch('src.utils.file_validation.magic.from_buffer', return_value='image/jpeg'):
            _, safe_filename = await validate_uploaded_image(file)

            # Should not contain path separators
            assert "/" not in safe_filename
            assert "\\" not in safe_filename
            assert ".." not in safe_filename


# Fixtures for common test data

@pytest.fixture
def valid_jpeg_content():
    """JPEG file content"""
    return b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 1000


@pytest.fixture
def valid_png_content():
    """PNG file content"""
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * 1000


@pytest.fixture
def mock_upload_file():
    """Factory for creating mock UploadFile objects"""
    def _create(filename: str, content: bytes):
        return UploadFile(
            filename=filename,
            file=io.BytesIO(content)
        )
    return _create
