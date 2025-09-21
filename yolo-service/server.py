"""
FastAPI Server for YOLO Dengue Detection Service
Servidor FastAPI para el Servicio de Detección de Criaderos de Dengue

Reutiliza las funciones existentes de detección y evaluación
"""

import os
import sys
import tempfile
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Agregar src al path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.detector import detect_breeding_sites
from src.core.evaluator import assess_dengue_risk, process_image_for_detection
from src.utils.file_ops import validate_file_exists

app = FastAPI(
    title="YOLO Dengue Detection Service",
    description="Servicio de detección de criaderos de dengue usando YOLO",
    version="1.0.0"
)

# CORS middleware - Configuración segura
allowed_origins = [
    "http://localhost:8000",  # Backend service
    "http://localhost:3000",  # Frontend development
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
]

# Add production origins from environment if available
if production_origins := os.getenv("ALLOWED_ORIGINS"):
    allowed_origins.extend(production_origins.split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Configuración del modelo (usar el modelo entrenado disponible)
MODEL_PATH = "models/best.pt"  # Ajustar según modelo disponible
if not os.path.exists(MODEL_PATH):
    # Fallback a modelos base si no hay entrenado
    available_models = [
        "models/yolo11n-seg.pt",
        "models/yolo11s-seg.pt",
        "models/yolo11m-seg.pt"
    ]
    for model in available_models:
        if os.path.exists(model):
            MODEL_PATH = model
            break

print(f"Usando modelo: {MODEL_PATH}")


# Esquemas de respuesta
class DetectionResult(BaseModel):
    """Resultado de una detección individual"""
    class_name: str
    class_id: int
    confidence: float
    risk_level: str
    breeding_site_type: str
    polygon: List[List[float]]
    mask_area: float


class LocationInfo(BaseModel):
    """Información de ubicación GPS"""
    has_location: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude_meters: Optional[float] = None
    location_source: Optional[str] = None


class CameraInfo(BaseModel):
    """Información de la cámara"""
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    camera_datetime: Optional[str] = None
    camera_software: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Respuesta completa del análisis"""
    analysis_id: str
    status: str
    detections: List[DetectionResult]
    total_detections: int
    risk_assessment: Dict[str, Any]
    location: Optional[LocationInfo] = None
    camera_info: Optional[CameraInfo] = None
    processing_time_ms: int
    model_used: str
    confidence_threshold: float


@app.get("/health")
async def health_check():
    """
    Verificación de salud del servicio
    """
    return {
        "status": "healthy",
        "service": "yolo-dengue-detection",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "model_available": os.path.exists(MODEL_PATH),
        "model_path": MODEL_PATH
    }


@app.post("/detect", response_model=AnalysisResponse)
async def detect_dengue_breeding_sites(
    file: UploadFile = File(...),
    confidence_threshold: float = Form(0.5),
    include_gps: bool = Form(True)
):
    """
    Detectar criaderos de dengue en imagen subida

    Args:
        file: Imagen a procesar
        confidence_threshold: Umbral de confianza (0.1-1.0)
        include_gps: Extraer información GPS de EXIF

    Returns:
        AnalysisResponse con detecciones y evaluación de riesgo
    """
    # Validar archivo
    if not file.filename:
        raise HTTPException(status_code=400, detail="No se proporcionó nombre de archivo")

    # Validar extensión usando shared library
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from shared import is_format_supported, SUPPORTED_IMAGE_FORMATS

    file_ext = Path(file.filename).suffix.lower()
    if not is_format_supported(file_ext):
        supported_formats = list(SUPPORTED_IMAGE_FORMATS.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado: {file_ext}. Formatos soportados: {', '.join(supported_formats)}"
        )

    # Validar umbral de confianza
    if not 0.1 <= confidence_threshold <= 1.0:
        raise HTTPException(
            status_code=400,
            detail="confidence_threshold debe estar entre 0.1 y 1.0"
        )

    analysis_id = str(uuid.uuid4())
    start_time = datetime.now()

    try:
        # Guardar archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Process image with automatic conversion if needed
            image_processing_result = process_image_for_detection(
                temp_file_path,
                target_dir=os.path.dirname(temp_file_path)
            )

            if not image_processing_result['success']:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error procesando imagen: {'; '.join(image_processing_result['errors'])}"
                )

            # Use the processed image path for detection
            processed_image_path = image_processing_result['processed_path']

            # Ejecutar detección usando funciones existentes
            detections_raw = detect_breeding_sites(
                model_path=MODEL_PATH,
                source=processed_image_path,
                conf_threshold=confidence_threshold,
                include_gps=include_gps
            )

            # Procesar detecciones al formato de respuesta
            detections = []
            for det in detections_raw:
                class_name = det.get('class', 'unknown')

                detection_result = DetectionResult(
                    class_name=class_name,
                    class_id=det.get('class_id', 0),
                    confidence=det.get('confidence', 0.0),
                    risk_level=det.get('risk_level', 'BAJO'),
                    breeding_site_type=class_name,  # Usar directamente el nombre de clase
                    polygon=det.get('polygon', []),
                    mask_area=det.get('mask_area', 0.0)
                )
                detections.append(detection_result)

            # Evaluación de riesgo usando función existente
            risk_assessment = assess_dengue_risk(detections_raw)

            # Extraer información GPS y de cámara directamente del archivo (no depende de detecciones)
            location_info = None
            camera_info = None

            if include_gps:
                # Extraer GPS directamente del archivo temporal
                from src.utils.gps_metadata import extract_image_gps, get_image_camera_info

                gps_data = extract_image_gps(temp_file_path)
                camera_data = get_image_camera_info(temp_file_path)

                # Procesar datos GPS
                if gps_data and gps_data.get('has_gps'):
                    location_info = LocationInfo(
                        has_location=True,
                        latitude=gps_data.get('latitude'),
                        longitude=gps_data.get('longitude'),
                        altitude_meters=gps_data.get('altitude'),
                        location_source=gps_data.get('location_source', 'EXIF_GPS')
                    )
                else:
                    location_info = LocationInfo(
                        has_location=False,
                        latitude=None,
                        longitude=None,
                        altitude_meters=None,
                        location_source=None
                    )

                # Procesar información de cámara
                if camera_data:
                    camera_info = CameraInfo(
                        camera_make=camera_data.get('camera_make'),
                        camera_model=camera_data.get('camera_model'),
                        camera_datetime=camera_data.get('datetime_original'),
                        camera_software=camera_data.get('software')
                    )

            # Calcular tiempo de procesamiento
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)

            return AnalysisResponse(
                analysis_id=analysis_id,
                status="completed",
                detections=detections,
                total_detections=len(detections),
                risk_assessment=risk_assessment,
                location=location_info,
                camera_info=camera_info,
                processing_time_ms=processing_time,
                model_used=MODEL_PATH,
                confidence_threshold=confidence_threshold
            )

        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        # Limpiar archivo temporal en caso de error
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

        raise HTTPException(
            status_code=500,
            detail=f"Error procesando imagen: {str(e)}"
        )


@app.get("/models")
async def list_available_models():
    """
    Listar modelos disponibles
    """
    models_dir = Path("models")
    available_models = []

    if models_dir.exists():
        for model_file in models_dir.glob("*.pt"):
            available_models.append({
                "name": model_file.name,
                "path": str(model_file),
                "size_mb": round(model_file.stat().st_size / 1024 / 1024, 2),
                "is_current": str(model_file) == MODEL_PATH
            })

    return {
        "available_models": available_models,
        "current_model": MODEL_PATH
    }


if __name__ == "__main__":
    import uvicorn
    import sys
    import os

    # Setup logging
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from shared.logging_utils import setup_yolo_logging, log_system_info, log_model_info

    logger = setup_yolo_logging('INFO')

    # Log system info
    log_system_info(logger, "YOLO Dengue Detection Service", "1.0.0")

    # Log model info
    if os.path.exists(MODEL_PATH):
        model_size_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
        log_model_info(logger, MODEL_PATH, model_size_mb)
    else:
        logger.warning(f"Model not found at: {MODEL_PATH}")

    logger.info("Starting YOLO Dengue Detection server...")
    logger.info("Server will be available at: http://localhost:8002")
    logger.info("API documentation: http://localhost:8002/docs")

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )