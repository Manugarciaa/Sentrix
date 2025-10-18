# Sentrix Shared Library - Librería Compartida

Paquete Python `sentrix_shared` que contiene funcionalidad común para backend y yolo-service. Garantiza consistencia, reduce duplicación y facilita el mantenimiento.

## Descripción

Centraliza componentes críticos para asegurar consistencia entre servicios:

- **Enums unificados**: Tipos de riesgo, criaderos, estados y roles
- **Evaluación de riesgo**: Algoritmos epidemiológicos compartidos
- **Utilidades de archivos**: Validación, procesamiento y nomenclatura estandarizada
- **Sistema de deduplicación**: Detección inteligente de contenido duplicado
- **Manejo de errores**: Excepciones estandarizadas
- **Logging centralizado**: Sistema de logs unificado
- **Soporte de formatos**: Conversión automática de imágenes (HEIC, JPEG, PNG, etc.)

## Estructura del Proyecto

```
shared/
├── sentrix_shared/            # Paquete principal
│   ├── __init__.py           # Exports principales del paquete
│   ├── data_models.py         # Enums y modelos de datos
│   ├── risk_assessment.py     # Algoritmos de evaluación epidemiológica
│   ├── file_utils.py          # Utilidades + nomenclatura estandarizada
│   ├── image_deduplication.py # Sistema de deduplicación por hash
│   ├── image_formats.py       # Soporte y conversión de formatos
│   ├── gps_utils.py           # Extracción GPS/EXIF de imágenes
│   ├── logging_utils.py       # Sistema de logging unificado
│   ├── error_handling.py      # Manejo de errores estandarizado
│   ├── config_manager.py      # Gestión de configuración compartida
│   ├── temporal_persistence.py # Validez temporal de coordenadas GPS
│   ├── import_utils.py        # Utilidades de importación
│   └── project_structure.py   # Estructura del proyecto
├── tests/                     # Suite de tests
│   ├── test_image_formats.py      # Tests de conversión de formatos
│   ├── test_standardized_naming.py # Tests de nomenclatura
│   └── test_temporal_persistence.py # Tests de validez temporal
├── pyproject.toml             # Configuración del paquete (PEP 518)
├── MANIFEST.in                # Archivos a incluir en distribución
├── requirements.txt           # Dependencias
├── .gitignore                 # Archivos ignorados por git
└── README.md                  # Este archivo
```

## Instalación

```bash
# Instalar en modo editable
cd shared
pip install -e .

# O desde otro directorio
pip install -e ../shared
```

## Componentes Principales

### 1. Enums Unificados

```python
from sentrix_shared.data_models import (
    # Tipos de riesgo
    DetectionRiskEnum,        # ALTO, MEDIO, BAJO, MINIMO

    # Tipos de criaderos
    BreedingSiteTypeEnum,     # BASURA, CALLES_MAL_HECHAS,
                             # CHARCOS_CUMULO_AGUA, HUECOS

    # Estados
    AnalysisStatusEnum,       # PENDING, PROCESSING, COMPLETED, FAILED
    ValidationStatusEnum,     # PENDING_VALIDATION, VALIDATED_POSITIVE, etc.

    # Usuarios
    UserRoleEnum,            # USER, ADMIN, EXPERT
    LocationSourceEnum       # EXIF_GPS, MANUAL, ESTIMATED
)
```

### 2. Evaluación de Riesgo

```python
from sentrix_shared.risk_assessment import assess_dengue_risk

detections = [
    {"class": "Charcos/Cumulo de agua", "confidence": 0.85},
    {"class": "Basura", "confidence": 0.75}
]

risk = assess_dengue_risk(detections)
# Retorna: {
#   'overall_risk_level': 'ALTO',
#   'risk_distribution': {...},
#   'total_detections': 2,
#   'high_risk_sites': 2
# }
```

### 3. Nomenclatura Estandarizada

```python
from sentrix_shared.file_utils import (
    generate_standardized_filename,
    create_filename_variations,
    parse_standardized_filename
)

# Generar nombre estandarizado
filename = generate_standardized_filename(
    original_filename="IMG_1234.jpg",
    camera_info={"camera_make": "Apple", "camera_model": "iPhone 15"},
    gps_data={"latitude": -34.603722, "longitude": -58.381592},
    analysis_timestamp=datetime.now()
)
# Resultado: SENTRIX_20250926_143052_IPHONE15_LATn34p604_LONn58p382_a1b2c3d4.jpg

# Crear variaciones (original, processed, thumbnail)
variations = create_filename_variations(
    base_filename="IMG_1234.jpg",
    camera_info=camera_info,
    gps_data=gps_data
)
```

### 4. Sistema de Deduplicación

```python
from sentrix_shared.image_deduplication import (
    check_image_duplicate,
    calculate_content_signature,
    estimate_storage_savings
)

# Calcular firma de contenido
signature = calculate_content_signature(image_data)
# {'sha256': 'abc123...', 'md5': 'def456...', 'size_bytes': 1024000}

# Verificar duplicados
duplicate_check = check_image_duplicate(
    image_data=image_data,
    existing_analyses=[...],
    camera_info={"camera_make": "Apple"},
    gps_data={"latitude": -34.603, "longitude": -58.381}
)
# {
#   'is_duplicate': True/False,
#   'duplicate_analysis_id': 'uuid',
#   'confidence': 0.85
# }

# Estimar ahorro
savings = estimate_storage_savings(duplicate_analyses)
# {
#   'storage_saved_mb': 125.5,
#   'deduplication_rate': 25.0
# }
```

### 5. Formatos de Imagen

```python
from sentrix_shared.image_formats import (
    ImageFormatConverter,
    is_format_supported,
    SUPPORTED_IMAGE_FORMATS
)

# Verificar soporte
if is_format_supported('.heic'):
    converter = ImageFormatConverter()
    result = converter.convert_heic_to_jpeg("photo.heic", "photo.jpg")
```

### 6. Logging Unificado

```python
from sentrix_shared.logging_utils import (
    setup_backend_logging,
    setup_yolo_logging,
    log_detection_result
)

# Configurar logger
logger = setup_backend_logging('INFO')

# Log específico de detección
log_detection_result(logger, analysis_id, detections, processing_time)
```

### 7. Manejo de Errores

```python
from sentrix_shared.error_handling import (
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

## Uso por Servicio

### Backend

```python
# Enums y validación
from sentrix_shared.data_models import ValidationStatusEnum, UserRoleEnum
from sentrix_shared.file_utils import validate_image_file

# Nomenclatura y deduplicación
from sentrix_shared.file_utils import generate_standardized_filename
from sentrix_shared.image_deduplication import check_image_duplicate

# Evaluación de riesgo
from sentrix_shared.risk_assessment import assess_dengue_risk
from sentrix_shared.logging_utils import setup_backend_logging
```

### YOLO Service

```python
# Detección
from sentrix_shared.data_models import DetectionRiskEnum, CLASS_ID_TO_BREEDING_SITE
from sentrix_shared.risk_assessment import assess_dengue_risk

# Procesamiento de imágenes
from sentrix_shared.image_formats import ImageFormatConverter
from sentrix_shared.gps_utils import extract_image_gps
from sentrix_shared.file_utils import generate_standardized_filename
```

## Mapeos y Constantes

```python
from sentrix_shared.data_models import (
    # Mapeo YOLO a enums
    CLASS_ID_TO_BREEDING_SITE,     # {0: BASURA, 1: CALLES_MAL_HECHAS, ...}
    BREEDING_SITE_TO_CLASS_ID,     # Mapeo inverso

    # Clasificaciones de riesgo
    HIGH_RISK_CLASSES,             # Criaderos alto riesgo
    MEDIUM_RISK_CLASSES            # Criaderos medio riesgo
)
```

## Formatos Soportados

| Formato | Extensión | Conversión | GPS |
|---------|-----------|------------|-----|
| JPEG    | .jpg, .jpeg | Nativo | ✅ |
| PNG     | .png | Nativo | ✅ |
| HEIC    | .heic, .heif | Auto → JPEG | ✅ |
| TIFF    | .tiff, .tif | Nativo | ✅ |
| WebP    | .webp | Nativo | ✅ |
| BMP     | .bmp | Nativo | ❌ |

## Testing

```bash
# Tests de shared library
cd shared && python -m pytest tests/ -v

# Test de importación
python -c "from sentrix_shared.data_models import DetectionRiskEnum; print('OK')"

# Verificar instalación
python -c "from sentrix_shared import risk_assessment; print('Installed')"

# Tests desde raíz del proyecto
python scripts/simple_test.py
python scripts/test_deduplication.py
```

## Convenciones de Importación

### ✅ Correcto

```python
# Importación directa desde sentrix_shared
from sentrix_shared.data_models import DetectionRiskEnum, BreedingSiteTypeEnum
from sentrix_shared.risk_assessment import assess_dengue_risk
from sentrix_shared.file_utils import generate_standardized_filename
```

### ❌ Evitar

```python
# No usar re-exportaciones locales
from app.models.enums import DetectionRiskEnum  # ❌

# No usar importaciones indirectas
from src.database.models.enums import *  # ❌

# No usar imports legacy de "shared"
from shared.data_models import DetectionRiskEnum  # ❌ (legacy, usar sentrix_shared)
```

## Variables de Entorno

```bash
# Servicios
YOLO_SERVICE_URL=http://localhost:8001
DATABASE_URL=postgresql://...

# Logging
LOG_LEVEL=INFO
LOG_FILE_SHARED=./logs/shared.log

# Procesamiento
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=.jpg,.jpeg,.png,.heic
```

## Desarrollo

### Agregar Nuevos Componentes

1. Crear módulo en `shared/nuevo_modulo.py`
2. Agregar exports en `shared/__init__.py`
3. Documentar en README
4. Crear tests en `shared/tests/`
5. Actualizar servicios que lo usen

### Principios de Diseño

- **Stateless**: Sin estado global
- **Portabilidad**: Funciona en todos los entornos
- **Consistencia**: Misma interfaz para todos los servicios
- **Testing**: Cobertura completa

## Compatibilidad

- **Python mínimo**: 3.8+
- **Python recomendado**: 3.9+
- **Testado en**: 3.8, 3.9, 3.10, 3.11

## Documentación Adicional

- **[Backend](../backend/README.md)**: API REST
- **[YOLO Service](../yolo-service/README.md)**: Detección IA
- **[Documentación completa](../docs/)**: Arquitectura y guías

---

**Python**: 3.8+ | **Dependencias**: Ver `requirements.txt` | **Actualizado**: Octubre 2025
