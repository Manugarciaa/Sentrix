# -*- coding: utf-8 -*-
"""
Analysis endpoints for image processing and breeding site detection
Endpoints de analisis para procesamiento de imagenes y deteccion de criaderos

SECURITY: Enhanced file validation with MIME type checking
"""

import uuid
import asyncio
import httpx
import os
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Request
from fastapi.responses import JSONResponse, FileResponse

from ...schemas.analyses import (
    AnalysisUploadRequest, AnalysisUploadResponse,
    AnalysisResponse, AnalysisListQuery, AnalysisListResponse,
    BatchUploadRequest, BatchUploadResponse
)
from src.services.analysis_service import analysis_service
from ...config import get_settings
from ...utils.auth import get_current_user, get_current_active_user, get_optional_current_user
from ...utils.file_validation import validate_uploaded_image  # SECURITY: New validation
from ...database.models.models import UserProfile
from ...logging_config import get_logger
from ...exceptions import (
    FileValidationException,
    ImageProcessingException,
    YOLOServiceException,
    YOLOTimeoutException,
    DatabaseException,
    AnalysisNotFoundException
)

logger = get_logger(__name__)

# SECURITY: Rate limiting always enabled for all endpoints
from ...middleware.rate_limit import limiter

router = APIRouter()
settings = get_settings()


# ============================================
# Helper Functions - Validation
# ============================================

def _validate_file_upload(file: Optional[UploadFile]) -> None:
    """
    Validate uploaded file for analysis.

    Raises:
        HTTPException: If file is invalid
    """
    if not file:
        raise HTTPException(
            status_code=400,
            detail="Se requiere un archivo de imagen"
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="El archivo debe tener un nombre valido"
        )


def _validate_file_format(filename: str) -> str:
    """
    Validate file format is supported.

    Args:
        filename: Name of the file

    Returns:
        str: File extension

    Raises:
        HTTPException: If format not supported
    """
    # Supported image formats
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.heic', '.heif', '.webp', '.bmp']

    file_ext = '.' + filename.split('.')[-1].lower()
    if file_ext not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado: {file_ext}. Formatos soportados: {', '.join(SUPPORTED_FORMATS)}"
        )
    return file_ext


def _validate_coordinates(latitude: Optional[float], longitude: Optional[float]) -> None:
    """
    Validate coordinate pair is complete.

    Raises:
        HTTPException: If only one coordinate provided
    """
    if (latitude is not None and longitude is None) or (longitude is not None and latitude is None):
        raise HTTPException(
            status_code=400,
            detail="Si proporciona coordenadas, tanto latitud como longitud son requeridas"
        )


def _validate_confidence_threshold(confidence_threshold: float) -> None:
    """
    Validate confidence threshold is in valid range.

    Args:
        confidence_threshold: Threshold value to validate

    Raises:
        HTTPException: If threshold out of range
    """
    if not settings.min_confidence_threshold <= confidence_threshold <= settings.max_confidence_threshold:
        raise HTTPException(
            status_code=400,
            detail=f"confidence_threshold debe estar entre {settings.min_confidence_threshold} y {settings.max_confidence_threshold}"
        )


async def _validate_file_size(image_data: bytes, max_size: int) -> None:
    """
    Validate image file size.

    Args:
        image_data: Image bytes
        max_size: Maximum allowed size in bytes

    Raises:
        HTTPException: If file too large
    """
    if len(image_data) > max_size:
        max_mb = max_size // (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"El archivo es demasiado grande. Maximo {max_mb}MB"
        )


# ============================================
# Helper Functions - Data Transformation
# ============================================

def _extract_gps_from_maps_url(google_maps_url: str) -> Optional[tuple[float, float]]:
    """Extract latitude and longitude from Google Maps URL"""
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


def _build_location_data(analysis_data: dict) -> dict:
    """Build location data dict from analysis data"""
    location_data = {"has_location": False}

    if not analysis_data.get("has_gps_data") or not analysis_data.get("google_maps_url"):
        return location_data

    google_maps_url = analysis_data["google_maps_url"]
    coords = _extract_gps_from_maps_url(google_maps_url)

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


def _build_camera_info(analysis_data: dict) -> Optional[dict]:
    """Build camera info dict from analysis data"""
    if not analysis_data.get("camera_make"):
        return None

    return {
        "camera_make": analysis_data.get("camera_make"),
        "camera_model": analysis_data.get("camera_model"),
        "camera_datetime": analysis_data.get("camera_datetime"),
        "camera_software": None
    }


def _build_detection_item(detection: dict, location_data: dict,
                         camera_info: Optional[dict], image_filename: str) -> dict:
    """Build a single detection item"""
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


def _build_risk_assessment(analysis_data: dict, processed_detections: List[dict]) -> dict:
    """Build risk assessment dict"""
    return {
        "level": analysis_data.get("risk_level") or "BAJO",
        "risk_score": analysis_data.get("risk_score", 0.0),
        "total_detections": analysis_data.get("total_detections", 0),
        "high_risk_count": sum(1 for d in processed_detections if d["risk_level"] == "ALTO"),
        "medium_risk_count": sum(1 for d in processed_detections if d["risk_level"] == "MEDIO"),
        "recommendations": ["Verificar detecciones", "Seguir protocolos de seguridad"]
    }


def _parse_iso_datetime(datetime_str: Optional[str]) -> datetime:
    """Parse ISO datetime string, return current time if invalid"""
    if not datetime_str:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return datetime.now(timezone.utc)


def _build_analysis_list_item(analysis: dict) -> dict:
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
        coords = _extract_gps_from_maps_url(google_maps_url)

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
    camera_info = _build_camera_info(analysis)

    # Build response item
    return {
        "id": uuid.UUID(analysis["id"]),
        "status": "completed",
        "image_url": analysis.get("image_url"),
        "image_filename": analysis.get("image_filename"),
        "processed_image_url": analysis.get("processed_image_url"),
        "processed_image_filename": analysis.get("processed_image_filename"),
        "image_size_bytes": analysis.get("image_size_bytes", 0),
        "location": location_data,
        "camera_info": camera_info,
        "model_used": analysis.get("model_used", "unknown"),
        "confidence_threshold": analysis.get("confidence_threshold", settings.yolo_confidence_threshold),
        "processing_time_ms": analysis.get("processing_time_ms", 0),
        "yolo_service_version": settings.yolo_service_version,
        "risk_assessment": {
            "level": analysis.get("risk_level") or "BAJO",
            "risk_score": analysis.get("risk_score", 0.0),
            "total_detections": analysis.get("total_detections", 0),
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "recommendations": []
        },
        "detections": [],  # Empty for list view (performance)
        "image_taken_at": _parse_iso_datetime(analysis.get("created_at")),
        "created_at": _parse_iso_datetime(analysis.get("created_at")),
        "updated_at": _parse_iso_datetime(analysis.get("updated_at"))
    }



@router.post("/analyses", response_model=AnalysisUploadResponse)
@limiter.limit("10/minute")  # SECURITY: Rate limit for authenticated users
async def create_analysis(
    request: Request,
    file: Optional[UploadFile] = File(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    confidence_threshold: Optional[float] = Form(None),
    include_gps: bool = Form(True),
    current_user: UserProfile = Depends(get_current_active_user)
):
    """
    Cargar imagen para analisis de criaderos de dengue con procesamiento real

    SECURITY: Rate limited to 10 requests per minute per user/IP
    """
    # Set default confidence threshold from settings
    if confidence_threshold is None:
        confidence_threshold = settings.yolo_confidence_threshold

    # Validate coordinates and confidence threshold
    _validate_coordinates(latitude, longitude)
    _validate_confidence_threshold(confidence_threshold)

    try:
        # SECURITY: Comprehensive file validation (size + MIME type + sanitization)
        image_data, safe_filename = await validate_uploaded_image(
            file,
            max_size=settings.max_file_size
        )
        logger.info(
            "file_validated",
            original_name=file.filename,
            safe_name=safe_filename,
            size_mb=len(image_data) / (1024 * 1024)
        )

        # Process image using service layer
        from src.services.analysis_service import analysis_service as service_instance

        result = await service_instance.process_image_analysis(
            image_data=image_data,
            filename=safe_filename,  # SECURITY: Use sanitized filename
            confidence_threshold=confidence_threshold,
            include_gps=include_gps,
            manual_latitude=latitude,
            manual_longitude=longitude,
            user_id=str(current_user.id)  # Pass user_id for RLS
        )

        # Validate result is not None
        if result is None:
            logger.error("analysis_service_returned_none", filename=file.filename)
            raise ImageProcessingException("Analysis processing returned no result")

        # Check if analysis creation failed
        if result.get("status") == "failed":
            error_msg = result.get("error", "Analysis creation failed")
            logger.error("analysis_creation_failed", filename=file.filename, error=error_msg)
            raise ImageProcessingException(f"Failed to create analysis: {error_msg}")

        # Build and return response
        return AnalysisUploadResponse(
            analysis_id=uuid.UUID(result["analysis_id"]),
            status=result["status"],
            has_gps_data=result.get("has_gps_data", False),
            camera_detected=result.get("camera_detected"),
            estimated_processing_time=f"{result.get('processing_time_ms', 0)}ms",
            message="Analisis completado exitosamente" if result["status"] == "completed"
                   else "Analisis en proceso"
        )

    except HTTPException:
        raise
    except httpx.TimeoutException:
        logger.error("yolo_timeout", timeout=settings.yolo_timeout_seconds)
        raise YOLOTimeoutException(timeout_seconds=settings.yolo_timeout_seconds)
    except httpx.HTTPStatusError as e:
        logger.error("yolo_http_error", status=e.response.status_code, error=str(e))
        raise YOLOServiceException(f"HTTP {e.response.status_code}: {str(e)}")
    except httpx.HTTPError as e:
        logger.error("yolo_connection_error", error=str(e))
        raise YOLOServiceException(f"Connection error: {str(e)}")
    except KeyError as e:
        logger.error("missing_required_field", field=str(e), exc_info=True)
        raise ImageProcessingException(f"Missing required field in processing result: {e}")
    except ValueError as e:
        logger.error("invalid_value_error", error=str(e), exc_info=True)
        raise ImageProcessingException(f"Invalid value during processing: {str(e)}")
    except Exception as e:
        logger.error("unexpected_processing_error", error=str(e), exc_info=True)
        raise ImageProcessingException(f"Unexpected error processing image: {str(e)}")


# ============================================
# Public Analysis Endpoint (No Authentication)
# ============================================

@router.post("/analyses/public")
@limiter.limit("3/minute")  # SECURITY: Strict rate limit for public endpoint
async def create_public_analysis(
    request: Request,
    file: Optional[UploadFile] = File(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    confidence_threshold: Optional[float] = Form(None),
    include_gps: bool = Form(True)
):
    """
    Public endpoint for quick analysis without authentication.

    SECURITY: Rate limited to 3 requests per minute per IP

    This endpoint is for demonstration purposes and public usage.
    Results are processed but NOT saved to the database.

    Args:
        file: Image file (multipart/form-data)
        latitude: Manual coordinate (optional, overrides EXIF)
        longitude: Manual coordinate (optional, overrides EXIF)
        confidence_threshold: Confidence threshold (default from settings)
        include_gps: Extract GPS automatically (default: true)

    Returns:
        Simplified analysis result with detections and risk level
    """
    # Set default confidence threshold from settings
    if confidence_threshold is None:
        confidence_threshold = settings.yolo_confidence_threshold

    # Validate coordinates and confidence threshold
    _validate_coordinates(latitude, longitude)
    _validate_confidence_threshold(confidence_threshold)

    try:
        # SECURITY: Comprehensive file validation (size + MIME type + sanitization)
        image_data, safe_filename = await validate_uploaded_image(
            file,
            max_size=settings.max_file_size
        )
        logger.info(
            "file_validated_public",
            original_name=file.filename,
            safe_name=safe_filename,
            size_mb=len(image_data) / (1024 * 1024)
        )

        # Process image using YOLO service directly (no database storage)
        from src.core.services.yolo_service import YOLOServiceClient

        yolo_client = YOLOServiceClient()

        # Call YOLO service with correct method name - use sanitized filename
        yolo_result = await yolo_client.detect_image(
            image_data=image_data,
            filename=safe_filename,  # SECURITY: Use sanitized filename
            confidence_threshold=confidence_threshold,
            include_gps=include_gps
        )

        # DEBUG: Log what YOLO returned
        logger.info(f"[GPS DEBUG PUBLIC] YOLO result keys: {yolo_result.keys()}")
        logger.info(f"[GPS DEBUG PUBLIC] location data: {yolo_result.get('location')}")

        # Build simplified response for public endpoint
        detections = []
        for detection in yolo_result.get("detections", []):
            detections.append({
                "type": detection.get("class_name", "Unknown"),
                "confidence": detection.get("confidence", 0.0),
                "bbox": detection.get("bbox", [0, 0, 0, 0])
            })

        # Get risk level from risk_assessment
        risk_assessment = yolo_result.get("risk_assessment", {})
        risk_level = risk_assessment.get("level", "BAJO")

        # Get processed image in base64 if available
        processed_image_base64 = yolo_result.get("processed_image_base64")
        processed_image_url = None

        if processed_image_base64:
            # Convert base64 to data URL for frontend display
            processed_image_url = f"data:image/jpeg;base64,{processed_image_base64}"
        elif len(detections) > 0:
            # If YOLO didn't return processed image but there are detections,
            # draw them manually to ensure user always sees the detections
            try:
                import base64
                from PIL import Image, ImageDraw
                import io

                # Load original image
                img = Image.open(io.BytesIO(image_data))
                draw = ImageDraw.Draw(img)

                # Draw bounding boxes for each detection
                for detection in yolo_result.get("detections", []):
                    bbox = detection.get("bbox", [])
                    if len(bbox) == 4:
                        x1, y1, x2, y2 = bbox
                        # Draw rectangle
                        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
                        # Add label
                        label = f"{detection.get('class_name', 'Unknown')} {detection.get('confidence', 0):.2f}"
                        draw.text((x1, y1 - 10), label, fill="red")

                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=90)
                buffer.seek(0)
                processed_image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
                processed_image_url = f"data:image/jpeg;base64,{processed_image_base64}"

                logger.info("drew_detections_manually", count=len(detections))
            except Exception as e:
                logger.warning("failed_to_draw_detections", error=str(e))
                # If drawing fails, at least return original image as base64
                processed_image_url = f"data:image/jpeg;base64,{base64.b64encode(image_data).decode('utf-8')}"

        # Extract GPS data from YOLO result
        location_info = yolo_result.get("location", {})
        gps_data = None

        # Check if manual coordinates were provided
        if latitude is not None and longitude is not None:
            gps_data = {
                "has_location": True,
                "latitude": latitude,
                "longitude": longitude,
                "location_source": "MANUAL",
                "google_maps_url": f"https://maps.google.com/?q={latitude},{longitude}"
            }
        # Otherwise check if YOLO extracted GPS from EXIF
        elif location_info and location_info.get("has_location"):
            gps_data = {
                "has_location": True,
                "latitude": location_info.get("latitude"),
                "longitude": location_info.get("longitude"),
                "altitude_meters": location_info.get("altitude_meters"),
                "location_source": location_info.get("location_source", "EXIF_GPS"),
                "google_maps_url": f"https://maps.google.com/?q={location_info.get('latitude')},{location_info.get('longitude')}"
            }
        else:
            gps_data = {"has_location": False}

        return {
            "id": str(uuid.uuid4()),
            "detections": detections,
            "risk_level": risk_level,
            "processed_image_url": processed_image_url,  # Imagen procesada temporal en base64
            "location": gps_data,
            "message": "Análisis completado. Para guardar resultados, crea una cuenta gratuita."
        }

    except HTTPException:
        raise
    except httpx.TimeoutException:
        logger.error("yolo_timeout_public", timeout=settings.yolo_timeout_seconds)
        raise YOLOTimeoutException(timeout_seconds=settings.yolo_timeout_seconds)
    except httpx.HTTPStatusError as e:
        logger.error("yolo_http_error_public", status=e.response.status_code, error=str(e))
        raise YOLOServiceException(f"HTTP {e.response.status_code}: {str(e)}")
    except httpx.HTTPError as e:
        logger.error("yolo_connection_error_public", error=str(e))
        raise YOLOServiceException(f"Connection error: {str(e)}")
    except Exception as e:
        logger.error("unexpected_public_processing_error", error=str(e), exc_info=True)
        raise ImageProcessingException(f"Unexpected error processing image: {str(e)}")


@router.get("/analyses/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: str,
    current_user: UserProfile = Depends(get_current_active_user)
):
    """
    Obtener analisis completo con detecciones georeferenciadas

    Args:
        analysis_id: UUID del analisis

    Returns:
        AnalysisResponse con informacion completa
    """
    logger.debug("get_analysis endpoint called", analysis_id=analysis_id)

    from src.services.analysis_service import analysis_service as service_instance

    # Fetch analysis from database
    analysis_data = await service_instance.get_analysis_by_id(analysis_id)
    if not analysis_data:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Build components using helper functions
    location_data = _build_location_data(analysis_data)
    camera_info = _build_camera_info(analysis_data)

    # Process detections
    processed_detections = [
        _build_detection_item(
            detection,
            location_data,
            camera_info,
            analysis_data.get("image_filename")
        )
        for detection in analysis_data.get("detections", [])
    ]

    # Build response
    return AnalysisResponse(
        id=uuid.UUID(analysis_data["id"]),
        status=analysis_data.get("status", "completed"),
        image_url=analysis_data.get("image_url"),
        image_filename=analysis_data.get("image_filename"),
        processed_image_url=analysis_data.get("processed_image_url"),
        processed_image_filename=analysis_data.get("processed_image_filename"),
        image_size_bytes=analysis_data.get("image_size_bytes", 0),
        location=location_data,
        camera_info=camera_info,
        model_used=analysis_data.get("model_used", "unknown"),
        confidence_threshold=analysis_data.get("confidence_threshold", settings.yolo_confidence_threshold),
        processing_time_ms=analysis_data.get("processing_time_ms", 0),
        yolo_service_version=settings.yolo_service_version,
        risk_assessment=_build_risk_assessment(analysis_data, processed_detections),
        detections=processed_detections,
        image_taken_at=_parse_iso_datetime(analysis_data.get("created_at")),
        created_at=_parse_iso_datetime(analysis_data.get("created_at")),
        updated_at=_parse_iso_datetime(analysis_data.get("updated_at"))
    )


@router.get("/analyses", response_model=AnalysisListResponse)
async def list_analyses(
    user_id: Optional[str] = None,
    has_gps: Optional[bool] = None,
    camera_make: Optional[str] = None,
    risk_level: Optional[str] = None,
    since: Optional[str] = None,
    limit: int = None,
    offset: int = 0,
    bbox: Optional[str] = None,
    current_user: Optional[UserProfile] = Depends(get_optional_current_user)
):
    """
    Listar analisis con filtros opcionales

    Authentication-aware endpoint:
    - Public (unauthenticated): Returns max 3 recent analyses for demo purposes
    - Authenticated: Returns all analyses from all users (up to default_pagination_limit)

    Query Parameters:
        user_id: Filtrar por usuario (optional)
        has_gps: Solo analisis con/sin GPS (true/false)
        camera_make: Filtrar por marca de camara
        bbox: Filtrar por bounding box geografico: sw_lat,sw_lng,ne_lat,ne_lng
        risk_level: Filtrar por nivel de riesgo
        since: Filtrar por fecha
        limit/offset: Paginacion
    """
    from src.services.analysis_service import analysis_service as service_instance

    # Apply authentication-aware limit
    if current_user is None:
        # Public access: limit to 3 recent analyses for demo
        if limit is None or limit > 3:
            limit = 3
        # Ignore user_id filter for unauthenticated users
        user_id = None
    else:
        # Authenticated access: use settings default or user-provided limit
        if limit is None:
            limit = settings.default_pagination_limit

    # Fetch analyses from database with filters
    result = await service_instance.list_analyses(
        limit=limit,
        offset=offset,
        user_id=user_id,
        has_gps=has_gps,
        risk_level=risk_level
    )

    # Transform to response format using helper
    analyses_responses = [
        AnalysisResponse(**_build_analysis_list_item(analysis))
        for analysis in result.get("analyses", [])
    ]

    return AnalysisListResponse(
        analyses=analyses_responses,
        total=result.get("total", 0),
        limit=limit,
        offset=offset,
        has_next=result.get("has_next", False)
    )


@router.post("/analyses/batch", response_model=BatchUploadResponse)
async def create_batch_analysis(
    request: BatchUploadRequest,
    current_user: UserProfile = Depends(get_current_active_user)
):
    """
    Procesamiento masivo con extracción GPS automática

    Args:
        request: Lista de URLs de imágenes para procesar

    Returns:
        BatchUploadResponse con lista de analysis_id
    """

    if len(request.image_urls) > settings.batch_max_images:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {settings.batch_max_images} images per batch"
        )

    batch_id = uuid.uuid4()
    analyses = []

    # Process images concurrently for better performance
    async def process_single_image(image_url: str) -> AnalysisUploadResponse:
        """Process a single image from URL"""
        try:
            # Download image from URL
            async with httpx.AsyncClient(timeout=settings.yolo_timeout_seconds) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                image_data = response.content

                # Extract filename from URL
                filename = image_url.split("/")[-1]
                if not filename.endswith(('.jpg', '.jpeg', '.png', '.tiff', '.heic')):
                    filename += '.jpg'

                # Process image using existing analysis service
                result = await analysis_service.process_image_from_data(
                    image_data=image_data,
                    filename=filename,
                    user_id=1,  # Default user for batch processing
                    confidence_threshold=settings.yolo_confidence_threshold,
                    latitude=None,
                    longitude=None
                )

                return AnalysisUploadResponse(
                    analysis_id=result["analysis_id"],
                    status="completed",
                    has_gps_data=result.get("has_gps_data", False),
                    camera_detected=result.get("camera_make"),
                    message="Processed successfully"
                )

        except httpx.TimeoutException:
            logger.warning("batch_image_download_timeout", url=image_url)
            return AnalysisUploadResponse(
                analysis_id=uuid.uuid4(),
                status="failed",
                has_gps_data=False,
                camera_detected=None,
                message=f"Download timeout for image: {image_url}"
            )
        except httpx.HTTPError as e:
            logger.warning("batch_image_download_failed", url=image_url, error=str(e))
            return AnalysisUploadResponse(
                analysis_id=uuid.uuid4(),
                status="failed",
                has_gps_data=False,
                camera_detected=None,
                message=f"Failed to download image: {str(e)}"
            )
        except Exception as e:
            logger.error("batch_image_processing_failed", url=image_url, error=str(e), exc_info=True)
            return AnalysisUploadResponse(
                analysis_id=uuid.uuid4(),
                status="failed",
                has_gps_data=False,
                camera_detected=None,
                message=f"Processing failed: {str(e)}"
            )

    # Process all images concurrently (configurable limit to avoid overwhelming)
    semaphore = asyncio.Semaphore(settings.batch_concurrent_limit)

    async def process_with_semaphore(image_url: str):
        async with semaphore:
            return await process_single_image(image_url)

    # Execute all processing tasks
    tasks = [process_with_semaphore(url) for url in request.image_urls]
    analyses = await asyncio.gather(*tasks, return_exceptions=False)

    # Calculate actual completion stats
    successful = sum(1 for analysis in analyses if analysis.status == "completed")
    failed = sum(1 for analysis in analyses if analysis.status == "failed")

    return BatchUploadResponse(
        batch_id=batch_id,
        total_images=len(request.image_urls),
        analyses=analyses,
        estimated_completion_time=f"Completed: {successful} successful, {failed} failed"
    )


@router.get("/test-image")
def get_test_image():
    """Test endpoint para servir imagen"""
    from fastapi.responses import Response
    from PIL import Image
    import io

    img = Image.new('RGB', (300, 200), color='blue')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    image_data = buffer.getvalue()

    return Response(
        content=image_data,
        media_type="image/jpeg"
    )


def _calculate_intensity(risk_level: str, detection_count: int) -> float:
    """
    Calculate heatmap intensity based on risk level and detection count.

    Args:
        risk_level: Risk level (ALTO, MEDIO, BAJO)
        detection_count: Number of detections

    Returns:
        float: Intensity value between 0.0 and 1.0
    """
    base_intensity = settings.heatmap_intensity_default

    if risk_level == "ALTO":
        base_intensity = settings.heatmap_intensity_high
    elif risk_level == "MEDIO":
        base_intensity = settings.heatmap_intensity_medium
    else:
        base_intensity = settings.heatmap_intensity_low

    # Add detection count bonus
    if risk_level in ["ALTO", "MEDIO"]:
        detection_bonus = min(
            detection_count * settings.heatmap_detection_bonus_high,
            settings.heatmap_max_bonus_high
        )
    else:
        detection_bonus = min(
            detection_count * settings.heatmap_detection_bonus_low,
            settings.heatmap_max_bonus_low
        )

    return round(min(base_intensity + detection_bonus, 1.0), 2)


def _build_heatmap_points(analysis: dict, current_user_id: Optional[str] = None) -> List[dict]:
    """
    Build heatmap points from analysis data, one per breeding site type.

    Creates separate points for each breeding site type found in detections,
    allowing different colors/intensities for garbage vs water vs holes etc.

    Args:
        analysis: Raw analysis data with google_maps_url and detections
        current_user_id: ID of current authenticated user (optional)

    Returns:
        list: List of heatmap points (one per breeding site type), or empty list if no valid coordinates
    """
    google_maps_url = analysis.get("google_maps_url", "")
    coords = _extract_gps_from_maps_url(google_maps_url)

    if not coords:
        return []

    lat, lng = coords
    risk_level = analysis.get("risk_level", "BAJO")
    detections = analysis.get("detections", [])
    analysis_user_id = analysis.get("user_id")

    # Determine if this analysis belongs to the current user
    is_own = current_user_id is not None and analysis_user_id is not None and str(analysis_user_id) == str(current_user_id)

    # If no detections with breeding site types, return single point with overall risk
    if not detections:
        return [{
            "latitude": lat,
            "longitude": lng,
            "intensity": _calculate_intensity(risk_level, 0),
            "riskLevel": risk_level,
            "detectionCount": 0,
            "breedingSiteType": None,
            "timestamp": analysis.get("created_at"),
            "isOwn": is_own
        }]

    # Group detections by breeding site type
    detections_by_type = {}
    for detection in detections:
        breeding_type = detection.get("breeding_site_type")
        if breeding_type:
            if breeding_type not in detections_by_type:
                detections_by_type[breeding_type] = []
            detections_by_type[breeding_type].append(detection)

    # Create one heatmap point per breeding site type
    points = []
    for breeding_type, type_detections in detections_by_type.items():
        # Calculate highest risk level among detections of this type
        type_risk_levels = [d.get("risk_level", "bajo") for d in type_detections]
        type_risk = "alto" if "alto" in type_risk_levels else (
            "medio" if "medio" in type_risk_levels else "bajo"
        )

        points.append({
            "latitude": lat,
            "longitude": lng,
            "intensity": _calculate_intensity(type_risk.upper(), len(type_detections)),
            "riskLevel": type_risk.upper(),
            "detectionCount": len(type_detections),
            "breedingSiteType": breeding_type,
            "timestamp": analysis.get("created_at"),
            "isOwn": is_own
        })

    return points

@router.get("/heatmap-data")
async def get_heatmap_data(
    limit: int = None,
    risk_level: Optional[str] = None,
    since: Optional[str] = None,
    current_user: Optional[UserProfile] = Depends(get_optional_current_user)
):
    """
    Obtener datos georeferenciados para visualización de mapa de calor

    Authentication-aware endpoint:
    - Public (unauthenticated): Returns max 10 points for demo purposes
    - Authenticated: Returns all points (up to heatmap_max_limit)

    Query Parameters:
        limit: Número máximo de puntos a retornar (default depends on auth)
        risk_level: Filtrar por nivel de riesgo (ALTO, MEDIO, BAJO)
        since: Filtrar análisis desde fecha ISO (ej: 2025-01-01T00:00:00Z)

    Returns:
        Datos de ubicaciones con intensidad de riesgo para heatmap
    """
    # Apply authentication-aware limit
    if current_user is None:
        # Public access: limit to 10 points for demo
        if limit is None or limit > 10:
            limit = 10
            logger.debug("public_heatmap_access", limit=limit)
    else:
        # Authenticated access: use settings default or user-provided limit
        if limit is None:
            limit = settings.heatmap_max_limit
            logger.debug("authenticated_heatmap_access", user_id=current_user.id, limit=limit)

    try:
        from src.services.analysis_service import analysis_service as service_instance

        # Use service layer method instead of direct database access
        result = await service_instance.get_heatmap_data(
            limit=limit,
            risk_level=risk_level,
            since=since
        )

        if not result.get("data"):
            return {
                "status": "success",
                "data": [],
                "total_locations": 0,
                "high_risk_count": 0,
                "medium_risk_count": 0,
                "low_risk_count": 0,
                "breeding_type_counts": {}
            }

        # Process analyses into heatmap points (multiple points per analysis, one per breeding site type)
        heatmap_points = []
        risk_counts = {"ALTO": 0, "MEDIO": 0, "BAJO": 0, "MINIMO": 0}
        breeding_type_counts = {}

        # Get current user ID for ownership check
        current_user_id = str(current_user.id) if current_user else None

        for analysis in result["data"]:
            points = _build_heatmap_points(analysis, current_user_id)
            for point in points:
                heatmap_points.append(point)
                # Count by risk level
                risk_level = point["riskLevel"]
                if risk_level in risk_counts:
                    risk_counts[risk_level] += 1
                # Count by breeding site type
                breeding_type = point.get("breedingSiteType")
                if breeding_type:
                    breeding_type_counts[breeding_type] = breeding_type_counts.get(breeding_type, 0) + 1

        return {
            "status": "success",
            "data": heatmap_points,
            "total_locations": len(heatmap_points),
            "high_risk_count": risk_counts["ALTO"],
            "medium_risk_count": risk_counts["MEDIO"],
            "low_risk_count": risk_counts["BAJO"] + risk_counts.get("MINIMO", 0),
            "breeding_type_counts": breeding_type_counts
        }

    except HTTPException:
        raise
    except DatabaseException:
        raise
    except Exception as e:
        logger.error("heatmap_fetch_error", error=str(e), exc_info=True)
        raise DatabaseException(f"Error fetching heatmap data: {str(e)}", operation="fetch_heatmap")

@router.get("/analyses/{analysis_id}/mock")
def get_analysis_mock(analysis_id: str):
    """Mock endpoint para datos de analisis simplificado"""
    import uuid
    from datetime import datetime

    return {
        "id": analysis_id,
        "status": "completed",
        "image_filename": f"test_analysis_{analysis_id[:8]}.jpg",
        "image_size_bytes": 24935,
        "location": {
            "has_location": True,
            "latitude": -26.8083,
            "longitude": -65.2176,
            "coordinates": "-26.8083,-65.2176",
            "location_source": "TEST",
            "google_maps_url": f"https://maps.google.com/?q=-26.8083,-65.2176"
        },
        "camera_info": {
            "camera_make": "Test Camera",
            "camera_model": "Mock Model",
            "camera_datetime": "2025-09-27T10:30:00Z"
        },
        "model_used": "dengue_test_v1",
        "confidence_threshold": settings.yolo_confidence_threshold,
        "processing_time_ms": 1500,
        "yolo_service_version": settings.yolo_service_version,
        "risk_assessment": {
            "level": "MEDIO",
            "risk_score": 0.75,
            "total_detections": 2,
            "high_risk_count": 0,
            "medium_risk_count": 2,
            "recommendations": ["Verificar área señalada", "Eliminar agua estancada"]
        },
        "detections": [
            {
                "id": str(uuid.uuid4()),
                "class_id": 1,
                "class_name": "Recipiente con agua",
                "confidence": 0.85,
                "risk_level": "MEDIO",
                "breeding_site_type": "RECIPIENTE",
                "polygon": [[30, 20], [70, 20], [70, 60], [30, 60]],
                "mask_area": 1600.0,
                "area_square_pixels": 1600.0,
                "location": {
                    "has_location": True,
                    "latitude": -26.8083,
                    "longitude": -65.2176
                },
                "validation_status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "class_id": 2,
                "class_name": "Charco de agua",
                "confidence": 0.72,
                "risk_level": "MEDIO",
                "breeding_site_type": "CHARCO",
                "polygon": [[10, 70], [40, 70], [40, 90], [10, 90]],
                "mask_area": 600.0,
                "area_square_pixels": 600.0,
                "location": {
                    "has_location": True,
                    "latitude": -26.8083,
                    "longitude": -65.2176
                },
                "validation_status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        ],
        "image_taken_at": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

@router.get("/analyses/{analysis_id}/image")
def get_analysis_image(analysis_id: str):
    """
    Servir imagen del analisis - TEST ENDPOINT

    Args:
        analysis_id: UUID del analisis

    Returns:
        Test image
    """
    from fastapi.responses import Response
    import pathlib

    # Crear una imagen simple en memoria si no existe test_image.jpg
    try:
        test_image_path = pathlib.Path("test_image.jpg")
        if test_image_path.exists():
            with open(test_image_path, "rb") as f:
                image_data = f.read()
        else:
            # Crear una imagen simple de 1x1 pixel
            from PIL import Image
            import io

            img = Image.new('RGB', (200, 200), color='red')
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG')
            image_data = buffer.getvalue()

        return Response(
            content=image_data,
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f"inline; filename=test_{analysis_id[:8]}.jpg"
            }
        )

    except FileNotFoundError as e:
        logger.error("test_image_not_found", error=str(e))
        raise HTTPException(status_code=404, detail="Test image not found")
    except OSError as e:
        logger.error("test_image_io_error", error=str(e), exc_info=True)
        raise ImageProcessingException(f"Error reading test image: {str(e)}")
    except Exception as e:
        logger.error("test_image_error", error=str(e), exc_info=True)
        raise ImageProcessingException(f"Error generating test image: {str(e)}")


def _count_risk_distribution(analyses: list) -> dict:
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


def _calculate_unique_locations(analyses: list) -> set:
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
        coords = _extract_gps_from_maps_url(google_maps_url)

        if coords:
            lat, lng = coords
            # Round to 3 decimals (~110m precision)
            unique_locations.add((round(lat, 3), round(lng, 3)))

    return unique_locations


def _calculate_detection_types(analyses: list) -> list:
    """
    Calculate detection counts by breeding site type.

    Args:
        analyses: List of analysis data dicts with detections

    Returns:
        list: Detection type counts [{"name": str, "value": int}, ...]
    """
    type_counts = {}

    for analysis in analyses:
        detections = analysis.get("detections", [])
        for detection in detections:
            # Get breeding site type from detection
            breeding_type = detection.get("breeding_site_type") or detection.get("class_name", "Desconocido")

            # Normalize breeding site type names
            if "BASURA" in breeding_type.upper() or "GARBAGE" in breeding_type.upper():
                breeding_type = "Basura"
            elif "CHARCO" in breeding_type.upper() or "AGUA" in breeding_type.upper() or "WATER" in breeding_type.upper():
                breeding_type = "Charcos/Agua"
            elif "HUECO" in breeding_type.upper() or "HOLE" in breeding_type.upper():
                breeding_type = "Huecos"
            elif "CALLE" in breeding_type.upper() or "STREET" in breeding_type.upper() or "ROAD" in breeding_type.upper():
                breeding_type = "Calles"

            type_counts[breeding_type] = type_counts.get(breeding_type, 0) + 1

    # Convert to array format expected by frontend
    return [{"name": name, "value": count} for name, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)]


def _calculate_weekly_trend(analyses: list) -> list:
    """
    Calculate detection trend for the last 7 days.

    Args:
        analyses: List of analysis data dicts

    Returns:
        list: Daily detection counts [{"day": str, "detections": int}, ...]
    """
    from collections import defaultdict

    # Get last 7 days
    now = datetime.now(timezone.utc)
    daily_counts = defaultdict(int)

    # Initialize all days with 0
    day_names = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    for i in range(7):
        day = now - timedelta(days=6-i)
        day_str = day_names[day.weekday()]
        daily_counts[day_str] = 0

    # Count detections per day
    for analysis in analyses:
        created_at_str = analysis.get("created_at")
        if not created_at_str:
            continue

        try:
            # Parse ISO format timestamp
            if isinstance(created_at_str, str):
                # Handle both formats: with and without timezone
                if 'T' in created_at_str:
                    if '+' in created_at_str or created_at_str.endswith('Z'):
                        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    else:
                        created_at = datetime.fromisoformat(created_at_str).replace(tzinfo=timezone.utc)
                else:
                    created_at = datetime.fromisoformat(created_at_str).replace(tzinfo=timezone.utc)
            else:
                created_at = created_at_str

            # Check if within last 7 days
            days_ago = (now - created_at).days
            if 0 <= days_ago < 7:
                day_str = day_names[created_at.weekday()]
                detection_count = len(analysis.get("detections", []))
                daily_counts[day_str] += detection_count
        except Exception as e:
            logger.warning("weekly_trend_date_parse_error", created_at=created_at_str, error=str(e))
            continue

    # Convert to array format expected by frontend
    result = []
    for i in range(7):
        day = now - timedelta(days=6-i)
        day_str = day_names[day.weekday()]
        result.append({"day": day_str, "detections": daily_counts[day_str]})

    return result


@router.get("/map-stats")
async def get_map_statistics():
    """
    Obtener estadísticas agregadas para visualización de mapa

    Returns:
        Estadísticas del sistema: total de análisis, detecciones,
        distribución de riesgo, área monitoreada, precisión del modelo,
        tipos de detecciones y tendencia semanal
    """
    try:
        from src.services.analysis_service import analysis_service as service_instance

        # Use service layer method instead of direct database access
        result = await service_instance.get_map_statistics()

        if not result.get("data"):
            return {
                "total_analyses": 0,
                "total_detections": 0,
                "locations_with_gps": 0,
                "total_area_detected_m2": 0,
                "model_accuracy": settings.model_accuracy_baseline,
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "risk_distribution": {"bajo": 0, "medio": 0, "alto": 0, "critico": 0},
                "active_zones": 0,
                "detection_types": [],
                "weekly_trend": []
            }

        # Calculate statistics using helpers
        analyses_data = result["data"]
        total_analyses = result["total_analyses"]
        total_detections = result["total_detections"]
        risk_counts = _count_risk_distribution(analyses_data)
        unique_locations = _calculate_unique_locations(analyses_data)
        detection_types = _calculate_detection_types(analyses_data)
        weekly_trend = _calculate_weekly_trend(analyses_data)

        # Count analyses with GPS coordinates
        locations_with_gps = len([a for a in analyses_data if a.get("has_gps_data")])

        # Calculate total area detected (sum of all detection areas from enriched data)
        total_area_detected_m2 = result.get("total_area_detected_m2", 0)

        # Get latest analysis timestamp
        last_analysis = max(analyses_data, key=lambda x: x.get("created_at", ""), default=None)
        last_updated = last_analysis.get("created_at") if last_analysis else datetime.now(timezone.utc).isoformat()

        # Model accuracy (TODO: implement real calculation with validation metrics)
        model_accuracy = settings.model_accuracy_baseline

        return {
            "total_analyses": total_analyses,
            "total_detections": total_detections,
            "locations_with_gps": locations_with_gps,
            "total_area_detected_m2": total_area_detected_m2,
            "model_accuracy": model_accuracy,
            "last_updated": last_updated,
            "risk_distribution": risk_counts,
            "active_zones": len(unique_locations),
            "detection_types": result.get("detection_types", []),
            "weekly_trend": result.get("weekly_trend", [])
        }

    except HTTPException:
        raise
    except DatabaseException:
        raise
    except Exception as e:
        logger.error("map_stats_fetch_error", error=str(e), exc_info=True)
        raise DatabaseException(f"Error fetching map statistics: {str(e)}", operation="fetch_map_stats")


# ============================================
# Async Task Queue Endpoints - Helper Functions
# ============================================

def _validate_async_file_upload(file: UploadFile, filename: Optional[str] = None) -> str:
    """
    Validate file upload for async analysis.

    Args:
        file: Uploaded file
        filename: Optional filename override

    Returns:
        str: Validated file extension

    Raises:
        HTTPException: If validation fails
    """
    if not file or not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Image file is required"
        )

    # Supported image formats
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.heic', '.heif', '.webp', '.bmp']

    file_ext = '.' + file.filename.split('.')[-1].lower()
    if file_ext not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {file_ext}. Supported: {', '.join(SUPPORTED_FORMATS)}"
        )

    return file_ext


async def _prepare_async_task_data(
    file: UploadFile,
    confidence_threshold: float
) -> tuple[bytes, str]:
    """
    Prepare image data for async processing.

    Args:
        file: Uploaded file
        confidence_threshold: Confidence threshold value

    Returns:
        tuple: (image_data, base64_encoded_data)

    Raises:
        HTTPException: If file is too large or invalid
    """
    import base64

    # Read image data
    image_data = await file.read()

    # Validate size
    max_size = settings.max_file_size
    if len(image_data) > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum {max_size // (1024*1024)}MB"
        )

    # Encode image data as base64 for Celery (JSON serializable)
    image_data_b64 = base64.b64encode(image_data).decode('utf-8')

    return image_data, image_data_b64


def _submit_celery_task(
    image_data_b64: str,
    filename: str,
    confidence_threshold: float,
    include_gps: bool,
    user_id: Optional[str],
    request_id: str,
    logger
):
    """
    Submit analysis task to Celery queue.

    Args:
        image_data_b64: Base64 encoded image data
        filename: Image filename
        confidence_threshold: Detection threshold
        include_gps: Whether to extract GPS
        user_id: User ID
        request_id: Request tracing ID
        logger: Logger instance

    Returns:
        Celery AsyncResult task
    """
    from ...tasks.analysis_tasks import process_image_analysis_task

    task = process_image_analysis_task.apply_async(
        kwargs={
            "image_data_b64": image_data_b64,
            "filename": filename,
            "confidence_threshold": confidence_threshold,
            "include_gps": include_gps,
            "user_id": user_id,
            "request_id": request_id
        }
    )

    logger.info(
        "async_analysis_submitted",
        task_id=task.id,
        filename=filename
    )

    return task


# ============================================
# Async Task Queue Status Helpers
# ============================================

def _build_task_response_pending(job_id: str) -> dict:
    """
    Build response dict for PENDING task state.

    Args:
        job_id: Celery task ID

    Returns:
        dict: Status response for pending state
    """
    return {
        "job_id": job_id,
        "status": "pending",
        "progress": 0,
        "message": "Task queued, waiting for worker"
    }


def _build_task_response_started(job_id: str) -> dict:
    """
    Build response dict for STARTED task state.

    Args:
        job_id: Celery task ID

    Returns:
        dict: Status response for started state
    """
    return {
        "job_id": job_id,
        "status": "processing",
        "progress": 50,
        "message": "Analysis in progress"
    }


def _build_task_response_success(job_id: str, result: any) -> dict:
    """
    Build response dict for SUCCESS task state.

    Args:
        job_id: Celery task ID
        result: Task result data

    Returns:
        dict: Status response for success state with result
    """
    return {
        "job_id": job_id,
        "status": "completed",
        "progress": 100,
        "result": result,
        "message": "Analysis completed successfully"
    }


def _build_task_response_failure(job_id: str, error_info: str, logger) -> dict:
    """
    Build response dict for FAILURE task state.

    Logs error and constructs failure response.

    Args:
        job_id: Celery task ID
        error_info: Error information from task
        logger: Logger instance

    Returns:
        dict: Status response for failure state with error
    """
    logger.error(
        "async_analysis_failed",
        job_id=job_id,
        error=error_info
    )

    return {
        "job_id": job_id,
        "status": "failed",
        "progress": 0,
        "error": error_info,
        "message": "Analysis failed"
    }


def _build_task_response_retry(job_id: str) -> dict:
    """
    Build response dict for RETRY task state.

    Args:
        job_id: Celery task ID

    Returns:
        dict: Status response for retry state
    """
    return {
        "job_id": job_id,
        "status": "retrying",
        "progress": 25,
        "message": "Analysis failed, retrying..."
    }


def _build_task_response_unknown(job_id: str, state: str) -> dict:
    """
    Build response dict for unknown task state.

    Args:
        job_id: Celery task ID
        state: Unknown task state

    Returns:
        dict: Status response for unknown state
    """
    return {
        "job_id": job_id,
        "status": state.lower(),
        "progress": 0,
        "message": f"Task in state: {state}"
    }


# ============================================
# Async Task Queue Endpoints
# ============================================

@router.post("/analyses/async")
async def create_analysis_async(
    file: UploadFile = File(...),
    confidence_threshold: float = Form(None),
    include_gps: bool = Form(True),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    current_user: UserProfile = Depends(get_current_active_user)
):
    """
    Submit image for async analysis using Celery task queue

    This endpoint immediately returns a job ID for polling,
    allowing the client to track progress without blocking.

    Benefits:
    - No timeout issues for large images or slow processing
    - Backend remains responsive under heavy load
    - Can handle hundreds of concurrent requests
    - Supports retry logic for failed analyses

    Args:
        file: Image file to analyze
        confidence_threshold: Detection confidence threshold (0.1-1.0)
        include_gps: Extract GPS metadata from image
        latitude: Manual latitude override
        longitude: Manual longitude override

    Returns:
        dict: Job ID and status URL for polling
    """
    from ...logging_config import get_logger, get_request_id
    from ...validators.analysis_validators import validate_confidence_threshold

    logger = get_logger(__name__)

    # Set default confidence threshold from settings
    if confidence_threshold is None:
        confidence_threshold = settings.yolo_confidence_threshold

    try:
        # Validate inputs
        _validate_async_file_upload(file)
        validate_confidence_threshold(confidence_threshold)

        # Prepare task data
        image_data, image_data_b64 = await _prepare_async_task_data(
            file,
            confidence_threshold
        )

        # Get request ID for distributed tracing
        request_id = get_request_id()

        logger.info(
            "submitting_async_analysis",
            filename=file.filename,
            file_size=len(image_data),
            confidence_threshold=confidence_threshold,
            user_id=current_user.id if current_user else None
        )

        # Submit to Celery
        task = _submit_celery_task(
            image_data_b64=image_data_b64,
            filename=file.filename,
            confidence_threshold=confidence_threshold,
            include_gps=include_gps,
            user_id=str(current_user.id) if current_user else None,
            request_id=request_id,
            logger=logger
        )

        return {
            "job_id": task.id,
            "status": "pending",
            "status_url": f"/api/v1/analyses/status/{task.id}",
            "message": "Analysis submitted successfully. Use status_url to check progress."
        }

    except HTTPException:
        raise
    except ValueError as e:
        logger.error("async_analysis_invalid_data", filename=file.filename if file else "unknown", error=str(e))
        raise ImageProcessingException(f"Invalid data for async analysis: {str(e)}")
    except Exception as e:
        logger.error(
            "async_analysis_submission_failed",
            filename=file.filename if file else "unknown",
            error=str(e),
            exc_info=True
        )
        raise ImageProcessingException(f"Failed to submit async analysis: {str(e)}")


@router.get("/analyses/status/{job_id}")
async def get_analysis_status(job_id: str):
    """
    Poll analysis job status

    Check the status of an async analysis job.
    The job progresses through states: PENDING → STARTED → SUCCESS/FAILURE

    States:
    - PENDING: Task queued, waiting for worker
    - STARTED: Worker processing the image
    - SUCCESS: Analysis completed, result available
    - FAILURE: Analysis failed, error available
    - RETRY: Task being retried after failure

    Args:
        job_id: Celery task ID returned from /analyses/async

    Returns:
        dict: Current status, progress, and result (if completed)
    """
    from celery.result import AsyncResult
    from ...celery_app import celery_app
    from ...logging_config import get_logger

    logger = get_logger(__name__)

    try:
        # Get task result
        task = AsyncResult(job_id, app=celery_app)

        # Route to appropriate response builder based on state
        if task.state == "PENDING":
            return _build_task_response_pending(job_id)

        elif task.state == "STARTED":
            return _build_task_response_started(job_id)

        elif task.state == "SUCCESS":
            return _build_task_response_success(job_id, task.result)

        elif task.state == "FAILURE":
            error_info = str(task.info) if task.info else "Unknown error"
            return _build_task_response_failure(job_id, error_info, logger)

        elif task.state == "RETRY":
            return _build_task_response_retry(job_id)

        else:
            return _build_task_response_unknown(job_id, task.state)

    except ImportError as e:
        logger.error("celery_not_available", error=str(e))
        raise HTTPException(
            status_code=503,
            detail="Task queue service not available"
        )
    except Exception as e:
        logger.error(
            "status_check_failed",
            job_id=job_id,
            error=str(e),
            exc_info=True
        )
        raise DatabaseException(f"Failed to check task status: {str(e)}", operation="check_celery_status")