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

from src.core import detect_breeding_sites, assess_dengue_risk
from src.utils import validate_file_exists

app = FastAPI(
    title="YOLO Dengue Detection Service",
    description="Servicio de detección de criaderos de dengue usando YOLO",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

    # Validar extensión
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Extensión no permitida. Use: {', '.join(allowed_extensions)}"
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
            # Ejecutar detección usando funciones existentes
            detections_raw = detect_breeding_sites(
                model_path=MODEL_PATH,
                source=temp_file_path,
                conf_threshold=confidence_threshold,
                include_gps=include_gps
            )

            # Procesar detecciones al formato de respuesta
            detections = []
            for det in detections_raw:
                detection_result = DetectionResult(
                    class_name=det.get('class', 'unknown'),
                    class_id=det.get('class_id', 0),
                    confidence=det.get('confidence', 0.0),
                    risk_level=det.get('risk_level', 'BAJO'),
                    breeding_site_type=det.get('class', 'unknown'),
                    polygon=det.get('polygon', []),
                    mask_area=det.get('mask_area', 0.0)
                )
                detections.append(detection_result)

            # Evaluación de riesgo usando función existente
            risk_assessment = assess_dengue_risk(detections_raw)

            # Extraer información de ubicación del primer resultado (si existe)
            location_info = None
            camera_info = None

            if detections_raw and include_gps:
                first_detection = detections_raw[0]
                location_data = first_detection.get('location', {})

                if location_data and location_data.get('has_location'):
                    location_info = LocationInfo(
                        has_location=True,
                        latitude=location_data.get('latitude'),
                        longitude=location_data.get('longitude'),
                        altitude_meters=location_data.get('altitude_meters'),
                        location_source=location_data.get('location_source', 'EXIF_GPS')
                    )

                image_metadata = first_detection.get('image_metadata', {})
                camera_data = image_metadata.get('camera_info', {})
                if camera_data:
                    camera_info = CameraInfo(
                        camera_make=camera_data.get('make'),
                        camera_model=camera_data.get('model'),
                        camera_datetime=camera_data.get('datetime'),
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

    print("Iniciando servidor YOLO Dengue Detection...")
    print(f"Modelo: {MODEL_PATH}")
    print("Servidor disponible en: http://localhost:8001")
    print("Documentación: http://localhost:8001/docs")

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )