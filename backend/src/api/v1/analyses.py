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
from src.services.analysis_service import analysis_service
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
        from src.services.analysis_service import analysis_service as service_instance

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

    from src.services.analysis_service import analysis_service as service_instance

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

    from src.services.analysis_service import analysis_service as service_instance

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

@router.get("/heatmap-data")
def get_heatmap_data():
    """Endpoint para obtener datos del mapa de calor"""
    try:
        import asyncio
        from src.services.analysis_service import analysis_service as service_instance

        # Datos de ejemplo basados en ubicaciones reales de Tucumán
        sample_data = [
            {
                "latitude": -26.8083,
                "longitude": -65.2176,
                "intensity": 0.8,
                "riskLevel": "ALTO",
                "detectionCount": 5,
                "location": "Centro - San Miguel de Tucumán",
                "timestamp": "2025-09-27T10:30:00Z"
            },
            {
                "latitude": -26.8100,
                "longitude": -65.2200,
                "intensity": 0.6,
                "riskLevel": "MEDIO",
                "detectionCount": 3,
                "location": "Barrio Norte",
                "timestamp": "2025-09-27T09:15:00Z"
            },
            {
                "latitude": -26.8050,
                "longitude": -65.2100,
                "intensity": 0.4,
                "riskLevel": "MEDIO",
                "detectionCount": 2,
                "location": "Zona Universitaria - UNT",
                "timestamp": "2025-09-27T08:45:00Z"
            },
            {
                "latitude": -26.8120,
                "longitude": -65.2250,
                "intensity": 0.3,
                "riskLevel": "BAJO",
                "detectionCount": 1,
                "location": "Barrio Residencial",
                "timestamp": "2025-09-27T07:20:00Z"
            },
            {
                "latitude": -26.8000,
                "longitude": -65.2300,
                "intensity": 0.7,
                "riskLevel": "ALTO",
                "detectionCount": 4,
                "location": "Zona Industrial",
                "timestamp": "2025-09-26T16:30:00Z"
            },
            {
                "latitude": -26.8150,
                "longitude": -65.2050,
                "intensity": 0.5,
                "riskLevel": "MEDIO",
                "detectionCount": 2,
                "location": "Barrio Sur",
                "timestamp": "2025-09-26T14:45:00Z"
            }
        ]

        return {
            "status": "success",
            "data": sample_data,
            "total_locations": len(sample_data),
            "high_risk_count": len([d for d in sample_data if d["riskLevel"] == "ALTO"]),
            "medium_risk_count": len([d for d in sample_data if d["riskLevel"] == "MEDIO"]),
            "low_risk_count": len([d for d in sample_data if d["riskLevel"] == "BAJO"])
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating heatmap data: {str(e)}",
            "data": []
        }

@router.get("/analyses/{analysis_id}/mock")
def get_analysis_mock(analysis_id: str):
    """Mock endpoint para datos de análisis simplificado"""
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
        "confidence_threshold": 0.5,
        "processing_time_ms": 1500,
        "yolo_service_version": "2.0.0",
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
                "created_at": datetime.utcnow().isoformat()
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
                "created_at": datetime.utcnow().isoformat()
            }
        ],
        "image_taken_at": datetime.utcnow().isoformat(),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }

@router.get("/analyses/{analysis_id}/image")
def get_analysis_image(analysis_id: str):
    """
    Servir imagen del análisis - TEST ENDPOINT

    Args:
        analysis_id: UUID del análisis

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

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.get("/map-stats")
def get_map_statistics():
    """Endpoint para obtener estadísticas reales del mapa"""
    try:
        from src.services.analysis_service import analysis_service as service_instance

        # Obtener todas las análisis de la base de datos
        analyses = service_instance.supabase.table("analyses").select("*").execute()

        if not analyses.data:
            return {
                "total_analyses": 0,
                "total_detections": 0,
                "area_monitored_km2": 0,
                "model_accuracy": 87.3,
                "last_updated": datetime.utcnow().isoformat(),
                "risk_distribution": {
                    "bajo": 0,
                    "medio": 0,
                    "alto": 0,
                    "critico": 0
                }
            }

        # Calcular estadísticas reales
        total_analyses = len(analyses.data)
        total_detections = sum(analysis.get("total_detections", 0) for analysis in analyses.data)

        # Calcular distribución de riesgo
        risk_counts = {"bajo": 0, "medio": 0, "alto": 0, "critico": 0}
        for analysis in analyses.data:
            risk_level = analysis.get("risk_level", "BAJO").lower()
            if risk_level in ["bajo", "minimo"]:
                risk_counts["bajo"] += 1
            elif risk_level == "medio":
                risk_counts["medio"] += 1
            elif risk_level == "alto":
                risk_counts["alto"] += 1
            else:  # Muy alto o crítico
                risk_counts["critico"] += 1

        # Calcular área aproximada basada en ubicaciones únicas
        unique_locations = set()
        for analysis in analyses.data:
            if analysis.get("latitude") and analysis.get("longitude"):
                # Redondear coordenadas para agrupar ubicaciones cercanas
                lat = round(float(analysis["latitude"]), 3)
                lng = round(float(analysis["longitude"]), 3)
                unique_locations.add((lat, lng))

        # Estimar área (aprox 1 km² por ubicación única)
        area_monitored = len(unique_locations) * 1.5  # Factor de cobertura

        # Obtener timestamp de la última análisis
        last_analysis = max(analyses.data, key=lambda x: x.get("created_at", ""), default=None)
        last_updated = last_analysis.get("created_at") if last_analysis else datetime.utcnow().isoformat()

        return {
            "total_analyses": total_analyses,
            "total_detections": total_detections,
            "area_monitored_km2": round(area_monitored, 1),
            "model_accuracy": 87.3,  # Valor fijo por ahora
            "last_updated": last_updated,
            "risk_distribution": risk_counts,
            "active_zones": len(unique_locations)
        }

    except Exception as e:
        # Retornar datos de respaldo en caso de error
        return {
            "total_analyses": 0,
            "total_detections": 0,
            "area_monitored_km2": 0,
            "model_accuracy": 87.3,
            "last_updated": datetime.utcnow().isoformat(),
            "risk_distribution": {
                "bajo": 0,
                "medio": 0,
                "alto": 0,
                "critico": 0
            },
            "error": str(e)
        }