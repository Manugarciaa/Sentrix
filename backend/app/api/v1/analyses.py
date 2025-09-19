"""
Analysis endpoints for image processing and breeding site detection
Endpoints de análisis para procesamiento de imágenes y detección de criaderos
"""

import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse

from app.schemas.analyses import (
    AnalysisUploadRequest, AnalysisUploadResponse,
    AnalysisResponse, AnalysisListQuery, AnalysisListResponse,
    BatchUploadRequest, BatchUploadResponse
)
from app.services.analysis_service import analysis_service
from app.config import get_settings

router = APIRouter()
settings = get_settings()

# Mock storage for development (replace with actual database later)
MOCK_ANALYSES = {}


@router.post("/analyses", response_model=AnalysisUploadResponse)
async def create_analysis(
    file: Optional[UploadFile] = File(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    confidence_threshold: Optional[float] = Form(0.5),
    include_gps: bool = Form(True)
):
    """
    Cargar imagen para análisis de criaderos de dengue con procesamiento real

    Args:
        file: Archivo de imagen (multipart/form-data)
        latitude: Coordenada manual (opcional, sobrescribe EXIF)
        longitude: Coordenada manual (opcional, sobrescribe EXIF)
        confidence_threshold: Umbral de confianza (default: 0.5)
        include_gps: Extraer GPS automáticamente (default: true)

    Returns:
        AnalysisUploadResponse con analysis_id y status
    """

    # Validación de archivo
    if not file:
        raise HTTPException(
            status_code=400,
            detail="Se requiere un archivo de imagen"
        )

    # Validar extensión
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="El archivo debe tener un nombre válido"
        )

    allowed_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
    file_ext = file.filename.split('.')[-1].lower()
    if f'.{file_ext}' not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Extensión no permitida. Use: {', '.join(allowed_extensions)}"
        )

    # Validar coordenadas si se proporcionan
    if (latitude is not None and longitude is None) or (longitude is not None and latitude is None):
        raise HTTPException(
            status_code=400,
            detail="Si proporciona coordenadas, tanto latitud como longitud son requeridas"
        )

    # Validar umbral de confianza
    if not 0.1 <= confidence_threshold <= 1.0:
        raise HTTPException(
            status_code=400,
            detail="confidence_threshold debe estar entre 0.1 y 1.0"
        )

    try:
        # Leer datos del archivo
        image_data = await file.read()

        # Validar tamaño
        max_size = 50 * 1024 * 1024  # 50MB
        if len(image_data) > max_size:
            raise HTTPException(
                status_code=413,
                detail="El archivo es demasiado grande. Máximo 50MB"
            )

        # Procesar imagen con servicio de análisis
        result = await analysis_service.process_image_analysis(
            image_data=image_data,
            filename=file.filename,
            confidence_threshold=confidence_threshold,
            include_gps=include_gps,
            manual_latitude=latitude,
            manual_longitude=longitude
        )

        return AnalysisUploadResponse(
            analysis_id=uuid.UUID(result["analysis_id"]),
            status=result["status"],
            has_gps_data=result.get("has_gps_data", False),
            camera_detected=result.get("camera_detected"),
            estimated_processing_time=f"{result.get('processing_time_ms', 0)}ms",
            message="Análisis completado exitosamente" if result["status"] == "completed"
                   else "Análisis en proceso"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando imagen: {str(e)}"
        )


@router.get("/analyses/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: str):
    """
    Obtener análisis completo con detecciones georeferenciadas

    Args:
        analysis_id: UUID del análisis

    Returns:
        AnalysisResponse con información completa
    """

    # Check if analysis exists in mock storage
    if analysis_id not in MOCK_ANALYSES:
        raise HTTPException(status_code=404, detail="Analysis not found")

    mock_analysis = MOCK_ANALYSES[analysis_id]

    # Mock complete analysis response
    # In real implementation, this would fetch from database with joins

    response = AnalysisResponse(
        id=uuid.UUID(analysis_id),
        status=mock_analysis["status"],
        image_filename=mock_analysis["image_filename"],
        image_size_bytes=1024000,  # Mock size

        # Mock location data
        location={
            "has_location": mock_analysis["has_gps_data"],
            "latitude": -26.831314 if mock_analysis["has_gps_data"] else None,
            "longitude": -65.195539 if mock_analysis["has_gps_data"] else None,
            "coordinates": "-26.831314,-65.195539" if mock_analysis["has_gps_data"] else None,
            "altitude_meters": 458.2 if mock_analysis["has_gps_data"] else None,
            "location_source": "EXIF_GPS" if mock_analysis["has_gps_data"] else None,
            "google_maps_url": "https://maps.google.com/?q=-26.831314,-65.195539" if mock_analysis["has_gps_data"] else None,
            "google_earth_url": "https://earth.google.com/web/search/-26.831314,-65.195539" if mock_analysis["has_gps_data"] else None
        } if mock_analysis["has_gps_data"] else {"has_location": False},

        # Mock camera info
        camera_info={
            "camera_make": "Xiaomi",
            "camera_model": "220333QL",
            "camera_datetime": "2025:08:29 15:19:08",
            "camera_software": "Unknown"
        } if mock_analysis["camera_detected"] else None,

        # Mock processing info
        model_used="yolo11s-seg.pt",
        confidence_threshold=mock_analysis["confidence_threshold"],
        processing_time_ms=1234,
        yolo_service_version="2.0.0",

        # Mock risk assessment
        risk_assessment={
            "level": "MEDIUM",
            "risk_score": 0.75,
            "total_detections": 2,
            "high_risk_count": 1,
            "medium_risk_count": 1,
            "recommendations": ["Monitoreo regular", "Eliminación de desechos"]
        },

        # Mock detections
        detections=[
            {
                "id": uuid.uuid4(),
                "class_id": 0,
                "class_name": "Basura",
                "confidence": 0.364,
                "risk_level": "MEDIO",
                "breeding_site_type": "Basura",
                "polygon": [[3837.75, 1336.25], [3837.75, 1502.0], [4002.0, 1502.0], [4002.0, 1336.25]],
                "mask_area": 1718.0,
                "area_square_pixels": 1718.0,
                "location": {
                    "has_location": mock_analysis["has_gps_data"],
                    "latitude": -26.831314 if mock_analysis["has_gps_data"] else None,
                    "longitude": -65.195539 if mock_analysis["has_gps_data"] else None,
                    "coordinates": "-26.831314,-65.195539" if mock_analysis["has_gps_data"] else None,
                    "google_maps_url": "https://maps.google.com/?q=-26.831314,-65.195539" if mock_analysis["has_gps_data"] else None
                } if mock_analysis["has_gps_data"] else {"has_location": False},
                "source_filename": mock_analysis["image_filename"],
                "camera_info": {
                    "camera_make": "Xiaomi",
                    "camera_model": "220333QL",
                    "camera_datetime": "2025:08:29 15:19:08"
                } if mock_analysis["camera_detected"] else None,
                "validation_status": "pending",
                "validation_notes": None,
                "validated_at": None,
                "created_at": mock_analysis["created_at"]
            }
        ],

        # Timestamps
        image_taken_at=datetime.utcnow(),
        created_at=mock_analysis["created_at"],
        updated_at=datetime.utcnow()
    )

    return response


@router.get("/analyses", response_model=AnalysisListResponse)
async def list_analyses(
    user_id: Optional[str] = None,
    has_gps: Optional[bool] = None,
    camera_make: Optional[str] = None,
    risk_level: Optional[str] = None,
    since: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    bbox: Optional[str] = None
):
    """
    Listar análisis con filtros opcionales

    Query Parameters:
        user_id: Filtrar por usuario
        has_gps: Solo análisis con/sin GPS (true/false)
        camera_make: Filtrar por marca de cámara
        bbox: Filtrar por bounding box geográfico: sw_lat,sw_lng,ne_lat,ne_lng
        risk_level: Filtrar por nivel de riesgo
        since: Filtrar por fecha
        limit/offset: Paginación
    """

    # Mock filtering and pagination
    filtered_analyses = []

    for analysis_id, analysis_data in MOCK_ANALYSES.items():
        # Apply filters (mock implementation)
        if has_gps is not None and analysis_data["has_gps_data"] != has_gps:
            continue

        # Create mock response for each analysis
        mock_response = AnalysisResponse(
            id=uuid.UUID(analysis_id),
            status=analysis_data["status"],
            image_filename=analysis_data["image_filename"],
            location={"has_location": analysis_data["has_gps_data"]} if analysis_data["has_gps_data"] else {"has_location": False},
            camera_info={
                "camera_make": "Xiaomi" if analysis_data["camera_detected"] else None
            } if analysis_data["camera_detected"] else None,
            risk_assessment={
                "level": "MEDIUM",
                "total_detections": 1
            },
            detections=[],
            created_at=analysis_data["created_at"],
            updated_at=datetime.utcnow()
        )

        filtered_analyses.append(mock_response)

    # Apply pagination
    total = len(filtered_analyses)
    paginated = filtered_analyses[offset:offset + limit]

    return AnalysisListResponse(
        analyses=paginated,
        total=total,
        limit=limit,
        offset=offset,
        has_next=offset + limit < total
    )


@router.post("/analyses/batch", response_model=BatchUploadResponse)
async def create_batch_analysis(request: BatchUploadRequest):
    """
    Procesamiento masivo con extracción GPS automática

    Args:
        request: Lista de URLs de imágenes para procesar

    Returns:
        BatchUploadResponse con lista de analysis_id
    """

    if len(request.image_urls) > 50:
        raise HTTPException(
            status_code=400,
            detail="Maximum 50 images per batch"
        )

    batch_id = uuid.uuid4()
    analyses = []

    # Process each image URL
    for image_url in request.image_urls:
        analysis_id = uuid.uuid4()

        # Mock analysis creation
        mock_analysis = {
            "id": analysis_id,
            "status": "pending",
            "image_filename": image_url.split("/")[-1],
            "has_gps_data": bool(uuid.uuid4().int % 2),  # Random GPS availability
            "confidence_threshold": request.confidence_threshold,
            "created_at": datetime.utcnow()
        }

        MOCK_ANALYSES[str(analysis_id)] = mock_analysis

        analyses.append(AnalysisUploadResponse(
            analysis_id=analysis_id,
            status="pending",
            has_gps_data=mock_analysis["has_gps_data"],
            camera_detected=None,  # Will be detected during processing
            message="Queued for batch processing"
        ))

    # Estimate completion time based on batch size
    estimated_minutes = len(request.image_urls) * 1  # 1 minute per image

    return BatchUploadResponse(
        batch_id=batch_id,
        total_images=len(request.image_urls),
        analyses=analyses,
        estimated_completion_time=f"{estimated_minutes}-{estimated_minutes*2} minutes"
    )