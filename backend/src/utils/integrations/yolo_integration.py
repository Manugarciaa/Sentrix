"""
YOLO service integration utilities
"""

from typing import Dict, Any, Optional
from sentrix_shared.data_models import (
    CLASS_ID_TO_BREEDING_SITE,
    YOLO_RISK_TO_DETECTION_RISK,
    DetectionRiskEnum
)

# Import shared risk assessment
from sentrix_shared.risk_assessment import assess_dengue_risk

def calculate_risk_assessment(detections: list) -> Dict[str, Any]:
    """
    Calculate risk assessment from detections using shared library
    """
    # Use unified risk assessment function
    return assess_dengue_risk(detections)

def parse_yolo_detection(detection: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse a single YOLO detection into standardized format
    """
    # Extract class info
    class_id = detection.get("class_id")
    class_name = detection.get("class_name") or detection.get("class")

    # Map to breeding site type
    breeding_site_type = None
    if class_id is not None and class_id in CLASS_ID_TO_BREEDING_SITE:
        breeding_site_type = CLASS_ID_TO_BREEDING_SITE[class_id]

    # Map risk level
    risk_level_str = detection.get("risk_level", "BAJO")
    risk_level = YOLO_RISK_TO_DETECTION_RISK.get(risk_level_str, DetectionRiskEnum.BAJO)

    # Extract location info
    location = detection.get("location", {})
    has_location = location.get("has_location", False)

    parsed = {
        "class_id": class_id,
        "class_name": class_name,
        "confidence": detection.get("confidence"),
        "risk_level": risk_level,
        "breeding_site_type": breeding_site_type,
        "polygon": detection.get("polygon", []),
        "mask_area": detection.get("mask_area"),
        "has_location": has_location,
    }

    # Add location coordinates if available
    if has_location:
        parsed["detection_latitude"] = location.get("latitude")
        parsed["detection_longitude"] = location.get("longitude")

    return parsed

def parse_yolo_report(yolo_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse complete YOLO service response into standardized format
    """
    detections = []

    # Parse detections
    if "detections" in yolo_response:
        for detection in yolo_response["detections"]:
            parsed_detection = parse_yolo_detection(detection)
            detections.append(parsed_detection)

    # Check for GPS data
    has_gps_data = False
    if detections:
        has_gps_data = any(d.get("has_location", False) for d in detections)

    # Or check at response level
    location = yolo_response.get("location", {})
    if location.get("has_location", False):
        has_gps_data = True

    # Parse analysis summary
    analysis = {
        "total_detections": len(detections),
        "has_gps_data": has_gps_data,
        "processing_time_ms": yolo_response.get("processing_time_ms", 0)
    }

    # Calculate risk assessment
    risk_assessment = calculate_risk_assessment(detections)

    return {
        "analysis": analysis,
        "detections": detections,
        "risk_assessment": risk_assessment
    }

def validate_yolo_response(response: Dict[str, Any]) -> bool:
    """
    Validate YOLO service response structure
    """
    if not isinstance(response, dict):
        return False

    # Check for success indicator (either "status" or "success")
    has_status = "status" in response or "success" in response
    if not has_status:
        return False

    # Check if response indicates success
    is_successful = (
        response.get("status") == "success" or
        response.get("status") == "healthy" or
        response.get("success") is True
    )

    if is_successful:
        # Successful response should have detections (can be empty array)
        if "detections" not in response:
            return False

        detections = response.get("detections", [])
        if not isinstance(detections, list):
            return False

        # Validate each detection (if any)
        for detection in detections:
            if not isinstance(detection, dict):
                return False

            # Confidence is required, class info should be present
            if "confidence" not in detection:
                return False

    return True