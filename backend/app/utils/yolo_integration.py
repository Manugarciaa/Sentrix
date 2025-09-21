"""
YOLO service integration utilities
"""

from typing import Dict, Any, Optional

# Import shared risk assessment
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from shared.risk_assessment import assess_dengue_risk

def calculate_risk_assessment(detections: list) -> Dict[str, Any]:
    """
    Calculate risk assessment from detections using shared library
    """
    # Use unified risk assessment function
    return assess_dengue_risk(detections)

def parse_yolo_report(yolo_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse YOLO service response into standardized format
    """
    parsed_data = {
        "detections": [],
        "processing_info": {},
        "risk_assessment": {}
    }

    # Parse detections
    if "detections" in yolo_response:
        for detection in yolo_response["detections"]:
            parsed_detection = {
                "class_id": detection.get("class_id"),
                "class_name": detection.get("class_name"),
                "confidence": detection.get("confidence"),
                "polygon": detection.get("polygon", []),
                "risk_level": detection.get("risk_level", "LOW"),
                "breeding_site_type": detection.get("breeding_site_type")
            }
            parsed_data["detections"].append(parsed_detection)

    # Parse processing info
    parsed_data["processing_info"] = {
        "model_used": yolo_response.get("model_version", "unknown"),
        "processing_time_ms": yolo_response.get("processing_time", 0),
        "confidence_threshold": yolo_response.get("confidence_threshold", 0.5)
    }

    # Calculate risk assessment
    parsed_data["risk_assessment"] = calculate_risk_assessment(parsed_data["detections"])

    return parsed_data

def validate_yolo_response(response: Dict[str, Any]) -> bool:
    """
    Validate YOLO service response structure
    """
    if not isinstance(response, dict):
        return False

    # Check required fields
    if "status" not in response:
        return False

    if response.get("status") == "success":
        # Successful response should have detections
        if "detections" not in response:
            return False

        detections = response.get("detections", [])
        if not isinstance(detections, list):
            return False

        # Validate each detection
        for detection in detections:
            if not isinstance(detection, dict):
                return False

            required_fields = ["class_id", "confidence"]
            for field in required_fields:
                if field not in detection:
                    return False

    return True