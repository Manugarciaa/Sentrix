# YOLO Service - Servicio de Detección IA

Servicio de inteligencia artificial para detección automatizada de criaderos de *Aedes aegypti* usando modelos YOLOv11.

## Descripción

Núcleo de IA de la plataforma Sentrix que proporciona capacidades de visión por computadora para detectar sitios de reproducción del mosquito *Aedes aegypti*:

- **Charcos/Cúmulo de agua**: Nivel ALTO
- **Basura**: Nivel ALTO
- **Huecos**: Nivel MEDIO
- **Calles mal hechas**: Nivel MEDIO

### Características

- **Modelos YOLOv11**: Segmentación de instancias a nivel pixel
- **Detección Automática de Modelo**: Usa el modelo entrenado más reciente
- **Imágenes Procesadas**: Generación automática con marcadores azules
- **Evaluación de Riesgo**: Clasificación epidemiológica (ALTO/MEDIO/BAJO/MÍNIMO)
- **Aceleración GPU**: Soporte CUDA automático
- **Múltiples Formatos**: JPEG, PNG, HEIC, TIFF, WebP, BMP

## Estructura del Proyecto

```
yolo-service/
├── server.py                   # Servidor FastAPI (puerto 8001)
├── main.py                     # CLI para detección manual
├── train_simple.py             # Script de entrenamiento simplificado
├── train_optimized.py          # Entrenamiento con k-fold cross-validation
├── evaluate_final.py           # Evaluación de modelos entrenados
├── diagnostic.py               # Diagnóstico de sistema y hardware
├── requirements.txt            # Dependencias Python
├── src/
│   ├── core/                  # Módulos principales
│   │   ├── detector.py        # Detector YOLO (inferencia)
│   │   ├── evaluator.py       # Evaluador de modelos
│   │   └── trainer.py         # Entrenador de modelos
│   ├── reports/               # Generación de reportes
│   │   └── report_generator.py # PDF y análisis de resultados
│   └── utils/                 # Utilidades
│       ├── device.py          # Gestión de GPU/CPU
│       ├── file_ops.py        # Operaciones de archivo
│       ├── gps_metadata.py    # Extracción GPS de imágenes
│       └── paths.py           # Gestión de rutas
├── scripts/                   # Scripts de utilidad
│   ├── batch_detection.py     # Detección en batch
│   ├── predict_new_images.py  # Predicción de nuevas imágenes
│   └── train_dengue_model.py  # Script legacy de entrenamiento
├── configs/                   # Configuraciones de entrenamiento
│   ├── classes.py             # Definición de clases
│   └── fold_*.yaml            # Configs para k-fold (5 folds)
├── models/                    # Modelos YOLO entrenados
│   ├── best.pt               # Mejor modelo manual
│   ├── yolo11*-seg.pt        # Modelos base de Ultralytics
│   └── dengue_seg_*/         # Runs de entrenamiento (auto-detectados)
│       └── weights/best.pt
├── tests/                     # Suite de tests
│   ├── test_unified.py        # Tests unificados principales
│   ├── test_model_inference.py # Tests de inferencia
│   ├── test_gps_metadata.py   # Tests de extracción GPS
│   ├── test_api_server.py     # Tests del servidor API
│   └── test_complete_system.py # Tests de sistema completo
├── test_images/               # Imágenes de prueba
│   └── processed/             # Imágenes procesadas de tests
└── results/                   # Resultados de detecciones
    └── analysis/              # Análisis de dataset
```

## Instalación Rápida

```bash
# Instalar dependencias
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configurar .env (opcional)
cp ../.env.example ../.env

# Ejecutar servidor
python server.py
```

## Variables de Entorno

```bash
# Puerto del servicio
YOLO_SERVICE_PORT=8001

# Configuración del modelo (opcional - auto-detección)
YOLO_MODEL_PATH=models/best.pt
YOLO_CONFIDENCE_THRESHOLD=0.5
YOLO_DEVICE=auto  # auto, cuda, cpu

# Rendimiento
YOLO_BATCH_SIZE=10
YOLO_TIMEOUT_SECONDS=60
```

## API Endpoints

### Health Check
```bash
curl http://localhost:8001/health
```

### Detección de Imagen
```bash
curl -X POST "http://localhost:8001/detect" \
  -F "file=@imagen.jpg" \
  -F "confidence_threshold=0.5"
```

### Listar Modelos
```bash
curl http://localhost:8001/models
```

## Respuesta de Detección

```json
{
  "analysis_id": "uuid",
  "status": "completed",
  "detections": [
    {
      "class_name": "Charcos/Cumulo de agua",
      "confidence": 0.85,
      "risk_level": "ALTO",
      "polygon": [[x1,y1], [x2,y2], ...],
      "mask_area": 1234.5
    }
  ],
  "total_detections": 3,
  "risk_assessment": {
    "overall_risk_level": "ALTO",
    "high_risk_count": 2,
    "medium_risk_count": 1,
    "risk_score": 0.75
  },
  "location": {
    "has_location": true,
    "latitude": -26.831314,
    "longitude": -65.123456
  },
  "processed_image": {
    "generated": true,
    "file_path": "temp/processed_image.jpg"
  },
  "processing_time_ms": 1234,
  "model_used": "models/best.pt"
}
```

## Gestión Automática de Modelos

El servidor detecta automáticamente el modelo más reciente en este orden:

1. Variable de entorno `YOLO_MODEL_PATH` (máxima prioridad)
2. Último modelo en `models/dengue_seg_*/weights/best.pt` (por fecha)
3. Modelo manual en `models/best.pt`
4. Modelos base `models/yolo11*-seg.pt` (fallback)

### Verificar Modelo en Uso

```bash
curl http://localhost:8001/health
# Respuesta incluye: "model_path": "models/dengue_seg_n_100ep_20251003/weights/best.pt"
```

## Entrenamiento de Modelos

### Script Simplificado (Recomendado)

```bash
# Entrenamiento básico (50 épocas)
python train_simple.py --model models/yolo11s-seg.pt --epochs 50 --batch 8

# Entrenamiento extendido (100 épocas)
python train_simple.py --epochs 100 --batch 8

# Personalizar nombre
python train_simple.py --epochs 50 --name mi_modelo
```

**Características:**
- ✅ Configuración optimizada y probada
- ✅ Sin problemas de freeze durante validación
- ✅ Augmentación balanceada de datos
- ✅ Early stopping automático
- ✅ Guardado del mejor modelo

**Resultados en:**
```
models/dengue_seg_s_50ep_YYYYMMDD/
├── weights/
│   ├── best.pt      # Usar este modelo
│   └── last.pt      # Último checkpoint
└── results.csv      # Métricas
```

### Parámetros de Entrenamiento

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `--model` | Modelo base | `models/yolo11s-seg.pt` |
| `--epochs` | Número de épocas | `100` |
| `--batch` | Tamaño de batch | `8` |
| `--imgsz` | Tamaño de imagen | `640` |
| `--name` | Nombre del run | Auto |

## Uso por CLI

```bash
# Detección individual
python main.py detect imagen.jpg

# Detección por lotes
python main.py batch-detect directorio_imagenes/

# Procesamiento masivo
python scripts/batch_detection.py --input imagenes/ --output resultados/
```

## Testing

```bash
# Tests unificados
python -m pytest tests/test_unified.py -v

# Tests de detección
python -m pytest tests/test_model_inference.py -v

# Todos los tests
python -m pytest tests/ -v
```

## Diagnóstico del Sistema

```bash
python diagnostic.py
```

**Información proporcionada:**
- Hardware (CPU, memoria, disco)
- Estado GPU y CUDA
- Modelos disponibles y recomendaciones
- Dependencias y rendimiento

## Integración con Shared Library

```python
# Enums y tipos de datos
from sentrix_shared.data_models import (
    DetectionRiskEnum,
    BreedingSiteTypeEnum,
    CLASS_ID_TO_BREEDING_SITE
)

# Evaluación de riesgo
from sentrix_shared.risk_assessment import assess_dengue_risk

# Utilidades
from sentrix_shared.file_utils import validate_image_file
from sentrix_shared.image_formats import ImageFormatConverter
from sentrix_shared.gps_utils import extract_image_gps
```

**Instalación de Shared Library:**
```bash
cd ../shared && pip install -e .
python -c "from sentrix_shared import risk_assessment; print('OK')"
```

## Imágenes Procesadas

El servicio genera automáticamente imágenes con marcadores visuales:

- **Color azul** consistente para detecciones
- **Polígonos precisos** siguiendo boundaries
- **Etiquetas informativas** con clase y confianza
- **Calidad preservada** de imagen original

```python
# Ejemplo de generación
processed_image_path = _create_processed_image(
    source_path="imagen.jpg",
    result=detection_result,
    output_dir="temp/"
)
```

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

## Configuración GPU

```bash
# Verificar CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Forzar dispositivo
export YOLO_DEVICE=cuda  # o 'cpu'
```

## Solución de Problemas

**Error: Modelo no encontrado**
```bash
# Verificar modelos disponibles
ls -la models/

# Descargar modelo base
python -c "from ultralytics import YOLO; YOLO('yolo11s-seg.pt')"
```

**Error: CUDA out of memory**
```bash
# Reducir batch size
python train_simple.py --batch 4
```

**Error: Timeout en detección**
```bash
# Aumentar timeout
export YOLO_TIMEOUT_SECONDS=120
```

## Documentación Adicional

- **[Backend](../backend/README.md)**: API REST y integración
- **[Shared Library](../shared/README.md)**: Librería compartida
- **[Documentación completa](../docs/)**: Arquitectura y guías

---

**Puerto**: 8001 | **Modelo**: YOLOv11 | **Python**: 3.8+ | **Actualizado**: Octubre 2025
