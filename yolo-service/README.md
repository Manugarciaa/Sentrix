# Sentrix YOLO Service - Servicio de Detección IA

Servicio de inteligencia artificial para la detección automatizada de criaderos de *Aedes aegypti* usando modelos YOLOv11. Incluye servidor HTTP FastAPI para integración con el backend.

## Descripción

Este servicio constituye el **núcleo de IA** de la plataforma Sentrix, proporcionando capacidades de visión por computadora para detectar sitios de reproducción del mosquito *Aedes aegypti*:

- **Basura** - Nivel de riesgo medio
- **Calles deterioradas** - Nivel de riesgo alto
- **Acumulaciones de agua** - Nivel de riesgo alto
- **Huecos y depresiones** - Nivel de riesgo alto

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
├── main.py              # CLI principal
└── server.py            # Servidor FastAPI
```

## Características Principales

### Core de IA
- **Modelos YOLOv11** optimizados para detección de criaderos
- **Segmentación de instancias** con precisión a nivel de pixel
- **Múltiples arquitecturas** (nano, small, medium, large)
- **Selección automática** según capacidades de hardware

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

# Logging centralizado
from shared.logging_utils import setup_yolo_logging
```

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

- [Convenciones de Imports](../shared/IMPORT_CONVENTIONS.md)
- [Configuración de Entorno](../scripts/setup-env.py)
- [Formatos de Imagen](../shared/image_formats.py)