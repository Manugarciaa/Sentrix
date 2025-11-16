"""
Unit tests for validators
Tests for analysis_validators.py functions
"""

import pytest
from fastapi import HTTPException, UploadFile
from io import BytesIO

from src.validators.analysis_validators import (
    validate_upload_file,
    validate_file_extension,
    validate_file_size,
    validate_coordinates,
    validate_confidence_threshold,
    validate_batch_size,
    validate_analysis_request
)


def create_mock_upload_file(filename: str, content: bytes = b"test") -> UploadFile:
    """Helper to create mock UploadFile"""
    return UploadFile(filename=filename, file=BytesIO(content))


class TestValidateUploadFile:
    """Test file upload validation"""

    def test_valid_file(self):
        """Test validation passes for valid file"""
        file = create_mock_upload_file("test.jpg")
        validate_upload_file(file)  # Should not raise

    def test_none_file(self):
        """Test validation fails for None file"""
        with pytest.raises(HTTPException) as exc_info:
            validate_upload_file(None)
        assert exc_info.value.status_code == 400
        assert "imagen" in exc_info.value.detail.lower()

    def test_file_without_filename(self):
        """Test validation fails for file without filename"""
        file = UploadFile(filename="", file=BytesIO(b"test"))
        with pytest.raises(HTTPException) as exc_info:
            validate_upload_file(file)
        assert exc_info.value.status_code == 400
        assert "nombre" in exc_info.value.detail.lower()

    def test_file_with_none_filename(self):
        """Test validation fails for file with None filename"""
        file = UploadFile(filename=None, file=BytesIO(b"test"))
        with pytest.raises(HTTPException) as exc_info:
            validate_upload_file(file)
        assert exc_info.value.status_code == 400


class TestValidateFileExtension:
    """Test file extension validation"""

    def test_valid_jpg_extension(self):
        """Test validation passes for .jpg"""
        result = validate_file_extension("image.jpg")
        assert result == ".jpg"

    def test_valid_jpeg_extension(self):
        """Test validation passes for .jpeg"""
        result = validate_file_extension("image.jpeg")
        assert result == ".jpeg"

    def test_valid_png_extension(self):
        """Test validation passes for .png"""
        result = validate_file_extension("image.png")
        assert result == ".png"

    def test_valid_heic_extension(self):
        """Test validation passes for .heic"""
        result = validate_file_extension("image.heic")
        assert result == ".heic"

    def test_uppercase_extension(self):
        """Test uppercase extension is lowercased"""
        result = validate_file_extension("image.JPG")
        assert result == ".jpg"

    def test_mixed_case_extension(self):
        """Test mixed case extension is lowercased"""
        result = validate_file_extension("image.JpEg")
        assert result == ".jpeg"

    def test_invalid_extension(self):
        """Test validation fails for unsupported extension"""
        with pytest.raises(HTTPException) as exc_info:
            validate_file_extension("document.pdf")
        assert exc_info.value.status_code == 400
        assert "no soportado" in exc_info.value.detail.lower()

    def test_no_extension(self):
        """Test validation fails for file without extension"""
        with pytest.raises(HTTPException) as exc_info:
            validate_file_extension("imagefile")
        assert exc_info.value.status_code == 400

    def test_extension_with_multiple_dots(self):
        """Test file with multiple dots"""
        result = validate_file_extension("my.image.file.png")
        assert result == ".png"


class TestValidateFileSize:
    """Test file size validation"""

    def test_valid_small_file(self):
        """Test validation passes for small file"""
        image_data = b"x" * 1024  # 1KB
        validate_file_size(image_data)  # Should not raise

    def test_valid_medium_file(self):
        """Test validation passes for medium file (5MB)"""
        image_data = b"x" * (5 * 1024 * 1024)  # 5MB
        validate_file_size(image_data)  # Should not raise

    def test_file_exceeds_default_max_size(self):
        """Test validation fails for file exceeding default max size"""
        # Assuming default max is 10MB, create 11MB file
        image_data = b"x" * (11 * 1024 * 1024)
        with pytest.raises(HTTPException) as exc_info:
            validate_file_size(image_data)
        assert exc_info.value.status_code == 413
        assert "grande" in exc_info.value.detail.lower()

    def test_file_exceeds_custom_max_size(self):
        """Test validation fails with custom max size"""
        image_data = b"x" * (2 * 1024 * 1024)  # 2MB
        max_size = 1 * 1024 * 1024  # 1MB max
        with pytest.raises(HTTPException) as exc_info:
            validate_file_size(image_data, max_size=max_size)
        assert exc_info.value.status_code == 413

    def test_file_exactly_at_max_size(self):
        """Test validation passes for file exactly at max size"""
        max_size = 1024
        image_data = b"x" * max_size
        validate_file_size(image_data, max_size=max_size)  # Should not raise

    def test_empty_file(self):
        """Test validation passes for empty file"""
        validate_file_size(b"")  # Should not raise


class TestValidateCoordinates:
    """Test GPS coordinates validation"""

    def test_both_coordinates_provided(self):
        """Test validation passes when both coordinates provided"""
        validate_coordinates(-26.831314, -65.195539)  # Should not raise

    def test_both_coordinates_none(self):
        """Test validation passes when both coordinates are None"""
        validate_coordinates(None, None)  # Should not raise

    def test_only_latitude_provided(self):
        """Test validation fails when only latitude provided"""
        with pytest.raises(HTTPException) as exc_info:
            validate_coordinates(-26.831314, None)
        assert exc_info.value.status_code == 400
        assert "latitud" in exc_info.value.detail.lower() or "latitude" in exc_info.value.detail.lower()

    def test_only_longitude_provided(self):
        """Test validation fails when only longitude provided"""
        with pytest.raises(HTTPException) as exc_info:
            validate_coordinates(None, -65.195539)
        assert exc_info.value.status_code == 400
        assert "longitud" in exc_info.value.detail.lower() or "longitude" in exc_info.value.detail.lower()

    def test_zero_coordinates(self):
        """Test validation passes for zero coordinates"""
        validate_coordinates(0.0, 0.0)  # Should not raise

    def test_positive_coordinates(self):
        """Test validation passes for positive coordinates"""
        validate_coordinates(40.7128, 74.0060)  # Should not raise

    def test_extreme_latitude(self):
        """Test validation passes for extreme latitude values"""
        validate_coordinates(90.0, 0.0)  # North Pole
        validate_coordinates(-90.0, 0.0)  # South Pole


class TestValidateConfidenceThreshold:
    """Test confidence threshold validation"""

    def test_valid_threshold_min(self):
        """Test validation passes for minimum threshold"""
        validate_confidence_threshold(0.1)  # Should not raise

    def test_valid_threshold_max(self):
        """Test validation passes for maximum threshold"""
        validate_confidence_threshold(1.0)  # Should not raise

    def test_valid_threshold_mid(self):
        """Test validation passes for middle threshold"""
        validate_confidence_threshold(0.5)  # Should not raise

    def test_threshold_too_low(self):
        """Test validation fails for threshold below minimum"""
        with pytest.raises(HTTPException) as exc_info:
            validate_confidence_threshold(0.05)
        assert exc_info.value.status_code == 400
        assert "0.1" in exc_info.value.detail
        assert "1.0" in exc_info.value.detail

    def test_threshold_too_high(self):
        """Test validation fails for threshold above maximum"""
        with pytest.raises(HTTPException) as exc_info:
            validate_confidence_threshold(1.1)
        assert exc_info.value.status_code == 400

    def test_threshold_zero(self):
        """Test validation fails for zero threshold"""
        with pytest.raises(HTTPException) as exc_info:
            validate_confidence_threshold(0.0)
        assert exc_info.value.status_code == 400

    def test_threshold_negative(self):
        """Test validation fails for negative threshold"""
        with pytest.raises(HTTPException) as exc_info:
            validate_confidence_threshold(-0.5)
        assert exc_info.value.status_code == 400

    def test_threshold_exactly_at_boundary(self):
        """Test validation at exact boundaries"""
        validate_confidence_threshold(0.1)  # Min boundary
        validate_confidence_threshold(1.0)  # Max boundary


class TestValidateBatchSize:
    """Test batch size validation"""

    def test_valid_batch_size_small(self):
        """Test validation passes for small batch"""
        validate_batch_size(5)  # Should not raise

    def test_valid_batch_size_max_default(self):
        """Test validation passes for max default batch size"""
        validate_batch_size(50)  # Should not raise

    def test_batch_size_exceeds_default(self):
        """Test validation fails for batch exceeding default max"""
        with pytest.raises(HTTPException) as exc_info:
            validate_batch_size(51)
        assert exc_info.value.status_code == 400
        assert "50" in exc_info.value.detail

    def test_batch_size_exceeds_custom_max(self):
        """Test validation fails with custom max size"""
        with pytest.raises(HTTPException) as exc_info:
            validate_batch_size(11, max_size=10)
        assert exc_info.value.status_code == 400
        assert "10" in exc_info.value.detail

    def test_batch_size_one(self):
        """Test validation passes for single item batch"""
        validate_batch_size(1)  # Should not raise

    def test_batch_size_zero(self):
        """Test validation passes for zero batch (edge case)"""
        validate_batch_size(0)  # Should not raise (validation doesn't check lower bound)

    def test_custom_max_size(self):
        """Test validation with custom max size"""
        validate_batch_size(100, max_size=100)  # Should not raise
        with pytest.raises(HTTPException):
            validate_batch_size(101, max_size=100)


class TestValidateAnalysisRequest:
    """Test complete analysis request validation"""

    def test_valid_complete_request(self):
        """Test validation passes for valid complete request"""
        file = create_mock_upload_file("test.jpg", b"x" * 1024)
        validate_analysis_request(
            file=file,
            latitude=-26.831314,
            longitude=-65.195539,
            confidence_threshold=0.7,
            image_data=b"x" * 1024
        )  # Should not raise

    def test_valid_request_without_coordinates(self):
        """Test validation passes without coordinates"""
        file = create_mock_upload_file("test.png")
        validate_analysis_request(
            file=file,
            latitude=None,
            longitude=None,
            confidence_threshold=0.5
        )  # Should not raise

    def test_valid_request_without_image_data(self):
        """Test validation passes without image data for size check"""
        file = create_mock_upload_file("test.jpg")
        validate_analysis_request(
            file=file,
            latitude=None,
            longitude=None,
            confidence_threshold=0.6
        )  # Should not raise

    def test_request_fails_on_invalid_file(self):
        """Test validation fails for invalid file"""
        with pytest.raises(HTTPException):
            validate_analysis_request(
                file=None,
                latitude=None,
                longitude=None,
                confidence_threshold=0.5
            )

    def test_request_fails_on_invalid_extension(self):
        """Test validation fails for invalid file extension"""
        file = create_mock_upload_file("document.pdf")
        with pytest.raises(HTTPException):
            validate_analysis_request(
                file=file,
                latitude=None,
                longitude=None,
                confidence_threshold=0.5
            )

    def test_request_fails_on_incomplete_coordinates(self):
        """Test validation fails for incomplete coordinates"""
        file = create_mock_upload_file("test.jpg")
        with pytest.raises(HTTPException):
            validate_analysis_request(
                file=file,
                latitude=-26.831314,
                longitude=None,  # Missing longitude
                confidence_threshold=0.5
            )

    def test_request_fails_on_invalid_threshold(self):
        """Test validation fails for invalid threshold"""
        file = create_mock_upload_file("test.jpg")
        with pytest.raises(HTTPException):
            validate_analysis_request(
                file=file,
                latitude=None,
                longitude=None,
                confidence_threshold=1.5  # Invalid
            )

    def test_request_fails_on_oversized_file(self):
        """Test validation fails for oversized file"""
        file = create_mock_upload_file("test.jpg")
        large_data = b"x" * (11 * 1024 * 1024)  # 11MB
        with pytest.raises(HTTPException):
            validate_analysis_request(
                file=file,
                latitude=None,
                longitude=None,
                confidence_threshold=0.5,
                image_data=large_data
            )

    def test_request_with_heic_file(self):
        """Test validation passes for HEIC file"""
        file = create_mock_upload_file("photo.heic")
        validate_analysis_request(
            file=file,
            latitude=None,
            longitude=None,
            confidence_threshold=0.7
        )  # Should not raise

    def test_request_with_minimum_threshold(self):
        """Test validation passes with minimum threshold"""
        file = create_mock_upload_file("test.jpg")
        validate_analysis_request(
            file=file,
            latitude=None,
            longitude=None,
            confidence_threshold=0.1
        )  # Should not raise

    def test_request_with_maximum_threshold(self):
        """Test validation passes with maximum threshold"""
        file = create_mock_upload_file("test.jpg")
        validate_analysis_request(
            file=file,
            latitude=None,
            longitude=None,
            confidence_threshold=1.0
        )  # Should not raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
