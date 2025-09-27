# Sentrix YOLO Service - Servicio de Detección IA

Servicio de inteligencia artificial para la detección automatizada de criaderos de *Aedes aegypti* usando modelos YOLOv11. Incluye servidor HTTP FastAPI para integración con el backend.

## Descripción

Este servicio constituye el **núcleo de IA** de la plataforma Sentrix, proporcionando capacidades avanzadas de visión por computadora para detectar sitios de reproducción del mosquito *Aedes aegypti*:

- **Basura** - Nivel de riesgo medio
- **Calles deterioradas** - Nivel de riesgo alto
- **Acumulaciones de agua** - Nivel de riesgo alto
- **Huecos y depresiones** - Nivel de riesgo alto
- **Generación de imágenes procesadas** - Con marcadores azules de detecciones
- **Integración con nomenclatura estandarizada** - Nombres profesionales para archivos

## Arquitectura

### Estructura del Proyecto

```
yolo-service/
├── src/                   # Código fuente principal
│   ├── core/             # Lógica central de detección
│   │   ├── detector.py   # Motor de detección YOLO
│   │   ├── evaluator.py  # Evaluación de riesgo
│   │   └── trainer.py    # Entrenamiento de modelos
│   ├── utils/            # Utilidades del servicio
│   │   ├── device.py     # Gestión GPU/CPU
│   │   ├── file_ops.py   # Operaciones de archivos
│   │   ├── gps_metadata.py # Extracción GPS/EXIF
│   │   └── model_utils.py # Utilidades de modelos
│   └── reports/          # Generación de reportes
├── configs/              # Configuración del servicio
├── scripts/              # Scripts de utilidad
│   ├── batch_detection.py # Detección por lotes
│   ├── predict_new_images.py # Predicción individual
│   └── train_dengue_model.py # Entrenamiento
├── models/               # Modelos YOLO entrenados
├── tests/                # Tests automatizados
├── main.py               # CLI para detección
└── server.py             # Servidor FastAPI
```

## Características Principales

### Core de IA
- **Modelos YOLOv11** optimizados para detección de criaderos
- **Segmentación de instancias** con precisión a nivel de pixel
- **Múltiples arquitecturas** (nano, small, medium, large)
- **Selección automática** según capacidades de hardware
- **Generación de imágenes procesadas** con marcadores azules de detecciones
- **OpenCV integrado** para visualización y post-procesamiento

### Evaluación de Riesgo
- **Algoritmo epidemiológico** para clasificación de riesgo
- **Análisis contextual** de tipos de criaderos detectados
- **Métricas de confianza** por detección
- **Reportes estructurados** en JSON

### Optimización
- **Aceleración GPU** automática con CUDA
- **Procesamiento por lotes** para múltiples imágenes
- **Arquitectura modular** para mantenimiento
- **Paths portables** multiplataforma

### Funcionalidades Avanzadas
- **Imágenes Procesadas**: Generación automática con marcadores azules de detecciones
- **Visualización de Polígonos**: Dibujo preciso de boundaries de detección
- **Etiquetas Informativas**: Clase y confianza mostradas en cada detección
- **Integración con Nomenclatura**: Soporte para sistema estandarizado de archivos

## Configuración

### Variables de Entorno

```bash
# Puerto del servicio
YOLO_SERVICE_PORT=8001

# Configuración del modelo
YOLO_MODEL_PATH=models/best.pt
YOLO_CONFIDENCE_THRESHOLD=0.5
YOLO_DEVICE=auto

# Rendimiento
YOLO_BATCH_SIZE=10
YOLO_MAX_DETECTIONS=100
YOLO_TIMEOUT_SECONDS=60
```

### Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp ../.env.example ../.env

# Ejecutar servidor
python server.py
```

## Interfaces de Uso

### 1. Servidor HTTP (Puerto 8001)

API REST para integración con backend:

```bash
# Health check
curl http://localhost:8001/health

# Detección de imagen
curl -X POST "http://localhost:8001/detect" \
  -F "file=@imagen.jpg" \
  -F "confidence_threshold=0.5"

# Listar modelos disponibles
curl http://localhost:8001/models
```

### 2. CLI (Línea de Comandos)

```bash
# Detección individual
python main.py detect imagen.jpg

# Detección por lotes
python main.py batch-detect directorio_imagenes/

# Entrenamiento
python main.py train --data dataset.yaml --epochs 100

# Evaluación
python main.py evaluate --model models/best.pt --data test/
```

### 3. Scripts Especializados

```bash
# Procesamiento masivo
python scripts/batch_detection.py --input imagenes/ --output resultados/

# Predicción con modelo específico
python scripts/predict_new_images.py --model models/custom.pt --image test.jpg

# Entrenamiento personalizado
python scripts/train_dengue_model.py --config training_config.yaml
```

## API Endpoints

### Health y Estado
- `GET /health` - Estado del servicio
- `GET /models` - Modelos disponibles

### Detección Principal
- `POST /detect` - Detectar criaderos en imagen
  - `file`: Archivo de imagen (jpg, png, heic, etc.)
  - `confidence_threshold`: Umbral de confianza (0.1-1.0)
  - `include_gps`: Extraer metadatos GPS (default: true)
  - `generate_processed_image`: Crear imagen con marcadores (default: true)
  - `output_dir`: Directorio para imagen procesada (opcional)

### Respuesta de Detección

```json
{
  "analysis_id": "uuid",
  "status": "completed",
  "detections": [
    {
      "class_name": "Charcos/Cumulo de agua",
      "class_id": 2,
      "confidence": 0.85,
      "risk_level": "ALTO",
      "breeding_site_type": "Charcos/Cumulo de agua",
      "polygon": [[x1,y1], [x2,y2], ...],
      "mask_area": 1234.5
    }
  ],
  "total_detections": 3,
  "risk_assessment": {
    "overall_risk_level": "ALTO",
    "total_detections": 3,
    "high_risk_count": 2,
    "medium_risk_count": 1,
    "risk_score": 0.75
  },
  "location": {
    "has_location": true,
    "latitude": -26.831314,
    "longitude": -65.123456,
    "altitude_meters": 450.2
  },
  "processed_image": {
    "generated": true,
    "file_path": "temp/processed_image.jpg",
    "markers_count": 3,
    "marker_color": "blue"
  },
  "processing_time_ms": 1234,
  "model_used": "models/best.pt"
}
```

## Integración con Shared Library

El servicio utiliza la librería compartida para:

```python
# Importación de enums unificados
from shared.data_models import (
    DetectionRiskEnum,
    BreedingSiteTypeEnum,
    CLASS_ID_TO_BREEDING_SITE
)

# Evaluación de riesgo
from shared.risk_assessment import assess_dengue_risk

# Utilidades de archivos e imágenes
from shared.file_utils import validate_image_file
from shared.image_formats import ImageFormatConverter

# Sistema de nomenclatura estandarizada (integración con backend)
from shared.file_utils import generate_standardized_filename

# Logging centralizado
from shared.logging_utils import setup_yolo_logging
```

## Generación de Imágenes Procesadas

### Funcionalidad de Marcadores
El YOLO service ahora genera automáticamente imágenes procesadas con marcadores visuales:

```python
def _create_processed_image(source_path, result, output_dir=None):
    """
    Crear imagen procesada con marcadores azules de detecciones
    """
    # Cargar imagen original
    image = cv2.imread(source_path)

    # Dibujar polígonos y etiquetas para cada detección
    for detection in result.detections:
        color = (255, 100, 0)  # Azul en formato BGR

        # Dibujar polígono de la detección
        cv2.polylines(image, [polygon], isClosed=True, color=color, thickness=3)

        # Agregar etiqueta con clase y confianza
        label = f"{detection.class_name}: {detection.confidence:.2f}"
        cv2.putText(image, label, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # Guardar imagen procesada
    cv2.imwrite(output_path, image)
```

### Características de los Marcadores
- **Color azul** consistente para todas las detecciones
- **Polígonos precisos** siguiendo los boundaries de segmentación
- **Etiquetas informativas** con clase detectada y nivel de confianza
- **Calidad preservada** de la imagen original

## Formatos de Imagen Soportados

- **JPEG/JPG** - Formato estándar
- **PNG** - Con transparencia
- **HEIC/HEIF** - Formato Apple (conversión automática)
- **TIFF** - Alta calidad
- **WebP** - Formato web
- **BMP** - Bitmap básico

## Requisitos del Sistema

### Mínimos
- Python 3.8+
- 4GB RAM
- 2GB espacio en disco

### Recomendados
- Python 3.9+
- 8GB RAM
- GPU NVIDIA con CUDA 11.8+
- 10GB espacio en disco

## Desarrollo

### Ejecutar Tests

```bash
# Tests básicos
python -m pytest tests/test_unified.py -v

# Tests de detección
python -m pytest tests/test_model_inference.py -v

# Tests completos
python -m pytest tests/ -v
```

### Diagnóstico del Sistema

```bash
# Diagnóstico completo del hardware y modelos
python diagnostic.py
```

**Información proporcionada:**
- Hardware del sistema (CPU, memoria, disco)
- Estado de GPU y CUDA
- Modelos disponibles y recomendaciones
- Estado de dependencias
- Información de rendimiento

### Configuración GPU

```bash
# Verificar CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Configurar dispositivo
export YOLO_DEVICE=cuda  # o 'cpu' para forzar CPU
```

## Configuración de Puertos

- **YOLO Service**: Puerto 8001 (estandarizado)
- **Backend API**: Puerto 8000
- **Frontend**: Puerto 3000

## Documentación Adicional

- [Scripts de Corrección](../scripts/README.md)
- [Convenciones de Imports](../shared/IMPORT_CONVENTIONS.md)
- [Librería Compartida](../shared/README.md)

---

## Actualizaciones Recientes (v2.3.0)

### Nuevas Funcionalidades Implementadas:
- **Generación de Imágenes Procesadas**: Creación automática con marcadores azules de detecciones
- **Visualización Avanzada**: Polígonos precisos y etiquetas informativas con OpenCV
- **Integración con Nomenclatura**: Soporte para sistema estandarizado de archivos
- **API Extendida**: Nuevos parámetros para control de generación de imágenes

### Mejoras en Detección:
- **Marcadores Visuales**: Color azul consistente (255, 100, 0 en BGR)
- **Polígonos de Segmentación**: Boundaries precisos de cada detección
- **Etiquetas Dinámicas**: Clase y confianza mostradas automáticamente
- **Preservación de Calidad**: Imagen original mantenida sin degradación

### API Mejorada:
- **Parámetro `generate_processed_image`**: Control de generación de imágenes marcadas
- **Parámetro `output_dir`**: Especificación de directorio para archivos procesados
- **Respuesta extendida**: Información completa sobre imagen procesada generada
- **Compatibilidad**: Funciona con todos los formatos de imagen soportados

### Estado Actual:
- **YOLO Service funcionando** en puerto 8001 con funcionalidades avanzadas
- **Modelo cargado**: `models/best.pt` (19.6MB) con capacidades de visualización
- **Generación automática**: Imágenes procesadas creadas en cada detección
- **Integración completa**: Backend recibe URLs de imágenes originales y procesadas
- **OpenCV**: Librería integrada para procesamiento visual

### Integración Sistema:
- **Backend**: Recibe archivos procesados para almacenamiento dual
- **Shared Library**: Uso de nomenclatura estandarizada cuando requerido
- **Visualización**: Frontend puede mostrar comparación original vs procesada
- **Storage**: Optimización con sistema de deduplicación del backend

**El YOLO Service incluye ahora capacidades completas de visualización y generación de imágenes procesadas con marcadores precisos.**