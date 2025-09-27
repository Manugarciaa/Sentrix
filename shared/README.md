# Sentrix Shared Library - Librería Compartida

Librería compartida de Sentrix que contiene toda la funcionalidad común utilizada por los servicios backend y yolo-service. Garantiza consistencia, reduce duplicación y facilita el mantenimiento.

## Descripción

Esta librería centraliza componentes críticos para asegurar consistencia entre servicios:

- **Enums unificados** - Tipos de riesgo, criaderos, estados y roles
- **Evaluación de riesgo** - Algoritmos epidemiológicos compartidos
- **Utilidades de archivos avanzadas** - Validación, procesamiento y nomenclatura estandarizada
- **Sistema de deduplicación** - Detección inteligente de contenido duplicado
- **Nomenclatura profesional** - Sistema estandarizado para archivos de análisis
- **Manejo de errores** - Clases de excepción estandarizadas
- **Logging centralizado** - Sistema de logs unificado
- **Configuración** - Gestión de configuración centralizada

## Estructura del Proyecto

```
shared/
├── data_models.py         # Enums y modelos de datos principales
├── risk_assessment.py     # Algoritmos de evaluación de riesgo
├── file_utils.py         # Utilidades avanzadas + nomenclatura estandarizada
├── image_deduplication.py # Sistema de deduplicación inteligente
├── image_formats.py      # Soporte de formatos de imagen
├── gps_utils.py          # Extracción de metadatos GPS
├── logging_utils.py      # Sistema de logging unificado
├── error_handling.py     # Manejo de errores estandarizado
├── config_manager.py     # Gestión de configuración
├── import_utils.py       # Utilidades de importación
└── tests/                # Tests de la librería compartida
```

## Componentes Principales

### 1. Enums Unificados (`data_models.py`)

Definiciones centralizadas de tipos de datos:

```python
from shared.data_models import (
    # Tipos de riesgo
    DetectionRiskEnum,        # ALTO, MEDIO, BAJO, MINIMO
    RiskLevelEnum,           # Compatibilidad general

    # Tipos de criaderos
    BreedingSiteTypeEnum,    # BASURA, CALLES_MAL_HECHAS, etc.

    # Estados del sistema
    AnalysisStatusEnum,      # PENDING, PROCESSING, COMPLETED, FAILED
    ValidationStatusEnum,    # PENDING, VALIDATED_POSITIVE, etc.

    # Usuarios y ubicación
    UserRoleEnum,           # USER, ADMIN, EXPERT
    LocationSourceEnum      # EXIF_GPS, MANUAL, ESTIMATED
)
```

### 2. Evaluación de Riesgo (`risk_assessment.py`)

Algoritmo epidemiológico unificado:

```python
from shared.risk_assessment import assess_dengue_risk

# Evaluar riesgo de detecciones
detections = [
    {"class": "Charcos/Cumulo de agua", "confidence": 0.85},
    {"class": "Basura", "confidence": 0.75}
]

risk_result = assess_dengue_risk(detections)
# Retorna: overall_risk_level, risk_distribution, total_detections
```

### 3. Utilidades de Archivos Avanzadas (`file_utils.py`)

Validación, procesamiento y nomenclatura estandarizada:

```python
from shared.file_utils import (
    validate_image_file,
    process_image_for_detection,
    get_file_metadata,
    # Nuevas funcionalidades
    generate_standardized_filename,
    create_filename_variations,
    parse_standardized_filename
)

# Validar formato de imagen
is_valid = validate_image_file("imagen.jpg")

# Generar nombre estandarizado
standardized = generate_standardized_filename(
    original_filename="IMG_1234.jpg",
    camera_info={"camera_make": "Apple", "camera_model": "iPhone 15"},
    gps_data={"has_gps": True, "latitude": -34.603722, "longitude": -58.381592},
    analysis_timestamp=datetime.now()
)
# Resultado: SENTRIX_20250926_143052_IPHONE15_LATn34p604_LONn58p382_a1b2c3d4.jpg

# Crear variaciones de nombres
variations = create_filename_variations(
    base_filename="IMG_1234.jpg",
    camera_info=camera_info,
    gps_data=gps_data
)
# Resultado: {
#   'original': 'IMG_1234.jpg',
#   'standardized': 'SENTRIX_...',
#   'processed': 'SENTRIX_PROC_...',
#   'thumbnail': 'SENTRIX_..._thumb.jpg'
# }
```

### 3.1. Sistema de Deduplicación (`image_deduplication.py`)

Detección inteligente de contenido duplicado:

```python
from shared.image_deduplication import (
    check_image_duplicate,
    calculate_content_signature,
    get_deduplication_manager,
    estimate_storage_savings
)

# Calcular firma de contenido
signature = calculate_content_signature(image_data)
# Resultado: {'sha256': 'abc123...', 'md5': 'def456...', 'size_bytes': 1024000}

# Verificar duplicados
duplicate_check = check_image_duplicate(
    image_data=image_data,
    existing_analyses=[...],
    camera_info={"camera_make": "Apple"},
    gps_data={"latitude": -34.603722, "longitude": -58.381592}
)

# Resultado de verificación:
# {
#   'is_duplicate': True/False,
#   'duplicate_analysis_id': 'existing-id',
#   'should_store_separately': False,
#   'confidence': 0.85
# }

# Estimar ahorro de storage
savings = estimate_storage_savings(duplicate_analyses)
# Resultado: {
#   'total_analyses': 100,
#   'duplicate_references': 25,
#   'storage_saved_mb': 125.5,
#   'deduplication_rate': 25.0
# }
```

### 4. Formatos de Imagen (`image_formats.py`)

Soporte completo de formatos:

```python
from shared.image_formats import (
    ImageFormatConverter,
    is_format_supported,
    SUPPORTED_IMAGE_FORMATS
)

# Verificar soporte
if is_format_supported('.heic'):
    converter = ImageFormatConverter()
    result = converter.convert_heic_to_jpeg("photo.heic", "photo.jpg")
```

### 5. Logging Unificado (`logging_utils.py`)

Sistema de logs centralizado:

```python
from shared.logging_utils import (
    setup_backend_logging,
    setup_yolo_logging,
    log_detection_result
)

# Configurar logging para backend
logger = setup_backend_logging('INFO')

# Log específico de detección
log_detection_result(logger, analysis_id, detections, processing_time)
```

### 6. Manejo de Errores (`error_handling.py`)

Excepciones estandarizadas:

```python
from shared.error_handling import (
    ValidationError,
    ProcessingError,
    FileNotFoundError,
    ModelLoadError
)

try:
    result = process_image(image_path)
except ValidationError as e:
    logger.error(f"Error de validación: {e}")
```

## Convenciones de Importación

### ✅ Patrón Correcto

```python
# Importación directa desde shared
from shared.data_models import DetectionRiskEnum, BreedingSiteTypeEnum
from shared.risk_assessment import assess_dengue_risk
from shared.logging_utils import setup_backend_logging
```

### ❌ Patrones Obsoletos

```python
# EVITAR - Re-exportaciones locales
from app.models.enums import DetectionRiskEnum

# EVITAR - Importaciones indirectas
from src.database.models.enums import *
```

## Uso por Servicio

### Backend

```python
# Esquemas y validación
from shared.data_models import ValidationStatusEnum, UserRoleEnum
from shared.file_utils import validate_image_file

# Sistema de nomenclatura estandarizada
from shared.file_utils import (
    generate_standardized_filename,
    create_filename_variations,
    parse_standardized_filename
)

# Sistema de deduplicación
from shared.image_deduplication import (
    check_image_duplicate,
    calculate_content_signature,
    get_deduplication_manager,
    estimate_storage_savings
)

# API y servicios
from shared.risk_assessment import assess_dengue_risk
from shared.logging_utils import setup_backend_logging
```

### YOLO-Service

```python
# Detección y evaluación
from shared.data_models import DetectionRiskEnum, CLASS_ID_TO_BREEDING_SITE
from shared.risk_assessment import assess_dengue_risk

# Procesamiento de imágenes
from shared.image_formats import ImageFormatConverter
from shared.gps_utils import extract_image_gps

# Nomenclatura para imágenes procesadas
from shared.file_utils import generate_standardized_filename
```

## Mapeos y Constantes

### Mapeo YOLO a Enums

```python
from shared.data_models import (
    CLASS_ID_TO_BREEDING_SITE,     # {0: BASURA, 1: CALLES_MAL_HECHAS, ...}
    BREEDING_SITE_TO_CLASS_ID,     # Mapeo inverso
    YOLO_RISK_TO_DETECTION_RISK    # {"ALTO": DetectionRiskEnum.ALTO, ...}
)
```

### Clasificaciones de Riesgo

```python
from shared.data_models import (
    HIGH_RISK_CLASSES,     # Criaderos de alto riesgo
    MEDIUM_RISK_CLASSES,   # Criaderos de riesgo medio
    LOW_RISK_CLASSES       # Criaderos de bajo riesgo
)
```

## Configuración

### Gestión Centralizada

```python
from shared.config_manager import (
    YoloServiceConfig,
    DatabaseConfig,
    ConfigManager
)

# Configuración del servicio YOLO
yolo_config = YoloServiceConfig()
print(yolo_config.url)  # http://localhost:8001
```

### Variables de Entorno

La librería respeta las siguientes variables de entorno:

```bash
# Configuración de servicios
YOLO_SERVICE_URL=http://localhost:8001
DATABASE_URL=postgresql://...

# Logging
LOG_LEVEL=INFO
LOG_FILE_SHARED=./logs/shared.log

# Procesamiento
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=.jpg,.jpeg,.png,.heic
```

## Formatos de Imagen Soportados

| Formato | Extensión | Conversión | Metadatos GPS |
|---------|-----------|------------|---------------|
| JPEG    | .jpg, .jpeg | Nativo | ✅ |
| PNG     | .png | Nativo | ✅ |
| HEIC    | .heic, .heif | Auto → JPEG | ✅ |
| TIFF    | .tiff, .tif | Nativo | ✅ |
| WebP    | .webp | Nativo | ✅ |
| BMP     | .bmp | Nativo | ❌ |

## Testing

### Ejecutar Tests

```bash
# Tests específicos de shared
cd shared && python -m pytest tests/ -v

# Test de importación básica
python -c "from shared.data_models import DetectionRiskEnum; print('OK')"

# Validación completa del sistema
cd .. && python scripts/simple-validation.py
```

### Tests Incluidos

- `test_image_formats.py` - Conversión y validación de formatos
- `test_standardized_naming.py` - Sistema de nomenclatura estandarizada
- `test_deduplication.py` - Sistema de deduplicación inteligente
- Tests de enums y consistencia de datos
- Tests de evaluación de riesgo
- Tests de utilidades de archivos avanzadas

## Desarrollo

### Agregar Nuevos Componentes

1. **Crear módulo** en `shared/nuevo_modulo.py`
2. **Agregar exports** en `shared/__init__.py`
3. **Documentar** en este README
4. **Crear tests** en `shared/tests/`
5. **Actualizar** servicios que lo usen

### Principios de Diseño

- **Stateless** - Sin estado global
- **Portabilidad** - Funciona en todos los entornos
- **Consistencia** - Misma interfaz para todos los servicios
- **Documentación** - Docstrings completos
- **Testing** - Cobertura completa

## Compatibilidad

### Retrocompatibilidad

- `ValidationStatusEnum.PENDING` - Mantiene compatibilidad con código legacy
- Aliases para enums renombrados
- Importaciones opcionales para dependencias

### Versiones Python

- **Mínima**: Python 3.8+
- **Recomendada**: Python 3.9+
- **Testada**: 3.8, 3.9, 3.10, 3.11

## Documentación Adicional

- [Scripts de Utilidad](../scripts/README.md)
- [Convenciones de Imports](IMPORT_CONVENTIONS.md)
- [Backend README](../backend/README.md)
- [YOLO Service README](../yolo-service/README.md)

---

## Actualizaciones Recientes (v2.0.0)

### Nuevas Funcionalidades Implementadas:
- **Sistema de Nomenclatura Estandarizada**: Generación automática de nombres profesionales
- **Deduplicación Inteligente**: Detección de contenido duplicado con scoring de similitud
- **Gestión Avanzada de Archivos**: Variaciones de nombres y parsing de metadatos
- **Optimización de Storage**: Cálculo automático de ahorros por deduplicación

### Componentes Agregados:
- **`image_deduplication.py`**: Sistema completo de deduplicación
- **`file_utils.py` mejorado**: Funciones de nomenclatura estandarizada
- **Nuevos tests**: Cobertura completa para funcionalidades avanzadas
- **Documentación extendida**: Ejemplos detallados de uso

### Estado de Integración Verificado:
- **Backend**: Usando nomenclatura y deduplicación sin errores
- **YOLO Service**: Generación de nombres estandarizados
- **Frontend**: Interfaces actualizadas para nuevas funcionalidades
- **Tests**: Suite completa funcionando correctamente

### Funcionalidades Avanzadas:
- **Nomenclatura Profesional**: Formato SENTRIX_YYYYMMDD_HHMMSS_DEVICE_LOCATION_ID
- **Deduplicación por Contenido**: Hash SHA-256 y scoring de metadatos
- **Variaciones de Archivos**: Original, procesado, thumbnail con nomenclatura consistente
- **Optimización Automática**: Ahorro de storage transparente

### Mejoras en Performance:
- **Detección Rápida**: Algoritmos optimizados para grandes volúmenes
- **Storage Eficiente**: Referencias automáticas para duplicados
- **Trazabilidad Completa**: Seguimiento de origen y procesamiento
- **Escalabilidad**: Sistema preparado para crecimiento de datos

**La librería compartida incluye ahora un sistema completo de gestión inteligente de archivos con optimización automática.**