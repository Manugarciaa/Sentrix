"""
FastAPI Server for YOLO Dengue Detection Service
Servidor FastAPI para el Servicio de Detección de Criaderos de Dengue

SEGURIDAD MEJORADA:
- Rate limiting por IP
- Validación de MIME type real
- Límite de tamaño de archivo
- Sanitización de nombres de archivo
- ThreadPoolExecutor para inferencia asíncrona
- Limpieza automática de archivos temporales
"""

import os
import sys
import tempfile
import uuid
import logging
import base64
import re
import atexit
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

# Load environment variables from project root
from dotenv import load_dotenv, find_dotenv

# Setup basic logging for module initialization
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Silence ultralytics verbose output
logging.getLogger('ultralytics').setLevel(logging.WARNING)

# Find .env in project root (searches up directory tree)
dotenv_path = find_dotenv(usecwd=False)
if dotenv_path:
    load_dotenv(dotenv_path)
    logger.info(f"Loaded environment from: {dotenv_path}")
else:
    # Fallback: try parent directory
    parent_env = Path(__file__).parent.parent / ".env"
    if parent_env.exists():
        load_dotenv(parent_env)
        logger.info(f"Loaded environment from: {parent_env}")
    else:
        logger.warning("No .env file found, using environment variables only")

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Try to import magic, fallback to extension-only validation in development
try:
    import magic
    MAGIC_AVAILABLE = True
except (ImportError, OSError):
    MAGIC_AVAILABLE = False
    import warnings
    warnings.warn("python-magic not available, using extension-only validation (development mode)")

from src.core.detector import detect_breeding_sites
from src.core.evaluator import process_image_for_detection
from src.utils.file_ops import validate_file_exists
from sentrix_shared.risk_assessment import assess_dengue_risk

# ============================================
# CONFIGURACIÓN DE SEGURIDAD
# ============================================

# Tamaño máximo de archivo (50MB)
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))

# Tamaño máximo para encoding base64 (5MB) - evita memory exhaustion
MAX_BASE64_IMAGE_SIZE = int(os.getenv("MAX_BASE64_IMAGE_SIZE", 5 * 1024 * 1024))

# MIME types permitidos
ALLOWED_MIME_TYPES = {
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/tiff',
    'image/x-tiff',
    'image/webp',
    'image/heic',
    'image/heif',
    'image/bmp'
}

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# ThreadPool para inferencia asíncrona (evita bloquear event loop)
executor = ThreadPoolExecutor(
    max_workers=int(os.getenv("YOLO_MAX_WORKERS", 4)),
    thread_name_prefix="yolo_worker"
)

# Tracking de archivos temporales para cleanup
# Using set instead of WeakSet because str objects don't support weak references
temp_files = set()


def cleanup_temp_files():
    """Limpia archivos temporales al cerrar el servicio"""
    logger.info("Cleaning up temporary files...")
    for file_path in temp_files:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.warning(f"Failed to cleanup {file_path}: {e}")


# Register cleanup on exit
atexit.register(cleanup_temp_files)


# ============================================
# LIFESPAN CONTEXT MANAGER
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting YOLO Dengue Detection Service...")
    logger.info(f"Max file size: {MAX_FILE_SIZE / (1024*1024):.1f}MB")
    logger.info(f"Max workers: {executor._max_workers}")
    logger.info(f"Model path: {MODEL_PATH}")

    yield

    # Shutdown
    logger.info("Shutting down YOLO service...")
    executor.shutdown(wait=True, cancel_futures=True)
    cleanup_temp_files()


# ============================================
# APP INITIALIZATION
# ============================================

app = FastAPI(
    title="YOLO Dengue Detection Service",
    description="Servicio de detección de criaderos de dengue usando YOLO con seguridad mejorada",
    version="2.0.0",
    lifespan=lifespan
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - Configuración segura
allowed_origins = [
    "http://localhost:8000",  # Backend service
    "http://localhost:3000",  # Frontend development
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
]

# Add production origins from environment if available
if production_origins := os.getenv("ALLOWED_ORIGINS"):
    # Validar que sean URLs válidas
    for origin in production_origins.split(","):
        origin = origin.strip()
        if origin and (origin.startswith("http://") or origin.startswith("https://")):
            allowed_origins.append(origin)
        else:
            logger.warning(f"Invalid origin ignored: {origin}")

# Ensure no wildcards in production
if os.getenv("ENVIRONMENT") == "production" and "*" in allowed_origins:
    logger.error("SECURITY: Wildcard CORS not allowed in production!")
    allowed_origins.remove("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


# ============================================
# MODELO YOLO
# ============================================

def find_latest_trained_model():
    """
    Busca el modelo entrenado más reciente y lo copia a models/best.pt

    Prioridad:
    1. Variable de entorno YOLO_MODEL_PATH (validada)
    2. Último modelo en carpetas de entrenamiento (dengue_seg_*/weights/best.pt)
    3. models/best.pt (modelo entrenado manual)
    4. Modelos base (yolo11*-seg.pt)
    """
    import shutil

    # 1. Variable de entorno (máxima prioridad)
    env_model = os.getenv("YOLO_MODEL_PATH")
    if env_model:
        # SEGURIDAD: Validar que el path es seguro (no contiene ..)
        env_model_path = Path(env_model).resolve()
        base_dir = Path(__file__).parent.resolve()

        try:
            # Verificar que el modelo esté dentro del directorio permitido
            env_model_path.relative_to(base_dir)
            if env_model_path.exists() and env_model_path.suffix == '.pt':
                logger.info(f"Using model from environment: {env_model_path}")
                return str(env_model_path)
            else:
                logger.warning(f"Model from environment not found or invalid: {env_model}")
        except ValueError:
            logger.error(f"SECURITY: Model path outside allowed directory: {env_model}")

    # 2. Buscar en carpetas de entrenamiento (dengue_seg_*)
    models_dir = Path("models")
    best_pt_path = models_dir / "best.pt"
    training_folders = sorted(models_dir.glob("dengue_seg_*"), key=os.path.getmtime, reverse=True)

    for folder in training_folders:
        trained_model = folder / "weights" / "best.pt"
        if trained_model.exists():
            # Copiar el modelo entrenado más reciente a models/best.pt
            try:
                shutil.copy2(trained_model, best_pt_path)
                logger.info(f"Modelo actualizado: {trained_model} -> {best_pt_path}")
                return str(best_pt_path)
            except Exception as e:
                logger.warning(f"No se pudo copiar modelo: {e}")
                return str(trained_model)

    # 3. Modelo entrenado en raíz de models/
    if best_pt_path.exists():
        return str(best_pt_path)

    # 4. Fallback a modelos base
    available_models = [
        "models/yolo11n-seg.pt",
        "models/yolo11s-seg.pt",
        "models/yolo11m-seg.pt"
    ]
    for model in available_models:
        if os.path.exists(model):
            logger.warning(f"Usando modelo base (no entrenado): {model}")
            return model

    raise FileNotFoundError("No se encontró ningún modelo YOLO disponible")


MODEL_PATH = find_latest_trained_model()
logger.info(f"Usando modelo: {MODEL_PATH}")


# ============================================
# FUNCIONES DE VALIDACIÓN
# ============================================

def sanitize_filename(filename: str) -> str:
    """
    Sanitiza nombre de archivo para prevenir path traversal

    Args:
        filename: Nombre de archivo original

    Returns:
        Nombre de archivo sanitizado
    """
    # Remover path separators y caracteres peligrosos
    safe_name = os.path.basename(filename)
    # Permitir solo caracteres alfanuméricos, guiones, underscores y punto
    safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', safe_name)
    return safe_name


async def validate_file_content(file: UploadFile, max_size: int) -> bytes:
    """
    Valida contenido de archivo subido

    Args:
        file: Archivo subido
        max_size: Tamaño máximo permitido en bytes

    Returns:
        Contenido del archivo en bytes

    Raises:
        HTTPException: Si el archivo es inválido
    """
    # 1. VALIDAR TAMAÑO
    content = await file.read(max_size + 1)  # Leer 1 byte extra para detectar si es muy grande

    if len(content) > max_size:
        max_mb = max_size / (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {max_mb:.1f}MB"
        )

    # 2. VALIDAR MIME TYPE REAL (magic bytes)
    if MAGIC_AVAILABLE:
        try:
            mime_type = magic.from_buffer(content, mime=True)
            logger.debug(f"Detected MIME type: {mime_type}")

            if mime_type not in ALLOWED_MIME_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type: {mime_type}. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}"
                )
        except Exception as e:
            logger.error(f"MIME type detection failed: {e}")
            raise HTTPException(
                status_code=400,
                detail="Could not determine file type"
            )
    else:
        logger.debug("MIME validation disabled (magic not available)")

    return content


def create_safe_temp_file(content: bytes, file_ext: str) -> str:
    """
    Crea archivo temporal de forma segura

    Args:
        content: Contenido del archivo
        file_ext: Extensión del archivo

    Returns:
        Path del archivo temporal creado
    """
    # Crear archivo temporal con permisos restrictivos
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext, mode='wb') as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name

    # Registrar para cleanup automático
    temp_files.add(temp_file_path)

    return temp_file_path


# ============================================
# ESQUEMAS DE RESPUESTA
# ============================================

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
    processed_image_base64: Optional[str] = None


# ============================================
# ENDPOINTS
# ============================================

@app.get("/health")
async def health_check():
    """
    Health check mejorado - verifica componentes críticos
    """
    import torch
    import psutil

    # Verificar modelo existe
    model_exists = os.path.exists(MODEL_PATH)

    # Verificar memoria disponible
    memory = psutil.virtual_memory()
    memory_available_mb = memory.available / (1024 * 1024)

    # Verificar GPU si está disponible
    gpu_available = torch.cuda.is_available()
    gpu_info = None
    if gpu_available:
        gpu_info = {
            "name": torch.cuda.get_device_name(0),
            "memory_allocated_mb": torch.cuda.memory_allocated(0) / (1024 * 1024),
            "memory_reserved_mb": torch.cuda.memory_reserved(0) / (1024 * 1024)
        }

    # Estado general
    healthy = model_exists and memory_available_mb > 100

    return {
        "status": "healthy" if healthy else "degraded",
        "service": "yolo-dengue-detection",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "model_available": model_exists,
            "model_path": MODEL_PATH if model_exists else None,
            "memory_available_mb": round(memory_available_mb, 2),
            "gpu_available": gpu_available,
            "gpu_info": gpu_info,
            "workers_active": executor._threads is not None
        }
    }


@app.post("/detect", response_model=AnalysisResponse)
@limiter.limit("10/minute")  # Rate limiting: 10 requests por minuto por IP
async def detect_dengue_breeding_sites(
    request: Request,  # Requerido por slowapi
    file: UploadFile = File(...),
    confidence_threshold: float = Form(0.5),
    include_gps: bool = Form(True)
):
    """
    Detectar criaderos de dengue en imagen subida

    SEGURIDAD:
    - Rate limiting: 10 req/min por IP
    - Max file size: 50MB
    - MIME type validation
    - Sanitized filenames
    - Async inference con ThreadPoolExecutor

    Args:
        request: FastAPI request (para rate limiting)
        file: Imagen a procesar
        confidence_threshold: Umbral de confianza (0.1-1.0)
        include_gps: Extraer información GPS de EXIF

    Returns:
        AnalysisResponse con detecciones y evaluación de riesgo
    """
    # Validar nombre de archivo existe
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Sanitizar nombre de archivo
    safe_filename = sanitize_filename(file.filename)
    logger.info(f"Processing: {safe_filename}, include_gps={include_gps} (type: {type(include_gps).__name__})")

    # Validar extensión usando shared library
    from sentrix_shared import is_format_supported, SUPPORTED_IMAGE_FORMATS

    file_ext = Path(safe_filename).suffix.lower()
    if not is_format_supported(file_ext):
        supported_formats = list(SUPPORTED_IMAGE_FORMATS.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {file_ext}. Supported: {', '.join(supported_formats)}"
        )

    # Validar umbral de confianza
    if not 0.1 <= confidence_threshold <= 1.0:
        raise HTTPException(
            status_code=400,
            detail="confidence_threshold must be between 0.1 and 1.0"
        )

    analysis_id = str(uuid.uuid4())
    start_time = datetime.now()
    temp_file_path = None
    processed_image_path = None

    try:
        # VALIDAR CONTENIDO DEL ARCHIVO (tamaño y MIME type)
        content = await validate_file_content(file, MAX_FILE_SIZE)

        # Crear archivo temporal de forma segura
        temp_file_path = create_safe_temp_file(content, file_ext)
        logger.debug(f"Created temp file: {temp_file_path}")

        # Process image with automatic conversion if needed
        image_processing_result = process_image_for_detection(
            temp_file_path,
            target_dir=os.path.dirname(temp_file_path)
        )

        if not image_processing_result['success']:
            raise HTTPException(
                status_code=400,
                detail=f"Image processing failed: {'; '.join(image_processing_result['errors'])}"
            )

        # Use the processed image path for detection
        processed_image_path = image_processing_result['processed_path']

        # EJECUTAR DETECCIÓN EN THREADPOOL (evita bloquear event loop)
        import asyncio
        loop = asyncio.get_event_loop()

        detection_result = await loop.run_in_executor(
            executor,
            detect_breeding_sites,
            MODEL_PATH,
            processed_image_path,
            confidence_threshold,
            include_gps,
            True,  # save_processed_image
            None   # output_dir (usar default)
        )

        # Extraer detecciones del resultado
        detections_raw = detection_result.get('detections', [])
        processed_image_saved = detection_result.get('processed_image_path')

        # Procesar detecciones al formato de respuesta
        detections = []
        for det in detections_raw:
            class_name = det.get('class', 'unknown')

            detection_result_obj = DetectionResult(
                class_name=class_name,
                class_id=det.get('class_id', 0),
                confidence=det.get('confidence', 0.0),
                risk_level=det.get('risk_level', 'BAJO'),
                breeding_site_type=class_name,
                polygon=det.get('polygon', []),
                mask_area=det.get('mask_area', 0.0)
            )
            detections.append(detection_result_obj)

        # Evaluación de riesgo usando función existente de shared library
        risk_assessment = assess_dengue_risk(detections_raw)

        # Extraer información GPS y de cámara directamente del archivo
        location_info = None
        camera_info = None

        if include_gps:
            from src.utils.gps_metadata import extract_image_gps, get_image_camera_info

            logger.info(f"[GPS DEBUG] Extracting GPS from: {temp_file_path}")
            gps_data = extract_image_gps(temp_file_path)
            logger.info(f"[GPS DEBUG] GPS data extracted: {gps_data}")

            camera_data = get_image_camera_info(temp_file_path)

            # Procesar datos GPS
            if gps_data and gps_data.get('has_gps'):
                logger.info(f"[GPS DEBUG] GPS FOUND - Lat: {gps_data.get('latitude')}, Lng: {gps_data.get('longitude')}")
                location_info = LocationInfo(
                    has_location=True,
                    latitude=gps_data.get('latitude'),
                    longitude=gps_data.get('longitude'),
                    altitude_meters=gps_data.get('altitude'),
                    location_source=gps_data.get('location_source', 'EXIF_GPS')
                )
            else:
                logger.info(f"[GPS DEBUG] No GPS found in image")
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

        # Leer imagen procesada como base64 si existe y no es muy grande
        processed_image_base64 = None
        if processed_image_saved and os.path.exists(processed_image_saved):
            try:
                file_size = os.path.getsize(processed_image_saved)

                # SEGURIDAD: No encodear imágenes muy grandes (evita memory exhaustion)
                if file_size <= MAX_BASE64_IMAGE_SIZE:
                    with open(processed_image_saved, 'rb') as f:
                        processed_image_bytes = f.read()
                        processed_image_base64 = base64.b64encode(processed_image_bytes).decode('utf-8')
                    logger.info(f"Processed image encoded to base64, size: {len(processed_image_base64)} chars")
                else:
                    # If image is too large, compress it before encoding
                    logger.warning(
                        f"Processed image too large for base64 ({file_size / (1024*1024):.1f}MB > "
                        f"{MAX_BASE64_IMAGE_SIZE / (1024*1024):.1f}MB), compressing..."
                    )
                    try:
                        from PIL import Image
                        import io

                        # Load image and compress
                        img = Image.open(processed_image_saved)
                        buffer = io.BytesIO()

                        # Start with quality 85, reduce if still too large
                        quality = 85
                        while quality >= 30:
                            buffer.seek(0)
                            buffer.truncate()
                            img.save(buffer, format='JPEG', quality=quality, optimize=True)
                            compressed_size = buffer.tell()

                            if compressed_size <= MAX_BASE64_IMAGE_SIZE:
                                buffer.seek(0)
                                processed_image_bytes = buffer.read()
                                processed_image_base64 = base64.b64encode(processed_image_bytes).decode('utf-8')
                                logger.info(
                                    f"Compressed image to {compressed_size / (1024*1024):.1f}MB "
                                    f"with quality {quality}"
                                )
                                break
                            quality -= 10

                        if not processed_image_base64:
                            logger.warning("Could not compress image enough, skipping encoding")
                    except Exception as compress_error:
                        logger.warning(f"Failed to compress image: {compress_error}")
            except Exception as e:
                logger.warning(f"Failed to encode processed image: {e}")

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
            confidence_threshold=confidence_threshold,
            processed_image_base64=processed_image_base64
        )

    except HTTPException:
        # Re-raise HTTP exceptions (ya tienen el código de status correcto)
        raise

    except Exception as e:
        logger.exception(f"Unexpected error processing image: {e}")

        # En producción, no exponer detalles internos
        if os.getenv("ENVIRONMENT") == "production":
            raise HTTPException(
                status_code=500,
                detail="Internal server error processing image"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing image: {str(e)}"
            )

    finally:
        # Cleanup de archivos temporales
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                temp_files.discard(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {temp_file_path}: {e}")

        if processed_image_path and os.path.exists(processed_image_path):
            try:
                os.unlink(processed_image_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup processed file {processed_image_path}: {e}")


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


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    import uvicorn

    # Setup logging
    from sentrix_shared.logging_utils import setup_yolo_logging, log_system_info, log_model_info

    logger = setup_yolo_logging('INFO')

    # Log system info
    log_system_info(logger, "YOLO Dengue Detection Service", "2.0.0")

    # Log model info
    if os.path.exists(MODEL_PATH):
        model_size_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
        log_model_info(logger, MODEL_PATH, model_size_mb)
    else:
        logger.warning(f"Model not found at: {MODEL_PATH}")

    # Get port from environment variable
    port = int(os.getenv("YOLO_SERVICE_PORT", "8001"))

    logger.info("Starting YOLO Dengue Detection server...")
    logger.info(f"Server will be available at: http://localhost:{port}")
    logger.info(f"API documentation: http://localhost:{port}/docs")
    logger.info(f"Max file size: {MAX_FILE_SIZE / (1024*1024):.1f}MB")
    logger.info(f"Rate limit: 10 requests/minute per IP")

    # Disable reload in production (Render can't detect port with reloader)
    is_production = os.getenv("ENVIRONMENT", "development") == "production"

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=not is_production,  # Only reload in development
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
