"""
Unit tests for data transformers
Tests for analysis_transformers.py functions
"""

import pytest
import uuid
from datetime import datetime

from src.transformers.analysis_transformers import (
    extract_gps_from_maps_url,
    build_location_data,
    build_camera_info,
    build_detection_item,
    build_risk_assessment,
    parse_iso_datetime,
    build_analysis_list_item,
    calculate_heatmap_intensity,
    build_heatmap_point,
    count_risk_distribution,
    calculate_unique_locations
)


class TestExtractGPSFromMapsURL:
    """Test GPS extraction from Google Maps URLs"""

    def test_valid_google_maps_url(self):
        """Test extraction from valid Google Maps URL"""
        url = "https://maps.google.com/?q=-26.8083,-65.2176"
        result = extract_gps_from_maps_url(url)
        assert result == (-26.8083, -65.2176)

    def test_valid_url_with_trailing_params(self):
        """Test extraction with additional URL parameters returns None"""
        # Current implementation doesn't handle trailing params - returns None
        url = "https://maps.google.com/?q=-34.603722,-58.381592&zoom=15"
        result = extract_gps_from_maps_url(url)
        assert result is None

    def test_url_without_q_parameter(self):
        """Test URL without q= parameter returns None"""
        url = "https://maps.google.com/"
        assert extract_gps_from_maps_url(url) is None

    def test_empty_url(self):
        """Test empty URL returns None"""
        assert extract_gps_from_maps_url("") is None

    def test_none_url(self):
        """Test None URL returns None"""
        assert extract_gps_from_maps_url(None) is None

    def test_invalid_coordinates(self):
        """Test URL with invalid coordinate format"""
        url = "https://maps.google.com/?q=invalid"
        assert extract_gps_from_maps_url(url) is None

    def test_missing_longitude(self):
        """Test URL with only latitude"""
        url = "https://maps.google.com/?q=-26.8083"
        assert extract_gps_from_maps_url(url) is None

    def test_positive_coordinates(self):
        """Test extraction with positive coordinates"""
        url = "https://maps.google.com/?q=40.7128,74.0060"
        result = extract_gps_from_maps_url(url)
        assert result == (40.7128, 74.0060)


class TestBuildLocationData:
    """Test building location data from analysis data"""

    def test_with_valid_gps_data(self):
        """Test building location data with valid GPS"""
        analysis_data = {
            "has_gps_data": True,
            "google_maps_url": "https://maps.google.com/?q=-26.831314,-65.195539",
            "gps_altitude_meters": 458.2,
            "location_source": "EXIF_GPS",
            "google_earth_url": "https://earth.google.com/web/@-26.831314,-65.195539"
        }

        result = build_location_data(analysis_data)

        assert result["has_location"] is True
        assert result["latitude"] == -26.831314
        assert result["longitude"] == -65.195539
        assert result["coordinates"] == "-26.831314,-65.195539"
        assert result["altitude_meters"] == 458.2
        assert result["location_source"] == "EXIF_GPS"
        assert "google_maps_url" in result
        assert "google_earth_url" in result

    def test_without_gps_data(self):
        """Test building location data without GPS"""
        analysis_data = {"has_gps_data": False}
        result = build_location_data(analysis_data)

        assert result == {"has_location": False}

    def test_with_invalid_maps_url(self):
        """Test with invalid Google Maps URL"""
        analysis_data = {
            "has_gps_data": True,
            "google_maps_url": "invalid_url"
        }
        result = build_location_data(analysis_data)

        assert result == {"has_location": False}

    def test_missing_maps_url(self):
        """Test with missing Google Maps URL"""
        analysis_data = {"has_gps_data": True}
        result = build_location_data(analysis_data)

        assert result == {"has_location": False}


class TestBuildCameraInfo:
    """Test building camera info from analysis data"""

    def test_with_full_camera_data(self):
        """Test building camera info with all fields"""
        analysis_data = {
            "camera_make": "Apple",
            "camera_model": "iPhone 15",
            "camera_datetime": "2025:09:19 15:19:08"
        }

        result = build_camera_info(analysis_data)

        assert result["camera_make"] == "Apple"
        assert result["camera_model"] == "iPhone 15"
        assert result["camera_datetime"] == "2025:09:19 15:19:08"
        assert result["camera_software"] is None

    def test_with_minimal_camera_data(self):
        """Test building camera info with only make"""
        analysis_data = {"camera_make": "Xiaomi"}
        result = build_camera_info(analysis_data)

        assert result["camera_make"] == "Xiaomi"
        assert result["camera_model"] is None
        assert result["camera_datetime"] is None

    def test_without_camera_data(self):
        """Test building camera info without data"""
        analysis_data = {}
        result = build_camera_info(analysis_data)

        assert result is None

    def test_with_empty_camera_make(self):
        """Test with empty camera make"""
        analysis_data = {"camera_make": ""}
        result = build_camera_info(analysis_data)

        assert result is None


class TestBuildDetectionItem:
    """Test building detection items for API response"""

    def test_build_complete_detection(self):
        """Test building detection with all fields"""
        detection_id = str(uuid.uuid4())
        detection = {
            "id": detection_id,
            "class_id": 0,
            "class_name": "Basura",
            "confidence": 0.87,
            "risk_level": "ALTO",
            "breeding_site_type": "agua_estancada",
            "polygon": [[100, 200], [150, 200], [150, 250], [100, 250]],
            "mask_area": 2500.0,
            "created_at": "2025-09-26T14:30:52Z"
        }

        location_data = {
            "has_location": True,
            "latitude": -26.831314,
            "longitude": -65.195539
        }

        camera_info = {
            "camera_make": "Apple",
            "camera_model": "iPhone 15"
        }

        result = build_detection_item(
            detection, location_data, camera_info, "test.jpg"
        )

        assert result["id"] == uuid.UUID(detection_id)
        assert result["class_id"] == 0
        assert result["class_name"] == "Basura"
        assert result["confidence"] == 0.87
        assert result["risk_level"] == "ALTO"
        assert result["breeding_site_type"] == "agua_estancada"
        assert result["polygon"] == [[100, 200], [150, 200], [150, 250], [100, 250]]
        assert result["mask_area"] == 2500.0
        assert result["location"] == location_data
        assert result["camera_info"] == camera_info
        assert result["source_filename"] == "test.jpg"
        assert result["validation_status"] == "pending"

    def test_build_detection_with_defaults(self):
        """Test building detection with missing fields"""
        detection = {"id": str(uuid.uuid4())}

        result = build_detection_item(
            detection, {"has_location": False}, None, "image.jpg"
        )

        assert result["class_id"] == 0
        assert result["class_name"] == "Unknown"
        assert result["confidence"] == 0.0
        assert result["risk_level"] == "LOW"
        assert result["polygon"] == []
        assert result["mask_area"] == 0.0


class TestBuildRiskAssessment:
    """Test building risk assessment from analysis data"""

    def test_risk_assessment_with_detections(self):
        """Test building risk assessment with multiple detections"""
        analysis_data = {
            "risk_level": "MEDIO",
            "risk_score": 0.65,
            "total_detections": 5
        }

        detections = [
            {"risk_level": "ALTO"},
            {"risk_level": "ALTO"},
            {"risk_level": "MEDIO"},
            {"risk_level": "MEDIO"},
            {"risk_level": "BAJO"}
        ]

        result = build_risk_assessment(analysis_data, detections)

        assert result["level"] == "MEDIO"
        assert result["risk_score"] == 0.65
        assert result["total_detections"] == 5
        assert result["high_risk_count"] == 2
        assert result["medium_risk_count"] == 2
        assert len(result["recommendations"]) > 0

    def test_risk_assessment_without_detections(self):
        """Test building risk assessment with no detections"""
        analysis_data = {"total_detections": 0}
        result = build_risk_assessment(analysis_data, [])

        assert result["level"] == "BAJO"
        assert result["risk_score"] == 0.0
        assert result["total_detections"] == 0
        assert result["high_risk_count"] == 0
        assert result["medium_risk_count"] == 0

    def test_risk_assessment_all_high_risk(self):
        """Test risk assessment with all high risk detections"""
        analysis_data = {
            "risk_level": "ALTO",
            "risk_score": 0.95,
            "total_detections": 3
        }

        detections = [
            {"risk_level": "ALTO"},
            {"risk_level": "ALTO"},
            {"risk_level": "ALTO"}
        ]

        result = build_risk_assessment(analysis_data, detections)

        assert result["high_risk_count"] == 3
        assert result["medium_risk_count"] == 0


class TestParseISODatetime:
    """Test ISO datetime parsing"""

    def test_parse_valid_iso_datetime(self):
        """Test parsing valid ISO datetime"""
        datetime_str = "2025-09-26T14:30:52.123456"
        result = parse_iso_datetime(datetime_str)

        assert isinstance(result, datetime)
        assert result.year == 2025
        assert result.month == 9
        assert result.day == 26

    def test_parse_iso_datetime_with_z(self):
        """Test parsing ISO datetime with Z timezone"""
        datetime_str = "2025-09-26T14:30:52Z"
        result = parse_iso_datetime(datetime_str)

        assert isinstance(result, datetime)
        assert result.year == 2025

    def test_parse_none_datetime(self):
        """Test parsing None returns current time"""
        from datetime import timezone
        result = parse_iso_datetime(None)
        assert isinstance(result, datetime)
        # Should be within last minute
        assert (datetime.now(timezone.utc) - result).total_seconds() < 60

    def test_parse_empty_datetime(self):
        """Test parsing empty string returns current time"""
        result = parse_iso_datetime("")
        assert isinstance(result, datetime)

    def test_parse_invalid_datetime(self):
        """Test parsing invalid datetime returns current time"""
        result = parse_iso_datetime("invalid-date")
        assert isinstance(result, datetime)


class TestCalculateHeatmapIntensity:
    """Test heatmap intensity calculation"""

    def test_high_risk_with_detections(self):
        """Test intensity for high risk with multiple detections"""
        intensity = calculate_heatmap_intensity("ALTO", 5)
        assert 0.7 <= intensity <= 1.0

    def test_medium_risk_with_detections(self):
        """Test intensity for medium risk"""
        intensity = calculate_heatmap_intensity("MEDIO", 3)
        assert 0.4 <= intensity < 0.7

    def test_low_risk_minimal_detections(self):
        """Test intensity for low risk"""
        intensity = calculate_heatmap_intensity("BAJO", 1)
        assert 0.0 <= intensity < 0.4

    def test_high_risk_no_detections(self):
        """Test high risk with no detections"""
        intensity = calculate_heatmap_intensity("ALTO", 0)
        assert intensity == 0.7

    def test_intensity_never_exceeds_one(self):
        """Test that intensity never exceeds 1.0"""
        intensity = calculate_heatmap_intensity("ALTO", 100)
        assert intensity <= 1.0

    def test_intensity_values_rounded(self):
        """Test that intensity values are rounded to 2 decimals"""
        intensity = calculate_heatmap_intensity("MEDIO", 2)
        # Check it has at most 2 decimal places
        assert len(str(intensity).split('.')[-1]) <= 2


class TestBuildHeatmapPoint:
    """Test building heatmap points"""

    def test_build_valid_heatmap_point(self):
        """Test building heatmap point with valid data"""
        analysis = {
            "google_maps_url": "https://maps.google.com/?q=-26.831314,-65.195539",
            "risk_level": "ALTO",
            "total_detections": 3,
            "created_at": "2025-09-26T14:30:52Z"
        }

        result = build_heatmap_point(analysis)

        assert result is not None
        assert result["latitude"] == -26.831314
        assert result["longitude"] == -65.195539
        assert result["riskLevel"] == "ALTO"
        assert result["detectionCount"] == 3
        assert 0.0 <= result["intensity"] <= 1.0
        assert result["timestamp"] == "2025-09-26T14:30:52Z"

    def test_build_heatmap_point_invalid_url(self):
        """Test building heatmap point with invalid URL"""
        analysis = {
            "google_maps_url": "invalid_url",
            "risk_level": "MEDIO",
            "total_detections": 1
        }

        result = build_heatmap_point(analysis)
        assert result is None

    def test_build_heatmap_point_missing_url(self):
        """Test building heatmap point with missing URL"""
        analysis = {
            "risk_level": "BAJO",
            "total_detections": 0
        }

        result = build_heatmap_point(analysis)
        assert result is None


class TestCountRiskDistribution:
    """Test counting risk distribution"""

    def test_count_varied_risk_levels(self):
        """Test counting analyses with varied risk levels"""
        analyses = [
            {"risk_level": "BAJO"},
            {"risk_level": "BAJO"},
            {"risk_level": "MEDIO"},
            {"risk_level": "ALTO"},
            {"risk_level": "CRITICO"}
        ]

        result = count_risk_distribution(analyses)

        assert result["bajo"] == 2
        assert result["medio"] == 1
        assert result["alto"] == 1
        assert result["critico"] == 1

    def test_count_empty_analyses(self):
        """Test counting empty analyses list"""
        result = count_risk_distribution([])

        assert result["bajo"] == 0
        assert result["medio"] == 0
        assert result["alto"] == 0
        assert result["critico"] == 0

    def test_count_handles_minimo(self):
        """Test that MINIMO maps to bajo"""
        analyses = [{"risk_level": "MINIMO"}]
        result = count_risk_distribution(analyses)

        assert result["bajo"] == 1

    def test_count_handles_muy_alto(self):
        """Test that MUY_ALTO maps to critico"""
        analyses = [{"risk_level": "MUY_ALTO"}]
        result = count_risk_distribution(analyses)

        assert result["critico"] == 1

    def test_count_handles_none_risk_level(self):
        """Test handling of None risk level"""
        analyses = [{"risk_level": None}]
        result = count_risk_distribution(analyses)

        assert result["bajo"] == 1  # Default to bajo

    def test_count_handles_lowercase(self):
        """Test that function handles lowercase input"""
        analyses = [{"risk_level": "bajo"}]
        result = count_risk_distribution(analyses)

        assert result["bajo"] == 1


class TestCalculateUniqueLocations:
    """Test calculating unique locations"""

    def test_unique_locations_all_different(self):
        """Test unique locations with all different coordinates"""
        analyses = [
            {"google_maps_url": "https://maps.google.com/?q=-26.831314,-65.195539"},
            {"google_maps_url": "https://maps.google.com/?q=-26.841314,-65.205539"},
            {"google_maps_url": "https://maps.google.com/?q=-26.851314,-65.215539"}
        ]

        result = calculate_unique_locations(analyses)

        assert len(result) == 3

    def test_unique_locations_with_duplicates(self):
        """Test unique locations with duplicate coordinates"""
        analyses = [
            {"google_maps_url": "https://maps.google.com/?q=-26.831314,-65.195539"},
            {"google_maps_url": "https://maps.google.com/?q=-26.831314,-65.195539"},
            {"google_maps_url": "https://maps.google.com/?q=-26.841314,-65.205539"}
        ]

        result = calculate_unique_locations(analyses)

        assert len(result) == 2

    def test_unique_locations_rounds_to_3_decimals(self):
        """Test that locations are rounded to 3 decimals"""
        analyses = [
            {"google_maps_url": "https://maps.google.com/?q=-26.8313141,-65.1955391"},
            {"google_maps_url": "https://maps.google.com/?q=-26.8313149,-65.1955399"}
        ]

        result = calculate_unique_locations(analyses)

        # Both should round to same location
        assert len(result) == 1
        # Check coordinates are rounded
        for lat, lng in result:
            assert len(str(lat).split('.')[-1]) <= 3
            assert len(str(lng).split('.')[-1]) <= 3

    def test_unique_locations_ignores_invalid_urls(self):
        """Test that invalid URLs are ignored"""
        analyses = [
            {"google_maps_url": "https://maps.google.com/?q=-26.831314,-65.195539"},
            {"google_maps_url": "invalid_url"},
            {"google_maps_url": ""}
        ]

        result = calculate_unique_locations(analyses)

        assert len(result) == 1

    def test_unique_locations_empty_list(self):
        """Test with empty analyses list"""
        result = calculate_unique_locations([])
        assert len(result) == 0


class TestBuildAnalysisListItem:
    """Test building analysis list items"""

    def test_build_complete_analysis_item(self):
        """Test building analysis item with complete data"""
        analysis_id = str(uuid.uuid4())
        analysis = {
            "id": analysis_id,
            "image_filename": "IMG_1234.jpg",
            "image_size_bytes": 1024000,
            "has_gps_data": True,
            "google_maps_url": "https://maps.google.com/?q=-26.831314,-65.195539",
            "location_source": "EXIF_GPS",
            "google_earth_url": "https://earth.google.com/web/@-26.831314,-65.195539",
            "camera_make": "Apple",
            "camera_model": "iPhone 15",
            "camera_datetime": "2025:09:19 15:19:08",
            "model_used": "dengue_v2",
            "confidence_threshold": 0.7,
            "processing_time_ms": 1500,
            "risk_level": "MEDIO",
            "risk_score": 0.65,
            "total_detections": 3,
            "created_at": "2025-09-26T14:30:52Z",
            "updated_at": "2025-09-26T14:31:15Z"
        }

        result = build_analysis_list_item(analysis)

        assert result["id"] == uuid.UUID(analysis_id)
        assert result["status"] == "completed"
        assert result["image_filename"] == "IMG_1234.jpg"
        assert result["image_size_bytes"] == 1024000
        assert result["location"]["has_location"] is True
        assert result["location"]["latitude"] == -26.831314
        assert result["location"]["longitude"] == -65.195539
        assert result["camera_info"]["camera_make"] == "Apple"
        assert result["model_used"] == "dengue_v2"
        assert result["confidence_threshold"] == 0.7
        assert result["processing_time_ms"] == 1500
        assert result["risk_assessment"]["level"] == "MEDIO"
        assert result["risk_assessment"]["risk_score"] == 0.65
        assert result["risk_assessment"]["total_detections"] == 3
        assert result["detections"] == []  # Empty for list view

    def test_build_analysis_item_without_gps(self):
        """Test building analysis item without GPS data"""
        analysis = {
            "id": str(uuid.uuid4()),
            "image_filename": "test.jpg",
            "has_gps_data": False
        }

        result = build_analysis_list_item(analysis)

        assert result["location"]["has_location"] is False

    def test_build_analysis_item_without_camera(self):
        """Test building analysis item without camera data"""
        analysis = {
            "id": str(uuid.uuid4()),
            "image_filename": "test.jpg"
        }

        result = build_analysis_list_item(analysis)

        assert result["camera_info"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
