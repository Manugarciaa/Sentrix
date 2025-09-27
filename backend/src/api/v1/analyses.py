"""
Analysis endpoints for image processing and breeding site detection
Endpoints de análisis para procesamiento de imágenes y detección de criaderos
"""

import uuid
import asyncio
import httpx
import os
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse, FileResponse

from ...schemas.analyses import (
    AnalysisUploadRequest, AnalysisUploadResponse,
    AnalysisResponse, AnalysisListQuery, AnalysisListResponse,
    BatchUploadRequest, BatchUploadResponse
)
from ...services.analysis_service import analysis_service
from ...config import get_settings

router = APIRouter()
settings = get_settings()



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

    # Validar extensión usando shared library
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    from shared import is_format_supported, SUPPORTED_IMAGE_FORMATS

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="El archivo debe tener un nombre válido"
        )

    file_ext = '.' + file.filename.split('.')[-1].lower()
    if not is_format_supported(file_ext):
        supported_formats = list(SUPPORTED_IMAGE_FORMATS.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado: {file_ext}. Formatos soportados: {', '.join(supported_formats)}"
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

        # Import analysis service at the top level to avoid circular imports
        from ...services.analysis_service import analysis_service as service_instance

        # Procesar imagen con servicio de análisis
        result = await service_instance.process_image_analysis(
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

    print(f"ENDPOINT CALLED: get_analysis for ID {analysis_id}")

    from ..services.analysis_service import analysis_service as service_instance

    # Obtener análisis real desde base de datos
    analysis_data = await service_instance.get_analysis_by_id(analysis_id)

    if not analysis_data:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Construir ubicación desde datos del análisis - SIMPLIFIED
    location_data = {"has_location": False}
    print(f"ENDPOINT DEBUG: Building location for {analysis_id}")
    print(f"ENDPOINT DEBUG: has_gps_data = {analysis_data.get('has_gps_data')}")
    print(f"ENDPOINT DEBUG: google_maps_url = {analysis_data.get('google_maps_url')}")

    if analysis_data.get("has_gps_data") and analysis_data.get("google_maps_url"):
        google_maps_url = analysis_data.get("google_maps_url")
        if "q=" in google_maps_url:
            try:
                coords_part = google_maps_url.split("q=")[1]
                if "," in coords_part:
                    lat_str, lng_str = coords_part.split(",", 1)
                    lat = float(lat_str)
                    lng = float(lng_str)

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
                    print(f"ENDPOINT DEBUG: Successfully built location data with lat={lat}, lng={lng}")
            except Exception as e:
                print(f"ENDPOINT DEBUG: Error parsing coordinates: {e}")
    else:
        print(f"ENDPOINT DEBUG: No GPS data or google_maps_url missing")

    # Construir información de cámara
    camera_info = None
    if analysis_data.get("camera_make"):
        camera_info = {
            "camera_make": analysis_data.get("camera_make"),
            "camera_model": analysis_data.get("camera_model"),
            "camera_datetime": analysis_data.get("camera_datetime"),
            "camera_software": None
        }

    # Procesar detecciones
    processed_detections = []
    for detection in analysis_data.get("detections", []):
        processed_detection = {
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
            "source_filename": analysis_data.get("image_filename"),
            "camera_info": camera_info,
            "validation_status": "pending",
            "validation_notes": None,
            "validated_at": None,
            "created_at": detection.get("created_at")
        }
        processed_detections.append(processed_detection)

    response = AnalysisResponse(
        id=uuid.UUID(analysis_data["id"]),
        status=analysis_data.get("status", "completed"),
        image_filename=analysis_data.get("image_filename"),
        image_size_bytes=analysis_data.get("image_size_bytes", 0),
        location=location_data,
        camera_info=camera_info,
        model_used=analysis_data.get("model_used", "unknown"),
        confidence_threshold=analysis_data.get("confidence_threshold", 0.5),
        processing_time_ms=analysis_data.get("processing_time_ms", 0),
        yolo_service_version="2.0.0",
        risk_assessment={
            "level": analysis_data.get("risk_level") or "BAJO",
            "risk_score": analysis_data.get("risk_score", 0.0),
            "total_detections": analysis_data.get("total_detections", 0),
            "high_risk_count": sum(1 for d in processed_detections if d["risk_level"] == "ALTO"),
            "medium_risk_count": sum(1 for d in processed_detections if d["risk_level"] == "MEDIO"),
            "recommendations": ["Verificar detecciones", "Seguir protocolos de seguridad"]
        },
        detections=processed_detections,
        image_taken_at=datetime.fromisoformat(analysis_data["created_at"].replace("Z", "+00:00")) if analysis_data.get("created_at") else datetime.utcnow(),
        created_at=datetime.fromisoformat(analysis_data["created_at"].replace("Z", "+00:00")) if analysis_data.get("created_at") else datetime.utcnow(),
        updated_at=datetime.fromisoformat(analysis_data["updated_at"].replace("Z", "+00:00")) if analysis_data.get("updated_at") else datetime.utcnow()
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

    from ..services.analysis_service import analysis_service as service_instance

    # Obtener análisis desde base de datos con filtros
    result = await service_instance.list_analyses(
        limit=limit,
        offset=offset,
        user_id=user_id,
        has_gps=has_gps,
        risk_level=risk_level
    )

    # Convertir análisis a formato de respuesta
    analyses_responses = []
    for analysis in result.get("analyses", []):
        # Construir ubicación con coordenadas si están disponibles
        location_data = {"has_location": False}
        if analysis.get("has_gps_data"):
            # Extract GPS coordinates from Google Maps URL stored in analysis
            google_maps_url = analysis.get("google_maps_url")
            if google_maps_url and "q=" in google_maps_url:
                coords_part = google_maps_url.split("q=")[1]
                if "," in coords_part:
                    lat_str, lng_str = coords_part.split(",", 1)
                    try:
                        lat = float(lat_str)
                        lng = float(lng_str)
                        location_data = {
                            "has_location": True,
                            "latitude": lat,
                            "longitude": lng,
                            "coordinates": f"{lat},{lng}",
                            "location_source": analysis.get("location_source", "UNKNOWN"),
                            "google_maps_url": google_maps_url,
                            "google_earth_url": analysis.get("google_earth_url")
                        }
                    except ValueError:
                        pass

        # Construir información de cámara
        camera_info = None
        if analysis.get("camera_make"):
            camera_info = {
                "camera_make": analysis.get("camera_make"),
                "camera_model": analysis.get("camera_model"),
                "camera_datetime": analysis.get("camera_datetime"),
                "camera_software": None
            }

        analysis_response = AnalysisResponse(
            id=uuid.UUID(analysis["id"]),
            status="completed",
            image_filename=analysis.get("image_filename"),
            image_size_bytes=analysis.get("image_size_bytes", 0),
            location=location_data,
            camera_info=camera_info,
            model_used=analysis.get("model_used", "unknown"),
            confidence_threshold=analysis.get("confidence_threshold", 0.5),
            processing_time_ms=analysis.get("processing_time_ms", 0),
            yolo_service_version="2.0.0",
            risk_assessment={
                "level": analysis.get("risk_level") or "BAJO",
                "risk_score": analysis.get("risk_score", 0.0),
                "total_detections": analysis.get("total_detections", 0),
                "high_risk_count": 0,  # Calculated from detections if needed
                "medium_risk_count": 0,
                "recommendations": []
            },
            detections=[],  # Empty for list view (performance)
            image_taken_at=datetime.fromisoformat(analysis["created_at"].replace("Z", "+00:00")) if analysis.get("created_at") else datetime.utcnow(),
            created_at=datetime.fromisoformat(analysis["created_at"].replace("Z", "+00:00")) if analysis.get("created_at") else datetime.utcnow(),
            updated_at=datetime.fromisoformat(analysis["updated_at"].replace("Z", "+00:00")) if analysis.get("updated_at") else datetime.utcnow()
        )
        analyses_responses.append(analysis_response)

    return AnalysisListResponse(
        analyses=analyses_responses,
        total=result.get("total", 0),
        limit=limit,
        offset=offset,
        has_next=result.get("has_next", False)
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

    # Process images concurrently for better performance
    async def process_single_image(image_url: str) -> AnalysisUploadResponse:
        """Process a single image from URL"""
        try:
            # Download image from URL
            async with httpx.AsyncClient(timeout=30.0) as client:
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
                    confidence_threshold=0.5,
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

        except httpx.HTTPError as e:
            # Return error response for failed downloads
            return AnalysisUploadResponse(
                analysis_id=uuid.uuid4(),
                status="failed",
                has_gps_data=False,
                camera_detected=None,
                message=f"Failed to download image: {str(e)}"
            )
        except Exception as e:
            # Return error response for processing failures
            return AnalysisUploadResponse(
                analysis_id=uuid.uuid4(),
                status="failed",
                has_gps_data=False,
                camera_detected=None,
                message=f"Processing failed: {str(e)}"
            )

    # Process all images concurrently (max 10 at a time to avoid overwhelming)
    semaphore = asyncio.Semaphore(10)

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


@router.get("/analyses/{analysis_id}/image")
async def get_analysis_image(analysis_id: str):
    """
    Servir imagen del análisis

    Args:
        analysis_id: UUID del análisis

    Returns:
        FileResponse con la imagen
    """
    from ..services.analysis_service import analysis_service as service_instance

    # Obtener datos del análisis para verificar que existe
    analysis_data = await service_instance.get_analysis_by_id(analysis_id)

    if not analysis_data:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Path donde se guardan las imágenes (ajustar según tu configuración)
    # Por ahora usar un path temporal o mockup
    image_filename = analysis_data.get("image_filename", "default.jpg")

    # TODO: Implementar storage real de imágenes
    # Por ahora retornar una imagen de ejemplo o 404
    image_path = f"/tmp/sentrix_images/{analysis_id}_{image_filename}"

    if not os.path.exists(image_path):
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(image_path), exist_ok=True)

        # Por ahora, retornar 404 ya que no tenemos storage implementado
        raise HTTPException(
            status_code=404,
            detail="Image file not found. Image storage not implemented yet."
        )

    return FileResponse(
        path=image_path,
        media_type="image/jpeg",
        filename=image_filename
    )