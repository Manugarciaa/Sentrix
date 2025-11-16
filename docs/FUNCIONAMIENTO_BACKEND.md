# Como Funciona Backend

Documentacion detallada del funcionamiento interno del API Backend de Sentrix.

---

# BACKEND - API REST y Logica de Negocio

## Descripcion General

El Backend es el orquestador del sistema. Gestiona autenticacion, procesa subidas de imagenes, coordina la deteccion con YOLO Service, almacena resultados en PostgreSQL+PostGIS y gestiona archivos en Supabase Storage.

---

## Flujo Completo de Analisis

### 1. Autenticacion del Usuario

**Endpoint:** `POST /api/v1/auth/login`

**Proceso:**

```python
# 1. Usuario envia credenciales
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

# 2. Backend valida con Supabase Auth
from src.utils.supabase_client import supabase

auth_response = supabase.auth.sign_in_with_password({
    "email": email,
    "password": password
})

# 3. Genera JWT token
access_token = auth_response.session.access_token
refresh_token = auth_response.session.refresh_token

# 4. Response
{
  "access_token": "eyJhbGc...",
  "refresh_token": "v1.MR5m...",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "authenticated"
  }
}
```

**Headers Requeridos:**
```
Authorization: Bearer eyJhbGc...
```

---

### 2. Recepcion de Imagen para Analisis

**Endpoint:** `POST /api/v1/analyses`

**Input:**

```python
# FormData multipart/form-data
{
  "file": <binary image data>,
  "latitude": -34.603722,      # Opcional
  "longitude": -58.381592,     # Opcional
  "location_source": "MANUAL"  # O "EXIF_GPS"
}
```

**Validaciones de Seguridad:**

```python
from src.services.file_validation_service import FileValidationService

# 1. Validacion de MIME type real
mime_type = magic.from_buffer(file_content, mime=True)
ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/heic',
                 'image/tiff', 'image/bmp', 'image/webp']

if mime_type not in ALLOWED_TYPES:
    raise HTTPException(400, "Invalid image type")

# 2. Validacion de tamano
MAX_SIZE = 50 * 1024 * 1024  # 50MB
if len(file_content) > MAX_SIZE:
    raise HTTPException(413, "File too large")

# 3. Sanitizacion de nombre
safe_filename = sanitize_filename(original_filename)

# 4. Validacion de contenido (opcional)
# Intenta abrir la imagen para verificar que no esta corrupta
from PIL import Image
try:
    img = Image.open(BytesIO(file_content))
    img.verify()
except Exception:
    raise HTTPException(400, "Invalid or corrupted image")
```

---

### 3. Conversion HEIC a JPEG

**Proceso (si la imagen es HEIC):**

```python
from pillow_heif import register_heif_opener
from PIL import Image
import io

# 1. Registra soporte HEIC en Pillow
register_heif_opener()

# 2. Detecta si es HEIC
if mime_type == 'image/heic':
    # 3. Convierte a JPEG
    img = Image.open(BytesIO(file_content))

    # Preserva orientacion EXIF
    img = ImageOps.exif_transpose(img)

    # Convierte a RGB (HEIC puede ser RGBA)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Guarda como JPEG
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=95, optimize=True)
    file_content = output.getvalue()

    # Actualiza mime_type
    mime_type = 'image/jpeg'
    original_filename = original_filename.replace('.heic', '.jpg')
```

**Por que es necesario:**
- YOLO Service trabaja mejor con JPEG/PNG
- Supabase Storage tiene mejor soporte para JPEG
- Reduce tamano de archivo (HEIC ~30% mas pesado)
- Garantiza compatibilidad con todos los navegadores

---

### 4. Sistema de Deduplicacion

**Objetivo:** Evitar procesar imagenes duplicadas.

**Proceso:**

```python
from sentrix_shared.deduplication import compute_image_hash

# 1. Calcula hash perceptual de la imagen
image_hash = compute_image_hash(file_content)
# Ejemplo: "a1b2c3d4e5f6g7h8"

# 2. Busca en base de datos
from src.database.models import Analysis

existing_analysis = db.query(Analysis).filter(
    Analysis.user_id == current_user.id,
    Analysis.image_hash == image_hash
).first()

# 3. Si existe duplicado
if existing_analysis:
    # Opcion A: Retorna el analisis existente
    return {
        "status": "duplicate",
        "existing_analysis_id": existing_analysis.id,
        "message": "Image already analyzed",
        "original_analysis": existing_analysis.to_dict()
    }

    # Opcion B: Permite re-analizar (configurable)
    # Util si el modelo fue actualizado
```

**Algoritmo de Hash:**

```python
# Usa imagehash library
import imagehash
from PIL import Image

def compute_image_hash(image_bytes: bytes) -> str:
    img = Image.open(BytesIO(image_bytes))

    # Average hash (rapido, 8x8 grid)
    ahash = imagehash.average_hash(img, hash_size=8)

    # Difference hash (mas preciso)
    dhash = imagehash.dhash(img, hash_size=8)

    # Perceptual hash (muy preciso, mas lento)
    phash = imagehash.phash(img, hash_size=8)

    # Combina los hashes
    combined = f"{ahash}-{dhash}-{phash}"
    return combined
```

**Ventajas:**
- Detecta imagenes identicas (100% match)
- Detecta imagenes casi identicas (95%+ match)
- Funciona incluso si la imagen fue:
  - Redimensionada
  - Comprimida
  - Rotada ligeramente
  - Con filtros aplicados

---

### 5. Generacion de Nombre Estandarizado

**Proceso:**

```python
from sentrix_shared.filename_utils import generate_standardized_filename
from datetime import datetime

# Input
user_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
original_filename = "IMG_20251115_143000.jpg"
analysis_id = "x9y8z7w6-v5u4-3210-tuvw-xyz987654321"

# Generacion
timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
sanitized_name = sanitize_filename(original_filename)
base_name = sanitized_name.rsplit('.', 1)[0][:50]  # Max 50 chars

standardized_filename = f"{timestamp}_{user_id[:8]}_{base_name}.jpg"
# Resultado: "20251115_143000_a1b2c3d4_IMG_20251115_143000.jpg"

# Con analysis_id (para processed image)
processed_filename = f"{timestamp}_{analysis_id[:8]}_processed.jpg"
# Resultado: "20251115_143000_x9y8z7w6_processed.jpg"
```

**Estructura del Nombre:**
```
[timestamp]_[user_id_prefix]_[original_name].[ext]
```

**Ventajas:**
- Nombres unicos (timestamp + UUID)
- Ordenacion cronologica automatica
- Trazabilidad (incluye user_id)
- Sanitizacion contra path traversal
- Prevencion de colisiones

---

### 6. Llamada a YOLO Service

**Cliente HTTP con Circuit Breaker:**

```python
from src.services.yolo_client import YOLOClient
from pybreaker import CircuitBreaker

# 1. Configuracion del Circuit Breaker
yolo_breaker = CircuitBreaker(
    fail_max=5,              # Abre circuito tras 5 fallos
    timeout_duration=60,     # 60s antes de intentar de nuevo
    expected_exception=Exception
)

class YOLOClient:
    def __init__(self):
        self.base_url = "http://yolo-service:8001"
        self.timeout = 30  # 30 segundos

    @yolo_breaker
    async def detect(self, image_bytes: bytes,
                    confidence: float = 0.5) -> dict:
        """
        Envia imagen a YOLO Service para deteccion.
        Circuit Breaker protege contra fallos en cascada.
        """
        # 2. Prepara multipart request
        files = {
            'file': ('image.jpg', image_bytes, 'image/jpeg')
        }
        data = {
            'confidence_threshold': confidence
        }

        # 3. Envia request con timeout
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/detect",
                files=files,
                data=data
            )

        # 4. Manejo de errores
        if response.status_code != 200:
            raise YOLOServiceError(
                f"YOLO Service failed: {response.status_code}"
            )

        # 5. Parsea response
        result = response.json()
        return result
```

**Circuit Breaker States:**

```
Estado: CLOSED (Normal)
- Requests pasan normalmente
- Si 5 fallos consecutivos -> OPEN

Estado: OPEN (Circuito abierto)
- Requests fallan inmediatamente
- No se llama al servicio
- Tras 60s -> HALF_OPEN

Estado: HALF_OPEN (Prueba)
- Permite 1 request de prueba
- Si exito -> CLOSED
- Si falla -> OPEN
```

**Ventajas:**
- Proteccion contra fallos en cascada
- Fast-fail cuando YOLO Service esta caido
- Auto-recuperacion
- Timeouts configurables

---

### 7. Procesamiento de Respuesta YOLO

**Input desde YOLO:**

```python
yolo_response = {
    "detections": [
        {
            "class_name": "Charcos/Cumulo de agua",
            "class_id": 2,
            "confidence": 0.853,
            "bounding_box": {...},
            "polygon": [[x1,y1], [x2,y2], ...],
            "mask_area": 12450.5
        }
    ],
    "risk_assessment": {
        "overall_risk_level": "ALTO",
        "risk_score": 0.75
    },
    "processed_image": {
        "base64": "data:image/jpeg;base64,/9j/4AAQ..."
    },
    "location": {
        "latitude": -34.603722,
        "longitude": -58.381592,
        "source": "EXIF_GPS"
    }
}
```

**Procesamiento en Backend:**

```python
# 1. Extrae imagen procesada
import base64

base64_data = yolo_response['processed_image']['base64']
# Remueve prefix "data:image/jpeg;base64,"
base64_image = base64_data.split(',')[1]
processed_image_bytes = base64.b64decode(base64_image)

# 2. Procesa ubicacion
latitude = yolo_response.get('location', {}).get('latitude')
longitude = yolo_response.get('location', {}).get('longitude')
location_source = yolo_response.get('location', {}).get('source')

# Si usuario proporciono coordenadas manuales, sobrescribe
if manual_latitude and manual_longitude:
    latitude = manual_latitude
    longitude = manual_longitude
    location_source = "MANUAL"

# 3. Crea GeoPoint para PostGIS
from geoalchemy2 import WKTElement

geo_point = None
if latitude and longitude:
    # Formato: POINT(longitude latitude) - OJO: orden inverso!
    geo_point = WKTElement(
        f'POINT({longitude} {latitude})',
        srid=4326  # WGS84
    )
```

---

### 8. Subida Dual a Supabase Storage

**Proceso:**

```python
from src.utils.supabase_client import supabase

# 1. Subida de imagen original
original_path = f"analyses/{user_id}/{standardized_filename}"

original_upload = supabase.storage.from_('sentrix-images').upload(
    path=original_path,
    file=original_image_bytes,
    file_options={
        "content-type": "image/jpeg",
        "cache-control": "3600",
        "upsert": False  # Falla si ya existe
    }
)

# 2. Genera URL publica
original_url = supabase.storage.from_('sentrix-images').get_public_url(
    original_path
)

# 3. Subida de imagen procesada (con detecciones dibujadas)
processed_path = f"analyses/{user_id}/processed/{processed_filename}"

processed_upload = supabase.storage.from_('sentrix-images').upload(
    path=processed_path,
    file=processed_image_bytes,
    file_options={
        "content-type": "image/jpeg",
        "cache-control": "3600",
        "upsert": False
    }
)

# 4. Genera URL publica
processed_url = supabase.storage.from_('sentrix-images').get_public_url(
    processed_path
)
```

**Estructura de Buckets:**

```
sentrix-images/
├── analyses/
│   ├── {user_id}/
│   │   ├── 20251115_143000_a1b2c3d4_IMG.jpg      # Original
│   │   └── processed/
│   │       └── 20251115_143000_x9y8z7w6_processed.jpg  # Procesada
│   ├── {otro_user_id}/
│   │   ├── ...
```

**Politicas RLS (Row Level Security):**

```sql
-- Solo el dueno puede ver sus imagenes
CREATE POLICY "Users can view own images"
ON storage.objects FOR SELECT
USING (
  bucket_id = 'sentrix-images' AND
  (storage.foldername(name))[1] = 'analyses' AND
  (storage.foldername(name))[2] = auth.uid()::text
);

-- Solo el dueno puede subir imagenes
CREATE POLICY "Users can upload own images"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'sentrix-images' AND
  (storage.foldername(name))[1] = 'analyses' AND
  (storage.foldername(name))[2] = auth.uid()::text
);

-- Solo el dueno puede eliminar imagenes
CREATE POLICY "Users can delete own images"
ON storage.objects FOR DELETE
USING (
  bucket_id = 'sentrix-images' AND
  (storage.foldername(name))[1] = 'analyses' AND
  (storage.foldername(name))[2] = auth.uid()::text
);
```

---

### 9. Transaccion de Base de Datos

**Creacion de Registros:**

```python
from src.database.models import Analysis, Detection
from sqlalchemy.orm import Session

async def create_analysis_with_detections(
    db: Session,
    user_id: str,
    yolo_response: dict,
    original_url: str,
    processed_url: str,
    geo_point: WKTElement,
    image_hash: str
) -> Analysis:
    """
    Crea analisis y detecciones en una transaccion atomica.
    """

    try:
        # 1. Crea registro de analisis
        analysis = Analysis(
            id=str(uuid4()),
            user_id=user_id,
            status="completed",

            # Imagenes
            original_image_url=original_url,
            processed_image_url=processed_url,
            image_hash=image_hash,

            # Ubicacion
            latitude=latitude,
            longitude=longitude,
            location=geo_point,  # PostGIS geometry
            location_source=location_source,

            # Evaluacion de riesgo
            overall_risk_level=yolo_response['risk_assessment']['overall_risk_level'],
            risk_score=yolo_response['risk_assessment']['risk_score'],

            # Metadata
            detection_count=len(yolo_response['detections']),
            processing_time_ms=yolo_response.get('processing_time_ms'),
            model_version=yolo_response.get('model_version'),

            # Timestamps
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(analysis)
        db.flush()  # Obtiene analysis.id sin commit

        # 2. Crea detecciones individuales
        for det in yolo_response['detections']:
            detection = Detection(
                id=str(uuid4()),
                analysis_id=analysis.id,

                # Clasificacion
                breeding_site_type=det['class_name'],
                class_id=det['class_id'],
                confidence_score=det['confidence'],
                risk_level=det.get('risk_level', 'MEDIO'),

                # Geometria
                bounding_box=det['bounding_box'],  # JSON
                polygon=det['polygon'],            # JSON
                mask_area_pixels=det['mask_area'],

                # Ubicacion (hereda del analisis)
                latitude=latitude,
                longitude=longitude,
                location=geo_point,

                # Timestamps
                created_at=datetime.utcnow()
            )

            db.add(detection)

        # 3. Commit transaccion
        db.commit()
        db.refresh(analysis)

        return analysis

    except Exception as e:
        # 4. Rollback en caso de error
        db.rollback()

        # 5. Limpia archivos subidos
        try:
            supabase.storage.from_('sentrix-images').remove([
                original_path,
                processed_path
            ])
        except:
            pass  # Log pero no falla

        raise DatabaseError(f"Failed to create analysis: {e}")
```

**Modelos SQLAlchemy:**

```python
from sqlalchemy import Column, String, Float, Integer, DateTime, Enum
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import JSONB

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Imagenes
    original_image_url = Column(String, nullable=False)
    processed_image_url = Column(String)
    image_hash = Column(String, index=True)  # Para deduplicacion

    # Ubicacion (PostGIS)
    latitude = Column(Float)
    longitude = Column(Float)
    location = Column(Geometry('POINT', srid=4326), index=True)
    location_source = Column(Enum('EXIF_GPS', 'MANUAL', 'NONE'))

    # Riesgo
    overall_risk_level = Column(Enum('MINIMO', 'BAJO', 'MEDIO', 'ALTO'))
    risk_score = Column(Float)

    # Metadata
    detection_count = Column(Integer, default=0)
    processing_time_ms = Column(Integer)
    model_version = Column(String)
    status = Column(Enum('pending', 'processing', 'completed', 'failed'))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relaciones
    detections = relationship("Detection", back_populates="analysis",
                            cascade="all, delete-orphan")

class Detection(Base):
    __tablename__ = "detections"

    id = Column(String, primary_key=True)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False, index=True)

    # Clasificacion
    breeding_site_type = Column(String, nullable=False)
    class_id = Column(Integer, nullable=False)
    confidence_score = Column(Float, nullable=False)
    risk_level = Column(Enum('BAJO', 'MEDIO', 'ALTO'))

    # Geometria
    bounding_box = Column(JSONB)  # {x_min, y_min, x_max, y_max}
    polygon = Column(JSONB)       # [[x1,y1], [x2,y2], ...]
    mask_area_pixels = Column(Float)

    # Ubicacion
    latitude = Column(Float)
    longitude = Column(Float)
    location = Column(Geometry('POINT', srid=4326), index=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    analysis = relationship("Analysis", back_populates="detections")
```

**Indices PostGIS:**

```sql
-- Indice espacial para consultas geograficas
CREATE INDEX idx_analyses_location
ON analyses USING GIST (location);

CREATE INDEX idx_detections_location
ON detections USING GIST (location);

-- Permite queries como:
-- "Encuentra todos los analisis en un radio de 5km"
SELECT * FROM analyses
WHERE ST_DWithin(
    location::geography,
    ST_MakePoint(-58.381592, -34.603722)::geography,
    5000  -- metros
);
```

---

### 10. Response Final al Cliente

**Estructura Completa:**

```json
{
  "id": "x9y8z7w6-v5u4-3210-tuvw-xyz987654321",
  "status": "completed",

  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",

  "images": {
    "original": {
      "url": "https://xyz.supabase.co/storage/v1/object/public/sentrix-images/analyses/a1b2c3d4/20251115_143000_a1b2c3d4_IMG.jpg",
      "filename": "20251115_143000_a1b2c3d4_IMG.jpg",
      "size_bytes": 1245678
    },
    "processed": {
      "url": "https://xyz.supabase.co/storage/v1/object/public/sentrix-images/analyses/a1b2c3d4/processed/20251115_143000_x9y8z7w6_processed.jpg",
      "filename": "20251115_143000_x9y8z7w6_processed.jpg",
      "size_bytes": 1456789
    }
  },

  "location": {
    "latitude": -34.603722,
    "longitude": -58.381592,
    "source": "EXIF_GPS",
    "geo_point": "POINT(-58.381592 -34.603722)"
  },

  "risk_assessment": {
    "overall_risk_level": "ALTO",
    "risk_score": 0.75,
    "high_risk_count": 2,
    "medium_risk_count": 1,
    "total_detections": 3
  },

  "detections": [
    {
      "id": "det-001",
      "breeding_site_type": "Charcos/Cumulo de agua",
      "class_id": 2,
      "confidence_score": 0.853,
      "risk_level": "ALTO",

      "bounding_box": {
        "x_min": 100,
        "y_min": 150,
        "x_max": 300,
        "y_max": 400
      },

      "polygon": [[120,160], [280,165], [290,380], [110,390]],
      "mask_area_pixels": 12450.5,

      "location": {
        "latitude": -34.603722,
        "longitude": -58.381592
      }
    }
  ],

  "metadata": {
    "detection_count": 3,
    "processing_time_ms": 847,
    "model_version": "yolo11s-seg-dengue-v2.3",
    "image_hash": "a1b2c3d4e5f6g7h8-d1e2f3g4h5i6j7k8-p1q2r3s4t5u6v7w8"
  },

  "timestamps": {
    "created_at": "2025-11-15T14:30:00Z",
    "updated_at": "2025-11-15T14:30:00Z"
  }
}
```

---

## Caracteristicas Avanzadas

### 1. Row Level Security (RLS)

**Politicas en Supabase:**

```sql
-- Tabla analyses
CREATE POLICY "Users can view own analyses"
ON analyses FOR SELECT
USING (auth.uid()::text = user_id);

CREATE POLICY "Users can create own analyses"
ON analyses FOR INSERT
WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update own analyses"
ON analyses FOR UPDATE
USING (auth.uid()::text = user_id);

CREATE POLICY "Users can delete own analyses"
ON analyses FOR DELETE
USING (auth.uid()::text = user_id);

-- Tabla detections (hereda de analyses)
CREATE POLICY "Users can view detections of own analyses"
ON detections FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM analyses
    WHERE analyses.id = detections.analysis_id
    AND analyses.user_id = auth.uid()::text
  )
);
```

**Ventajas:**
- Seguridad a nivel de base de datos
- No depende de la logica del backend
- Previene data leakage
- Audit trail automatico

---

### 2. Validacion de Imagenes

**Proceso Multi-Capa:**

```python
from src.services.file_validation_service import FileValidationService

class FileValidationService:

    @staticmethod
    def validate_image(file_content: bytes, filename: str) -> dict:
        """
        Validacion comprehensiva de imagenes.
        """

        # 1. Validacion de MIME type REAL
        import magic
        mime_type = magic.from_buffer(file_content, mime=True)

        ALLOWED_TYPES = [
            'image/jpeg', 'image/png', 'image/heic',
            'image/tiff', 'image/bmp', 'image/webp'
        ]

        if mime_type not in ALLOWED_TYPES:
            raise ValidationError(
                f"Invalid MIME type: {mime_type}. "
                f"Allowed: {ALLOWED_TYPES}"
            )

        # 2. Validacion de extension vs MIME
        ext = filename.rsplit('.', 1)[-1].lower()
        expected_exts = {
            'image/jpeg': ['jpg', 'jpeg'],
            'image/png': ['png'],
            'image/heic': ['heic', 'heif'],
            'image/tiff': ['tiff', 'tif'],
            'image/bmp': ['bmp'],
            'image/webp': ['webp']
        }

        if ext not in expected_exts.get(mime_type, []):
            raise ValidationError(
                f"Extension {ext} does not match MIME type {mime_type}"
            )

        # 3. Validacion de tamano
        MAX_SIZE = 50 * 1024 * 1024  # 50MB
        if len(file_content) > MAX_SIZE:
            raise ValidationError(
                f"File too large: {len(file_content)} bytes. "
                f"Max: {MAX_SIZE} bytes"
            )

        # 4. Validacion de contenido (integridad)
        from PIL import Image
        try:
            img = Image.open(BytesIO(file_content))
            img.verify()

            # Re-abre para obtener dimensiones
            img = Image.open(BytesIO(file_content))
            width, height = img.size

        except Exception as e:
            raise ValidationError(f"Corrupted image: {e}")

        # 5. Validacion de dimensiones
        MIN_WIDTH, MIN_HEIGHT = 100, 100
        MAX_WIDTH, MAX_HEIGHT = 10000, 10000

        if width < MIN_WIDTH or height < MIN_HEIGHT:
            raise ValidationError(
                f"Image too small: {width}x{height}. "
                f"Min: {MIN_WIDTH}x{MIN_HEIGHT}"
            )

        if width > MAX_WIDTH or height > MAX_HEIGHT:
            raise ValidationError(
                f"Image too large: {width}x{height}. "
                f"Max: {MAX_WIDTH}x{MAX_HEIGHT}"
            )

        # 6. Validacion contra exploits conocidos
        # Previene ImageTragick, etc.
        if b'<?php' in file_content[:1000]:
            raise ValidationError("Malicious content detected")

        return {
            "valid": True,
            "mime_type": mime_type,
            "size_bytes": len(file_content),
            "dimensions": {"width": width, "height": height}
        }
```

---

### 3. Rate Limiting con Redis

**Configuracion:**

```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis

# 1. Inicializacion en startup
@app.on_event("startup")
async def startup():
    redis_client = await redis.from_url(
        "redis://localhost:6379",
        encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(redis_client)

# 2. Aplicacion por endpoint
@app.post("/api/v1/analyses",
          dependencies=[Depends(RateLimiter(times=10, minutes=1))])
async def create_analysis(...):
    """
    Rate limit: 10 requests por minuto por IP.
    """
    pass

# 3. Rate limit por usuario
from fastapi import Request

async def user_rate_limit_key(request: Request):
    user_id = request.state.user.id  # Del JWT
    return f"user:{user_id}"

@app.post("/api/v1/analyses",
          dependencies=[Depends(
              RateLimiter(times=100, hours=1,
                         identifier=user_rate_limit_key)
          )])
async def create_analysis(...):
    """
    Rate limit: 100 analisis por hora por usuario.
    """
    pass
```

**Limites Configurados:**

```python
RATE_LIMITS = {
    # Autenticacion
    "/api/v1/auth/login": "5/minute",
    "/api/v1/auth/register": "3/minute",

    # Analisis
    "/api/v1/analyses": "10/minute, 100/hour",

    # Consultas
    "/api/v1/analyses/{id}": "100/minute",
    "/api/v1/analyses": "50/minute",  # List

    # Salud
    "/health": "100/minute"
}
```

---

### 4. Cache con Redis

**Estrategia de Cache:**

```python
from src.cache.redis_client import cache_get, cache_set
import json

async def get_analysis_by_id(analysis_id: str, db: Session) -> Analysis:
    """
    Obtiene analisis con cache.
    """

    # 1. Intenta obtener de cache
    cache_key = f"analysis:{analysis_id}"
    cached = await cache_get(cache_key)

    if cached:
        return Analysis(**json.loads(cached))

    # 2. Si no esta en cache, consulta DB
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id
    ).first()

    if not analysis:
        raise HTTPException(404, "Analysis not found")

    # 3. Guarda en cache (TTL 1 hora)
    await cache_set(
        cache_key,
        json.dumps(analysis.to_dict()),
        expire=3600
    )

    return analysis
```

**Invalidacion de Cache:**

```python
async def update_analysis(analysis_id: str, update_data: dict, db: Session):
    """
    Actualiza analisis e invalida cache.
    """

    # 1. Actualiza en DB
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id
    ).first()

    for key, value in update_data.items():
        setattr(analysis, key, value)

    db.commit()

    # 2. Invalida cache
    cache_key = f"analysis:{analysis_id}"
    await cache_delete(cache_key)

    return analysis
```

---

### 5. Generacion de Reportes PDF

**Proceso:**

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Table
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

async def generate_analysis_report(analysis_id: str, db: Session) -> bytes:
    """
    Genera reporte PDF del analisis.
    """

    # 1. Obtiene datos
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id
    ).first()

    detections = db.query(Detection).filter(
        Detection.analysis_id == analysis_id
    ).all()

    # 2. Crea buffer PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # 3. Titulo
    title = Paragraph(
        f"<b>Reporte de Analisis - Sentrix</b><br/>"
        f"ID: {analysis.id}",
        styles['Title']
    )
    story.append(title)

    # 4. Informacion general
    info_data = [
        ["Fecha", analysis.created_at.strftime("%Y-%m-%d %H:%M")],
        ["Nivel de Riesgo", analysis.overall_risk_level],
        ["Puntaje de Riesgo", f"{analysis.risk_score:.2f}"],
        ["Detecciones", str(analysis.detection_count)],
        ["Ubicacion", f"{analysis.latitude}, {analysis.longitude}"]
    ]

    info_table = Table(info_data)
    story.append(info_table)

    # 5. Imagen procesada
    # Descarga de Supabase
    import httpx
    async with httpx.AsyncClient() as client:
        img_response = await client.get(analysis.processed_image_url)
        img_bytes = img_response.content

    img = Image(BytesIO(img_bytes), width=400, height=300)
    story.append(img)

    # 6. Tabla de detecciones
    det_data = [["Tipo", "Confianza", "Riesgo", "Area (px)"]]

    for det in detections:
        det_data.append([
            det.breeding_site_type,
            f"{det.confidence_score:.2f}",
            det.risk_level,
            f"{det.mask_area_pixels:.0f}"
        ])

    det_table = Table(det_data)
    story.append(det_table)

    # 7. Genera PDF
    doc.build(story)

    # 8. Retorna bytes
    buffer.seek(0)
    return buffer.read()

# Endpoint
@app.get("/api/v1/analyses/{analysis_id}/report")
async def download_report(analysis_id: str, db: Session = Depends(get_db)):
    """
    Descarga reporte PDF.
    """
    pdf_bytes = await generate_analysis_report(analysis_id, db)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=analysis_{analysis_id}.pdf"
        }
    )
```

---

## Integracion con Shared Library

### Modulos Compartidos Usados:

**1. sentrix_shared.gps_utils:**
```python
from sentrix_shared.gps_utils import extract_image_gps
```

**2. sentrix_shared.risk_assessment:**
```python
from sentrix_shared.risk_assessment import assess_dengue_risk
```

**3. sentrix_shared.deduplication:**
```python
from sentrix_shared.deduplication import compute_image_hash
```

**4. sentrix_shared.filename_utils:**
```python
from sentrix_shared.filename_utils import generate_standardized_filename
```

**5. sentrix_shared.data_models:**
```python
from sentrix_shared.data_models import DetectionRiskEnum, LocationSourceEnum
```

---

## Referencias

- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLAlchemy ORM: https://docs.sqlalchemy.org/
- PostGIS: https://postgis.net/documentation/
- Supabase Storage: https://supabase.com/docs/guides/storage
- YOLO Service: ../yolo-service/FUNCIONAMIENTO.md
- Frontend: ../frontend/FUNCIONAMIENTO.md
