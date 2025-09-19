"""
YOLO service integration utilities
"""

from typing import Dict, Any, Optional

def format_yolo_response(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format YOLO service response to match API schema
    """
    return {
        "status": "processed",
        "detections": response_data.get("detections", []),
        "processing_time_ms": response_data.get("processing_time", 0),
        "model_used": response_data.get("model_version", "unknown")
    }

def validate_yolo_request(image_data: Any) -> bool:
    """
    Validate request before sending to YOLO service
    """
    if not image_data:
        return False
    return True

def calculate_risk_assessment(detections: list) -> Dict[str, Any]:
    """
    Calculate risk assessment from detections
    """
    total_detections = len(detections)
    high_risk_count = sum(1 for d in detections if d.get("risk_level") == "HIGH")
    medium_risk_count = sum(1 for d in detections if d.get("risk_level") == "MEDIUM")

    if high_risk_count > 0:
        level = "HIGH"
        risk_score = 0.8 + (high_risk_count * 0.05)
    elif medium_risk_count > 0:
        level = "MEDIUM"
        risk_score = 0.5 + (medium_risk_count * 0.05)
    else:
        level = "LOW"
        risk_score = 0.2

    return {
        "level": level,
        "risk_score": min(risk_score, 1.0),
        "total_detections": total_detections,
        "high_risk_count": high_risk_count,
        "medium_risk_count": medium_risk_count,
        "recommendations": get_recommendations(level, total_detections)
    }

def get_recommendations(risk_level: str, detection_count: int) -> list:
    """
    Get recommendations based on risk level
    """
    recommendations = []

    if risk_level == "HIGH":
        recommendations.extend([
            "Immediate action required",
            "Contact local health authorities",
            "Remove standing water sources"
        ])
    elif risk_level == "MEDIUM":
        recommendations.extend([
            "Monitor area closely",
            "Consider preventive measures",
            "Schedule follow-up inspection"
        ])
    else:
        recommendations.extend([
            "Continue regular monitoring",
            "Maintain prevention practices"
        ])

    if detection_count > 5:
        recommendations.append("High detection count - consider area-wide intervention")

    return recommendations

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