"""
Data transformers for analysis responses

Transforms raw database/service data into API response formats.
Keeps data transformation logic separate from API endpoints.
"""

import uuid
from typing import Optional, List
from datetime import datetime, timezone

from ..logging_config import get_logger
from ..config import get_settings

logger = get_logger(__name__)
settings = get_settings()


def extract_gps_from_maps_url(google_maps_url: str) -> Optional[tuple[float, float]]:
    """
    Extract latitude and longitude from Google Maps URL.

    Args:
        google_maps_url: Google Maps URL with embedded coordinates

    Returns:
        Optional[tuple[float, float]]: (latitude, longitude) or None if invalid

    Example:
        >>> extract_gps_from_maps_url("https://maps.google.com/?q=-26.8083,-65.2176")
        (-26.8083, -65.2176)
    """
    if not google_maps_url or "q=" not in google_maps_url:
        return None

    try:
        coords_part = google_maps_url.split("q=")[1]
        if "," not in coords_part:
            return None

        lat_str, lng_str = coords_part.split(",", 1)
        return (float(lat_str), float(lng_str))
    except (ValueError, IndexError):
        return None


def build_location_data(analysis_data: dict) -> dict:
    """
    Build location data dict from analysis data.

    Args:
        analysis_data: Raw analysis data from database

    Returns:
        dict: Location data with coordinates and metadata
    """
    location_data = {"has_location": False}

    if not analysis_data.get("has_gps_data") or not analysis_data.get("google_maps_url"):
        return location_data

    google_maps_url = analysis_data["google_maps_url"]
    coords = extract_gps_from_maps_url(google_maps_url)

    if coords:
        lat, lng = coords
        location_data = {
            "has_location": True,
            "latitude": lat,
            "longitude": lng,
            "coordinates": f"{lat},{lng}",
            "altitude_meters": analysis_data.get("gps_altitude_meters"),
            "location_source": analysis_data.get("location_source"),
            "google_maps_url": google_maps_url,
            "google_earth_url": analysis_data.get("google_earth_url")
        }
        logger.debug("location data built successfully", lat=lat, lng=lng)

    return location_data


def build_camera_info(analysis_data: dict) -> Optional[dict]:
    """
    Build camera info dict from analysis data.

    Args:
        analysis_data: Raw analysis data from database

    Returns:
        Optional[dict]: Camera metadata or None if not available
    """
    if not analysis_data.get("camera_make"):
        return None

    return {
        "camera_make": analysis_data.get("camera_make"),
        "camera_model": analysis_data.get("camera_model"),
        "camera_datetime": analysis_data.get("camera_datetime"),
        "camera_software": None
    }


def build_detection_item(
    detection: dict,
    location_data: dict,
    camera_info: Optional[dict],
    image_filename: str
) -> dict:
    """
    Build a single detection item for API response.

    Args:
        detection: Raw detection data
        location_data: Location metadata
        camera_info: Camera metadata
        image_filename: Source image filename

    Returns:
        dict: Formatted detection item
    """
    return {
        "id": uuid.UUID(detection["id"]),
        "class_id": detection.get("class_id", 0),
        "class_name": detection.get("class_name", "Unknown"),
        "confidence": detection.get("confidence", 0.0),
        "risk_level": detection.get("risk_level", "LOW"),
        "breeding_site_type": detection.get("breeding_site_type", "Unknown"),
        "polygon": detection.get("polygon", []),
        "mask_area": detection.get("mask_area", 0.0),
        "area_square_pixels": detection.get("mask_area", 0.0),
        "location": location_data,
        "source_filename": image_filename,
        "camera_info": camera_info,
        "validation_status": "pending",
        "validation_notes": None,
        "validated_at": None,
        "created_at": detection.get("created_at")
    }


def build_risk_assessment(analysis_data: dict, processed_detections: List[dict]) -> dict:
    """
    Build risk assessment dict from analysis and detections.

    Args:
        analysis_data: Raw analysis data
        processed_detections: List of processed detection items

    Returns:
        dict: Risk assessment with counts and recommendations
    """
    return {
        "level": analysis_data.get("risk_level") or "BAJO",
        "risk_score": analysis_data.get("risk_score", 0.0),
        "total_detections": analysis_data.get("total_detections", 0),
        "high_risk_count": sum(1 for d in processed_detections if d["risk_level"] == "ALTO"),
        "medium_risk_count": sum(1 for d in processed_detections if d["risk_level"] == "MEDIO"),
        "recommendations": ["Verificar detecciones", "Seguir protocolos de seguridad"]
    }


def parse_iso_datetime(datetime_str: Optional[str]) -> datetime:
    """
    Parse ISO datetime string, return current time if invalid.

    Args:
        datetime_str: ISO format datetime string

    Returns:
        datetime: Parsed datetime or current UTC time if invalid
    """
    if not datetime_str:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return datetime.now(timezone.utc)


def build_analysis_list_item(analysis: dict) -> dict:
    """
    Build a single analysis response item for list view.

    Constructs location data, camera info, and risk assessment
    without including detections (for performance).

    Args:
        analysis: Raw analysis data from database

    Returns:
        dict: AnalysisResponse-compatible dict for list view
    """
    # Build location data from GPS URL
    location_data = {"has_location": False}
    if analysis.get("has_gps_data"):
        google_maps_url = analysis.get("google_maps_url")
        coords = extract_gps_from_maps_url(google_maps_url)

        if coords:
            lat, lng = coords
            location_data = {
                "has_location": True,
                "latitude": lat,
                "longitude": lng,
                "coordinates": f"{lat},{lng}",
                "location_source": analysis.get("location_source", "UNKNOWN"),
                "google_maps_url": google_maps_url,
                "google_earth_url": analysis.get("google_earth_url")
            }

    # Build camera info if available
    camera_info = build_camera_info(analysis)

    # Build response item
    return {
        "id": uuid.UUID(analysis["id"]),
        "status": "completed",
        "image_filename": analysis.get("image_filename"),
        "processed_image_url": analysis.get("processed_image_url"),
        "processed_image_filename": analysis.get("processed_image_filename"),
        "image_size_bytes": analysis.get("image_size_bytes", 0),
        "location": location_data,
        "camera_info": camera_info,
        "model_used": analysis.get("model_used", "unknown"),
        "confidence_threshold": analysis.get("confidence_threshold", settings.yolo_confidence_threshold),
        "processing_time_ms": analysis.get("processing_time_ms", 0),
        "yolo_service_version": "2.0.0",
        "risk_assessment": {
            "level": analysis.get("risk_level") or "BAJO",
            "risk_score": analysis.get("risk_score", 0.0),
            "total_detections": analysis.get("total_detections", 0),
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "recommendations": []
        },
        "detections": [],  # Empty for list view (performance)
        "image_taken_at": parse_iso_datetime(analysis.get("created_at")),
        "created_at": parse_iso_datetime(analysis.get("created_at")),
        "updated_at": parse_iso_datetime(analysis.get("updated_at"))
    }


def calculate_heatmap_intensity(risk_level: str, detection_count: int) -> float:
    """
    Calculate heatmap intensity based on risk level and detection count.

    Args:
        risk_level: Risk level (ALTO, MEDIO, BAJO)
        detection_count: Number of detections

    Returns:
        float: Intensity value between 0.0 and 1.0
    """
    base_intensity = 0.3

    if risk_level == "ALTO":
        base_intensity = 0.7
    elif risk_level == "MEDIO":
        base_intensity = 0.4
    else:
        base_intensity = 0.2

    # Add detection count bonus
    detection_bonus = (
        min(detection_count * 0.05, 0.3)
        if risk_level in ["ALTO", "MEDIO"]
        else min(detection_count * 0.03, 0.2)
    )

    return round(min(base_intensity + detection_bonus, 1.0), 2)


def build_heatmap_point(analysis: dict) -> Optional[dict]:
    """
    Build a single heatmap point from analysis data.

    Extracts coordinates from Google Maps URL and calculates intensity.

    Args:
        analysis: Raw analysis data with google_maps_url

    Returns:
        Optional[dict]: Heatmap point or None if coordinates invalid
    """
    google_maps_url = analysis.get("google_maps_url", "")
    coords = extract_gps_from_maps_url(google_maps_url)

    if not coords:
        return None

    lat, lng = coords
    risk_level = analysis.get("risk_level", "BAJO")
    detection_count = analysis.get("total_detections", 0)

    return {
        "latitude": lat,
        "longitude": lng,
        "intensity": calculate_heatmap_intensity(risk_level, detection_count),
        "riskLevel": risk_level,
        "detectionCount": detection_count,
        "timestamp": analysis.get("created_at")
    }


def count_risk_distribution(analyses: list) -> dict:
    """
    Count analysis distribution by risk level.

    Normalizes risk levels to lowercase categories.

    Args:
        analyses: List of analysis data dicts

    Returns:
        dict: Risk counts by category (bajo, medio, alto, critico)
    """
    risk_counts = {"bajo": 0, "medio": 0, "alto": 0, "critico": 0}

    for analysis in analyses:
        risk_level = (analysis.get("risk_level") or "BAJO").upper()
        if risk_level in ["BAJO", "MINIMO"]:
            risk_counts["bajo"] += 1
        elif risk_level == "MEDIO":
            risk_counts["medio"] += 1
        elif risk_level == "ALTO":
            risk_counts["alto"] += 1
        elif risk_level in ["MUY_ALTO", "CRITICO"]:
            risk_counts["critico"] += 1

    return risk_counts


def calculate_unique_locations(analyses: list) -> set:
    """
    Calculate unique GPS locations from analyses.

    Rounds coordinates to 3 decimals (~110m precision) to cluster nearby locations.

    Args:
        analyses: List of analysis data dicts

    Returns:
        set: Set of unique (lat, lng) tuples
    """
    unique_locations = set()

    for analysis in analyses:
        google_maps_url = analysis.get("google_maps_url")
        coords = extract_gps_from_maps_url(google_maps_url)

        if coords:
            lat, lng = coords
            # Round to 3 decimals (~110m precision)
            unique_locations.add((round(lat, 3), round(lng, 3)))

    return unique_locations
