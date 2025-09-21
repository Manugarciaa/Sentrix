# Sentrix Shared Library

## 📋 Descripción

La librería compartida de Sentrix contiene toda la funcionalidad común utilizada por los servicios backend y yolo-service. Esta librería garantiza consistencia, reduce duplicación de código y facilita el mantenimiento.

## 🚀 Inicio Rápido

### Configuración de Imports

```python
# Configurar imports automáticamente para tu servicio
from shared import setup_service_imports

# Para backend
setup_service_imports('backend')

# Para yolo-service
setup_service_imports('yolo-service')
```

### Imports Básicos

```python
# Evaluación de riesgo
from shared import assess_dengue_risk

# Modelos de datos
from shared import DetectionRiskEnum, BreedingSiteTypeEnum

# Utilidades de archivos
from shared import validate_image_file, extract_gps_from_exif

# Logging
from shared import setup_backend_logging, log_detection_result

# Manejo de errores
from shared import SentrixError, ValidationError, handle_exception

# Configuración
from shared import load_service_config
```

## 📚 Módulos Disponibles

### 1. Risk Assessment (`risk_assessment.py`)

Evaluación unificada de riesgo epidemiológico.

```python
from shared import assess_dengue_risk

# Evaluar riesgo de detecciones
detections = [
    {'class': 'Charcos/Cumulo de agua', 'confidence': 0.9},
    {'class': 'Basura', 'confidence': 0.8}
]

risk_result = assess_dengue_risk(detections)
print(risk_result['level'])  # 'ALTO'
print(risk_result['recommendations'])  # Lista de recomendaciones
```

### 2. Data Models (`data_models.py`)

Enums y modelos de datos unificados.

```python
from shared import (
    DetectionRiskEnum,
    BreedingSiteTypeEnum,
    normalize_breeding_site_type,
    get_risk_level_for_breeding_site
)

# Usar enums
risk = DetectionRiskEnum.ALTO
site_type = BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA

# Normalizar datos
normalized = normalize_breeding_site_type("Charcos")
# Resultado: BreedingSiteTypeEnum.CHARCOS_CUMULO_AGUA

# Obtener nivel de riesgo por defecto
risk_level = get_risk_level_for_breeding_site(site_type)
# Resultado: DetectionRiskEnum.ALTO
```

### 3. File Utils (`file_utils.py`)

Utilidades robustas para manejo de archivos.

```python
from shared import (
    validate_image_file,
    validate_batch_files,
    extract_filename_from_url,
    safe_filename
)

# Validar imagen individual
validation = validate_image_file("path/to/image.jpg")
if validation['is_valid']:
    print(f"Archivo válido: {validation['mime_type']}")

# Validar lote de archivos
file_paths = ["image1.jpg", "image2.png"]
batch_validation = validate_batch_files(file_paths)
print(f"Archivos válidos: {len(batch_validation['valid_files'])}")

# Extraer nombre de URL
filename = extract_filename_from_url("https://example.com/photos/dengue.jpg")
# Resultado: "dengue.jpg"
```

### 4. GPS Utils (`gps_utils.py`)

Utilidades avanzadas para GPS y metadatos EXIF.

```python
from shared import (
    extract_gps_from_exif,
    extract_camera_info_from_exif,
    validate_gps_coordinates,
    generate_maps_urls
)

# Extraer GPS de imagen
gps_data = extract_gps_from_exif("image_with_gps.jpg")
if gps_data['has_gps']:
    print(f"Ubicación: {gps_data['latitude']}, {gps_data['longitude']}")

# Extraer información de cámara
camera_info = extract_camera_info_from_exif("image.jpg")
print(f"Cámara: {camera_info['camera_make']} {camera_info['camera_model']}")

# Generar URLs de mapas
urls = generate_maps_urls(latitude=-12.0464, longitude=-77.0428)
print(f"Google Maps: {urls['google_maps']}")
```

### 5. Logging (`logging_utils.py`)

Sistema de logging profesional y unificado.

```python
from shared import (
    setup_backend_logging,
    setup_yolo_logging,
    log_detection_result,
    log_performance,
    ProgressLogger
)

# Configurar logging para servicio
logger = setup_backend_logging('INFO')

# Log de detección
log_detection_result(logger, "image.jpg", detections_count=5, processing_time_ms=1250)

# Log de rendimiento
log_performance(logger, "image_processing", 1250, image_size="1920x1080")

# Progress logger para operaciones largas
with ProgressLogger(logger, "batch_processing", total_items=100) as progress:
    for i in range(100):
        # Procesar item
        progress.update()
```

### 6. Error Handling (`error_handling.py`)

Manejo unificado de errores y excepciones.

```python
from shared import (
    SentrixError,
    ValidationError,
    FileProcessingError,
    handle_exception,
    safe_execute
)

# Lanzar error específico
def validate_input(data):
    if not data.get('required_field'):
        raise ValidationError(
            "Campo requerido faltante",
            field="required_field"
        )

# Manejo automático de errores
def risky_operation():
    try:
        # Operación que puede fallar
        result = process_image("corrupted.jpg")
        return result
    except Exception as e:
        return handle_exception(e, logger, context={'operation': 'image_processing'})

# Ejecución segura
result = safe_execute(
    operation=lambda: download_image(url),
    logger=logger,
    operation_name="download_image",
    context={'url': url},
    default_return=None
)
```

### 7. Configuration (`config_manager.py`)

Gestión centralizada de configuración.

```python
from shared import load_service_config, ConfigManager

# Cargar configuración para servicio
config = load_service_config('backend')

# Acceder a configuración
if config.is_production:
    logger.setLevel('WARNING')

# Usar configuración específica
yolo_url = config.yolo_service.url
db_url = config.database.url

# Configuración personalizada
manager = ConfigManager('my-service')
config = manager.load_config('custom-config.yaml')
```

### 8. Project Structure (`project_structure.py`)

Gestión de estructura de proyecto y paths.

```python
from shared import (
    setup_service_structure,
    get_backend_structure,
    validate_service_structure
)

# Configurar estructura estándar
structure = setup_service_structure('backend')

# Obtener paths importantes
src_path = structure.src_dir
logs_path = structure.logs_dir

# Validar estructura
validation = validate_service_structure('backend')
if validation['src_exists']:
    print("Estructura válida")
```

### 9. Import Utils (`import_utils.py`)

Gestión optimizada de imports y dependencias.

```python
from shared import (
    setup_service_imports,
    validate_service_dependencies,
    safe_import,
    lazy_import
)

# Configurar imports para servicio
setup_service_imports('yolo-service')

# Validar dependencias
deps = validate_service_dependencies('backend')
if not deps['all_required_available']:
    print(f"Dependencias faltantes: {deps['missing_required']}")

# Import seguro con fallback
torch = safe_import('torch', fallback=None)
if torch is None:
    print("PyTorch no disponible")

# Import lazy para dependencias opcionales
@lazy_import('ultralytics')
def process_with_yolo(yolo_module, image_path):
    model = yolo_module.YOLO('model.pt')
    return model(image_path)
```

## 🛠️ Patrones de Uso Recomendados

### Inicialización de Servicio

```python
# En el archivo principal de tu servicio (main.py, server.py)
from shared import (
    setup_service_imports,
    load_service_config,
    setup_backend_logging,  # o setup_yolo_logging
    log_system_info
)

# 1. Configurar imports
setup_service_imports('backend')  # o 'yolo-service'

# 2. Cargar configuración
config = load_service_config('backend')

# 3. Configurar logging
logger = setup_backend_logging(config.logging.level)

# 4. Log información del sistema
log_system_info(logger, config.service_name, config.version)
```

### Procesamiento de Imágenes

```python
from shared import (
    validate_image_file,
    extract_gps_from_exif,
    assess_dengue_risk,
    log_detection_result,
    handle_exception
)

def process_image(image_path, logger):
    try:
        # 1. Validar archivo
        validation = validate_image_file(image_path)
        if not validation['is_valid']:
            raise ValidationError(f"Archivo inválido: {validation['errors']}")

        # 2. Extraer GPS
        gps_data = extract_gps_from_exif(image_path)

        # 3. Procesar con IA (específico del servicio)
        detections = run_ai_detection(image_path)

        # 4. Evaluar riesgo
        risk_assessment = assess_dengue_risk(detections)

        # 5. Log resultado
        log_detection_result(logger, image_path, len(detections), processing_time_ms)

        return {
            'detections': detections,
            'risk_assessment': risk_assessment,
            'gps_data': gps_data
        }

    except Exception as e:
        return handle_exception(e, logger, context={'image_path': image_path})
```

### Manejo de Errores en APIs

```python
from fastapi import HTTPException
from shared import SentrixError, create_error_response

@app.post("/analyze")
async def analyze_image(file: UploadFile):
    try:
        result = await process_image(file)
        return {"success": True, "data": result}

    except SentrixError as e:
        # Error conocido del sistema
        response = create_error_response(e)
        raise HTTPException(status_code=400, detail=response)

    except Exception as e:
        # Error inesperado
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

## 🔧 Configuración Avanzada

### Variables de Entorno

```bash
# Configuración de logging
SENTRIX_LOG_LEVEL=INFO

# Configuración de servicios
SENTRIX_YOLO_SERVICE_URL=http://yolo-service:8002
SENTRIX_DATABASE_URL=postgresql://user:pass@db:5432/sentrix

# Configuración de seguridad
SENTRIX_JWT_SECRET=your-secret-key
SENTRIX_MAX_FILE_SIZE=50

# Configuración de CORS
SENTRIX_ALLOWED_ORIGINS=https://app.sentrix.com,https://admin.sentrix.com
```

### Archivo de Configuración

```yaml
# backend.yaml
service_name: "sentrix-backend"
debug: false

logging:
  level: "INFO"
  file_logging: true
  console_logging: true

yolo_service:
  url: "http://yolo-service:8002"
  timeout_seconds: 60.0
  confidence_threshold: 0.6

security:
  max_file_size_mb: 50
  allowed_file_types: [".jpg", ".jpeg", ".png"]
```

## 🧪 Testing

```python
import pytest
from shared import assess_dengue_risk, ValidationError

def test_risk_assessment():
    detections = [
        {'class': 'Charcos/Cumulo de agua', 'confidence': 0.9}
    ]
    result = assess_dengue_risk(detections)
    assert result['level'] == 'ALTO'
    assert len(result['recommendations']) > 0

def test_validation_error():
    with pytest.raises(ValidationError) as exc_info:
        validate_required_fields({}, ['required_field'])

    assert 'required_field' in str(exc_info.value)
```

## 📖 Changelog

### v1.0.0 (2024-09-21)
- ✅ Evaluación de riesgo unificada
- ✅ Modelos de datos compartidos
- ✅ Utilidades de archivos y GPS
- ✅ Sistema de logging profesional
- ✅ Manejo de errores robusto
- ✅ Gestión de configuración
- ✅ Estructura de proyecto estandarizada
- ✅ Utilidades de import optimizadas

## 🤝 Contribución

Para contribuir a la librería compartida:

1. Mantén la compatibilidad hacia atrás
2. Agrega tests para nueva funcionalidad
3. Documenta los cambios en este README
4. Sigue los patrones de código existentes
5. Actualiza la versión en `__init__.py`

## 📞 Soporte

Para problemas o preguntas sobre la librería compartida, consulta:
- Documentación de arquitectura: `../ARCHITECTURE.md`
- Código de ejemplo en los servicios
- Tests unitarios en `../backend/tests/` y `../yolo-service/tests/`