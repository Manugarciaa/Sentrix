"""
Tests para las utilidades de integración con el servicio YOLO
Verifica que el mapeo entre respuestas YOLO y modelos del backend funcione correctamente
"""

import pytest
from unittest.mock import Mock

from src.utils.integrations.yolo_integration import (
    parse_yolo_detection, parse_yolo_report, validate_yolo_response
)
from sentrix_shared.data_models import (
    DetectionRiskEnum,
    BreedingSiteTypeEnum,
    CLASS_ID_TO_BREEDING_SITE,
    CLASS_NAME_NORMALIZATIONS as CLASS_NAME_TO_BREEDING_SITE,
    YOLO_RISK_TO_DETECTION_RISK
)


class TestYOLOIntegrationMapping:
    """Tests para el mapeo de respuestas del servicio YOLO"""

    def test_class_id_mapping(self):
        """Test que el mapeo de class_id a enum de sitios de cría funciona"""
        assert CLASS_ID_TO_BREEDING_SITE[0] == BreedingSiteTypeEnum.BASURA
        assert CLASS_ID_TO_BREEDING_SITE[1] == BreedingSiteTypeEnum.CALLES_MAL_HECHAS
        assert CLASS_ID_TO_BREEDING_SITE[2] == BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA
        assert CLASS_ID_TO_BREEDING_SITE[3] == BreedingSiteTypeEnum.HUECOS

    def test_class_name_mapping(self):
        """Test class name to breeding site enum mapping"""
        assert CLASS_NAME_TO_BREEDING_SITE["Basura"] == BreedingSiteTypeEnum.BASURA
        assert CLASS_NAME_TO_BREEDING_SITE["Calles mal hechas"] == BreedingSiteTypeEnum.CALLES_MAL_HECHAS
        assert CLASS_NAME_TO_BREEDING_SITE["Charcos/Cumulo de agua"] == BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA
        assert CLASS_NAME_TO_BREEDING_SITE["Huecos"] == BreedingSiteTypeEnum.HUECOS

    def test_risk_level_mapping(self):
        """Test risk level mapping from YOLO to backend"""
        assert YOLO_RISK_TO_DETECTION_RISK["ALTO"] == DetectionRiskEnum.ALTO
        assert YOLO_RISK_TO_DETECTION_RISK["MEDIO"] == DetectionRiskEnum.MEDIO
        assert YOLO_RISK_TO_DETECTION_RISK["BAJO"] == DetectionRiskEnum.BAJO


class TestParseYOLODetection:
    """Test individual YOLO detection parsing"""

    def test_parse_basic_detection(self):
        """Test parsing a basic detection without GPS"""
        yolo_detection = {
            "class_id": 0,
            "class": "Basura",
            "confidence": 0.75,
            "risk_level": "MEDIO",
            "polygon": [[100, 100], [200, 100], [200, 200], [100, 200]],
            "mask_area": 10000.0,
            "location": {"has_location": False}
        }

        result = parse_yolo_detection(yolo_detection)

        assert result["class_id"] == 0
        assert result["class_name"] == "Basura"
        assert result["confidence"] == 0.75
        assert result["risk_level"] == DetectionRiskEnum.MEDIO
        assert result["breeding_site_type"] == BreedingSiteTypeEnum.BASURA
        assert result["polygon"] == [[100, 100], [200, 100], [200, 200], [100, 200]]
        assert result["mask_area"] == 10000.0
        assert result["has_location"] is False

    def test_parse_detection_with_gps(self):
        """Test parsing detection with GPS coordinates"""
        yolo_detection = {
            "class_id": 2,
            "class": "Charcos/Cumulo de agua",
            "confidence": 0.85,
            "risk_level": "ALTO",
            "polygon": [[150, 150], [250, 150], [250, 250], [150, 250]],
            "mask_area": 10000.0,
            "location": {
                "has_location": True,
                "latitude": -26.831314,
                "longitude": -65.195539,
                "altitude_meters": 458.2,
                "backend_integration": {
                    "verification_urls": {
                        "google_maps": "https://maps.google.com/?q=-26.831314,-65.195539",
                        "google_earth": "https://earth.google.com/web/search/-26.831314,-65.195539"
                    }
                }
            },
            "image_metadata": {
                "source_file": "test_image.jpg",
                "camera_info": {
                    "camera_make": "Xiaomi",
                    "camera_model": "220333QL",
                    "datetime_original": "2025:09:19 15:19:08"
                }
            }
        }

        result = parse_yolo_detection(yolo_detection)

        assert result["class_id"] == 2
        assert result["class_name"] == "Charcos/Cumulo de agua"
        assert result["confidence"] == 0.85
        assert result["risk_level"] == DetectionRiskEnum.ALTO
        assert result["breeding_site_type"] == BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA
        assert result["has_location"] is True
        assert result["detection_latitude"] == -26.831314
        assert result["detection_longitude"] == -65.195539
        assert result["detection_altitude_meters"] == 458.2
        assert "google_maps" in result["google_maps_url"]
        assert "google_earth" in result["google_earth_url"]
        assert result["source_filename"] == "test_image.jpg"
        assert result["camera_make"] == "Xiaomi"
        assert result["camera_model"] == "220333QL"

    def test_parse_detection_missing_fields(self):
        """Test parsing detection with missing optional fields"""
        yolo_detection = {
            "class": "Huecos",
            "confidence": 0.60,
            "risk_level": "ALTO"
        }

        result = parse_yolo_detection(yolo_detection)

        assert result["class_name"] == "Huecos"
        assert result["confidence"] == 0.60
        assert result["risk_level"] == DetectionRiskEnum.ALTO
        assert result["breeding_site_type"] == BreedingSiteTypeEnum.HUECOS
        assert result["class_id"] is None  # Missing field
        assert result["has_location"] is False  # Default when no location

    def test_parse_detection_unknown_class(self):
        """Test parsing detection with unknown class"""
        yolo_detection = {
            "class_id": 999,
            "class": "Unknown Class",
            "confidence": 0.50,
            "risk_level": "UNKNOWN_RISK"
        }

        result = parse_yolo_detection(yolo_detection)

        assert result["class_id"] == 999
        assert result["class_name"] == "Unknown Class"
        assert result["breeding_site_type"] is None  # Unknown mapping
        assert result["risk_level"] is None  # Unknown mapping


class TestParseYOLOReport:
    """Test complete YOLO report parsing"""

    def test_parse_complete_report(self):
        """Test parsing a complete YOLO report"""
        yolo_report = {
            "source": "test_image.jpg",
            "total_detections": 2,
            "processing_time_ms": 1234,
            "model_version": "yolo11s-v1",
            "location": {
                "has_location": True,
                "latitude": -26.831314,
                "longitude": -65.195539,
                "altitude_meters": 458.2,
                "gps_date": "2025:09:19",
                "location_source": "EXIF_GPS",
                "maps": {
                    "google_maps_url": "https://maps.google.com/?q=-26.831314,-65.195539"
                }
            },
            "camera_info": {
                "camera_make": "Xiaomi",
                "camera_model": "220333QL",
                "datetime_original": "2025:09:19 15:19:08",
                "software": "MIUI Camera"
            },
            "risk_assessment": {
                "level": "ALTO",
                "high_risk_sites": 1,
                "medium_risk_sites": 1,
                "recommendations": ["Eliminación inmediata", "Monitoreo frecuente"]
            },
            "detections": [
                {
                    "class_id": 0,
                    "class": "Basura",
                    "confidence": 0.75,
                    "risk_level": "MEDIO",
                    "polygon": [[100, 100], [200, 100], [200, 200], [100, 200]],
                    "mask_area": 10000.0,
                    "location": {"has_location": False}
                },
                {
                    "class_id": 3,
                    "class": "Huecos",
                    "confidence": 0.90,
                    "risk_level": "ALTO",
                    "polygon": [[300, 300], [400, 300], [400, 400], [300, 400]],
                    "mask_area": 10000.0,
                    "location": {"has_location": True, "latitude": -26.831314, "longitude": -65.195539}
                }
            ]
        }

        result = parse_yolo_report(yolo_report)

        # Test analysis data
        analysis = result["analysis"]
        assert analysis["image_filename"] == "test_image.jpg"
        assert analysis["total_detections"] == 2
        assert analysis["processing_time_ms"] == 1234
        assert analysis["model_used"] == "yolo11s-v1"
        assert analysis["has_gps_data"] is True
        assert analysis["gps_altitude_meters"] == 458.2
        assert analysis["gps_date"] == "2025:09:19"
        assert analysis["location_source"] == "EXIF_GPS"
        assert analysis["camera_make"] == "Xiaomi"
        assert analysis["camera_model"] == "220333QL"
        assert analysis["camera_software"] == "MIUI Camera"
        assert analysis["risk_level"] == "HIGH"  # ALTO -> HIGH mapping
        assert analysis["high_risk_count"] == 1
        assert analysis["medium_risk_count"] == 1
        assert "Eliminación inmediata" in analysis["recommendations"]

        # Test detections
        detections = result["detections"]
        assert len(detections) == 2

        # First detection
        det1 = detections[0]
        assert det1["class_id"] == 0
        assert det1["class_name"] == "Basura"
        assert det1["breeding_site_type"] == BreedingSiteTypeEnum.BASURA
        assert det1["risk_level"] == DetectionRiskEnum.MEDIO
        assert det1["has_location"] is False

        # Second detection
        det2 = detections[1]
        assert det2["class_id"] == 3
        assert det2["class_name"] == "Huecos"
        assert det2["breeding_site_type"] == BreedingSiteTypeEnum.HUECOS
        assert det2["risk_level"] == DetectionRiskEnum.ALTO

    def test_parse_report_no_gps(self):
        """Test parsing report without GPS data"""
        yolo_report = {
            "source": "no_gps_image.jpg",
            "total_detections": 1,
            "location": {"has_location": False},
            "camera_info": {},
            "risk_assessment": {"level": "BAJO"},
            "detections": [
                {
                    "class": "Basura",
                    "confidence": 0.60,
                    "risk_level": "BAJO"
                }
            ]
        }

        result = parse_yolo_report(yolo_report)

        analysis = result["analysis"]
        assert analysis["has_gps_data"] is False
        assert analysis["risk_level"] == "LOW"  # BAJO -> LOW

    def test_parse_report_missing_fields(self):
        """Test parsing report with missing optional fields"""
        yolo_report = {
            "detections": []
        }

        result = parse_yolo_report(yolo_report)

        analysis = result["analysis"]
        assert analysis["total_detections"] == 0
        assert analysis["has_gps_data"] is False
        assert len(result["detections"]) == 0


class TestValidateYOLOResponse:
    """Test YOLO response validation"""

    def test_valid_response(self):
        """Test validation of valid YOLO response"""
        valid_response = {
            "success": True,
            "detections": [
                {
                    "class": "Basura",
                    "confidence": 0.75,
                    "risk_level": "MEDIO"
                }
            ]
        }

        assert validate_yolo_response(valid_response) is True

    def test_invalid_response_missing_success(self):
        """Test validation fails when success field is missing"""
        invalid_response = {
            "detections": []
        }

        assert validate_yolo_response(invalid_response) is False

    def test_invalid_response_missing_detections(self):
        """Test validation fails when detections field is missing"""
        invalid_response = {
            "success": True
        }

        assert validate_yolo_response(invalid_response) is False

    def test_invalid_response_success_false(self):
        """Test validation fails when success is False"""
        invalid_response = {
            "success": False,
            "detections": []
        }

        assert validate_yolo_response(invalid_response) is False

    def test_invalid_detection_fields(self):
        """Test validation fails when detection has missing required fields"""
        invalid_response = {
            "success": True,
            "detections": [
                {
                    "class": "Basura",
                    # Missing confidence and risk_level
                }
            ]
        }

        assert validate_yolo_response(invalid_response) is False

    def test_valid_empty_detections(self):
        """Test validation passes with empty detections array"""
        valid_response = {
            "success": True,
            "detections": []
        }

        assert validate_yolo_response(valid_response) is True