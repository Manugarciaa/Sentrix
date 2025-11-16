# Stack Tecnológico - Sentrix Shared Library

Documentación completa de herramientas y tecnologías utilizadas en la librería compartida `sentrix_shared` del proyecto Sentrix.

---

## Descripción

`sentrix_shared` es una librería Python que centraliza código compartido entre Backend y YOLO Service, incluyendo:
- Modelos de datos y enums
- Evaluación de riesgo de dengue
- Utilidades de archivos y GPS
- Deduplicación de imágenes
- Conversión de formatos de imagen

---

## Dependencias Core

### Validación y Schemas
- **Pydantic** `2.11.7` - Validación de datos y schemas
  - Usado para definir modelos de datos tipados
  - Validación automática de entrada/salida
  - Serialización/deserialización JSON

### Configuración
- **PyYAML** `6.0.2` - Parser de archivos YAML
  - Lectura de configuraciones
  - Parsing de archivos de configuración YOLO

---

## Procesamiento de Imágenes

### Librerías de Imagen
- **Pillow** `11.3.0` - Procesamiento y manipulación de imágenes
  - Lectura/escritura de formatos
  - Extracción de metadata EXIF
  - Conversión de formatos
  - Redimensionamiento y transformaciones

- **pillow-heif** `1.1.0` - Soporte para formatos HEIF/HEIC
  - Conversión de HEIC a JPEG
  - Lectura de imágenes de iPhone/dispositivos Apple
  - Preservación de metadata EXIF

- **opencv-python-headless** `4.12.0.88` - Computer vision
  - Procesamiento avanzado de imágenes
  - Detección de características
  - Análisis de similaridad
  - Versión headless (sin GUI) para servidores

---

## Testing

### Framework de Tests
- **pytest** `8.4.1` - Framework de testing
  - Tests unitarios de módulos compartidos
  - Fixtures para datos de prueba
  - Coverage reporting

---

## Módulos y Funcionalidades

### 1. data_models.py

**Propósito:** Enums y constantes compartidas

**Tecnologías:**
- Enum (Python stdlib)
- Typing hints

**Exports:**
```python
DetectionRiskEnum        # ALTO, MEDIO, BAJO, MINIMO
BreedingSiteTypeEnum     # BASURA, CHARCOS, HUECOS, CALLES_MAL_HECHAS
AnalysisStatusEnum       # PENDING, PROCESSING, COMPLETED, FAILED
ValidationStatusEnum     # PENDING_VALIDATION, VALIDATED_POSITIVE, etc.
UserRoleEnum            # USER, ADMIN, EXPERT
LocationSourceEnum      # EXIF_GPS, MANUAL, ESTIMATED
```

**Mapeos:**
- CLASS_ID_TO_BREEDING_SITE - YOLO class ID → Tipo de criadero
- BREEDING_SITE_TO_CLASS_ID - Tipo de criadero → YOLO class ID
- HIGH_RISK_CLASSES - Clases de alto riesgo
- MEDIUM_RISK_CLASSES - Clases de riesgo medio

---

### 2. risk_assessment.py

**Propósito:** Evaluación inteligente de riesgo de dengue

**Tecnologías:**
- Python stdlib
- Algoritmos de scoring

**Funcionalidad:**
```python
assess_dengue_risk(detections) -> dict
```

**Algoritmo de Riesgo:**
- 3+ criaderos alto riesgo → ALTO
- 1 alto riesgo + 3 medio riesgo → ALTO
- 1-2 alto riesgo → MEDIO
- 3+ medio riesgo → MEDIO
- 1-2 medio riesgo → BAJO
- Sin detecciones → MÍNIMO

**Output:**
```python
{
    'overall_risk_level': 'ALTO',
    'risk_distribution': {...},
    'total_detections': 5,
    'high_risk_sites': 2,
    'medium_risk_sites': 3,
    'risk_score': 0.75
}
```

---

### 3. file_utils.py

**Propósito:** Utilidades de archivos y nomenclatura

**Tecnologías:**
- Pillow (metadata EXIF)
- hashlib (hashing)
- pathlib (manejo de rutas)

**Funciones principales:**

**generate_standardized_filename()**
- Nomenclatura estandarizada con metadata
- Formato: `SENTRIX_YYYYMMDD_HHMMSS_CAMERA_GPS_HASH.ext`
- Incluye: timestamp, cámara, GPS, hash único

**validate_image_file()**
- Validación de archivos de imagen
- Verificación de formato soportado
- Validación de tamaño y dimensiones

**get_file_hash()**
- Cálculo de hash SHA256 y MD5
- Firma única de contenido

---

### 4. gps_utils.py

**Propósito:** Extracción de GPS desde metadata EXIF

**Tecnologías:**
- Pillow (EXIF)
- PIL.ExifTags
- Conversión de coordenadas

**Funciones:**

**extract_image_gps()**
- Extrae coordenadas GPS de imagen
- Soporta formato EXIF GPS
- Conversión de grados/minutos/segundos a decimal

**parse_gps_coordinates()**
- Parseo de diferentes formatos GPS
- Normalización de coordenadas

**validate_gps_coordinates()**
- Validación de rangos válidos
- Latitud: -90 a 90
- Longitud: -180 a 180

---

### 5. image_deduplication.py

**Propósito:** Detección de imágenes duplicadas

**Tecnologías:**
- hashlib (SHA256, MD5)
- Pillow (análisis de imagen)
- OpenCV (perceptual hashing)

**Estrategias de Deduplicación:**

1. **Hash de contenido exacto**
   - SHA256 del archivo
   - Detección de duplicados exactos

2. **Metadata matching**
   - GPS coordinates
   - Timestamp de captura
   - Información de cámara

3. **Perceptual hashing** (opcional)
   - pHash usando OpenCV
   - Detección de imágenes similares
   - Tolerancia a compresión/resize

**Funciones:**

**check_image_duplicate()**
```python
{
    'is_duplicate': True/False,
    'duplicate_analysis_id': 'uuid',
    'confidence': 0.85,
    'match_type': 'exact_hash' | 'metadata' | 'perceptual'
}
```

**calculate_content_signature()**
```python
{
    'sha256': 'abc123...',
    'md5': 'def456...',
    'size_bytes': 1024000,
    'phash': 'fe34bc...'  # opcional
}
```

---

### 6. image_formats.py

**Propósito:** Conversión entre formatos de imagen

**Tecnologías:**
- Pillow
- pillow-heif

**Clase principal:**
```python
ImageFormatConverter()
```

**Formatos soportados:**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- HEIC (.heic) - Apple iPhone
- TIFF (.tiff, .tif)
- WebP (.webp)
- BMP (.bmp)

**Funcionalidades:**
- Conversión HEIC → JPEG (principal)
- Preservación de metadata EXIF
- Optimización de calidad
- Redimensionamiento opcional

---

### 7. error_handling.py

**Propósito:** Manejo centralizado de errores

**Tecnologías:**
- Python exceptions
- Custom exception classes

**Excepciones personalizadas:**
- `ImageProcessingError`
- `GPSExtractionError`
- `FileValidationError`
- `DuplicateImageError`

---

### 8. logging_utils.py

**Propósito:** Utilidades de logging compartidas

**Tecnologías:**
- logging (Python stdlib)
- Formatters personalizados

**Funcionalidades:**
- Configuración de loggers
- Formateo consistente
- Niveles de log configurables

---

### 9. config_manager.py

**Propósito:** Gestión de configuración

**Tecnologías:**
- Pydantic Settings
- PyYAML

**Funcionalidades:**
- Carga de configuración desde YAML
- Validación con Pydantic
- Configuración por ambiente

---

### 10. temporal_persistence.py

**Propósito:** Persistencia temporal de datos

**Funcionalidades:**
- Cache temporal
- Almacenamiento en memoria
- TTL (Time To Live)

---

### 11. project_structure.py

**Propósito:** Información de estructura del proyecto

**Funcionalidades:**
- Paths del proyecto
- Convenciones de nomenclatura
- Constantes de proyecto

---

### 12. import_utils.py

**Propósito:** Utilidades de importación

**Funcionalidades:**
- Importación condicional de módulos
- Verificación de dependencias
- Manejo de imports opcionales

---

## Instalación y Distribución

### Configuración del Paquete

**pyproject.toml** (PEP 621)
- Metadata del paquete
- Dependencias
- Versión
- Entry points

**MANIFEST.in**
- Archivos a incluir en distribución
- Exclusión de archivos de desarrollo

### Instalación

**Modo desarrollo (editable):**
```bash
pip install -e /path/to/shared
```

**Ventajas:**
- Cambios reflejados inmediatamente
- No requiere reinstalación
- Ideal para desarrollo

---

## Casos de Uso

### Backend
- Validación de uploads de imágenes
- Deduplicación de análisis
- Evaluación de riesgo
- Generación de nombres estandarizados
- Manejo de estados y roles

### YOLO Service
- Conversión de formatos de imagen (HEIC)
- Extracción de GPS para geolocalización
- Mapeo de class IDs a tipos de criaderos
- Evaluación de riesgo post-detección
- Formateo de resultados

---

## Beneficios de Centralización

### DRY (Don't Repeat Yourself)
- Código compartido una sola vez
- Cambios propagados a ambos servicios
- Menos duplicación

### Consistencia
- Enums compartidos garantizan consistencia
- Misma lógica de evaluación de riesgo
- Nomenclatura estandarizada

### Mantenibilidad
- Actualizar en un solo lugar
- Tests centralizados
- Versionado unificado

### Escalabilidad
- Fácil agregar nuevos servicios
- Reutilización de componentes
- Arquitectura modular

---

## Testing

### Tests Unitarios
```bash
cd shared
python -m pytest tests/ -v
```

### Coverage
```bash
pytest tests/ --cov=sentrix_shared --cov-report=html
```

### Tests de Integración
Verifican que Backend y YOLO Service pueden importar y usar la librería correctamente.

---

## Versión y Compatibilidad

**Versión actual:** 2.7.1
**Python requerido:** 3.8+
**Compatibilidad:** Backend (FastAPI) y YOLO Service (Ultralytics)

---

## Arquitectura de Dependencias

```
Backend (FastAPI)
    ↓
sentrix_shared ←── YOLO Service (Ultralytics)
    ↓
[Pydantic, Pillow, OpenCV, PyYAML]
```

---

**Última actualización:** Noviembre 2025
