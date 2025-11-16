# Stack Tecnológico - YOLO Service

Documentación completa de todas las herramientas, frameworks y librerías utilizadas en el servicio de detección YOLO del proyecto Sentrix.

---

## Core Framework

### YOLO y Deep Learning
- **Ultralytics** `8.3.198` - Framework YOLOv11 para detección y segmentación
- **PyTorch** `2.7.1` - Framework de deep learning
- **TorchVision** `0.22.1` - Utilidades de visión computacional para PyTorch

---

## Servidor Web

### FastAPI y ASGI
- **FastAPI** `0.116.1` - Framework web para API REST
- **Uvicorn** `0.35.0` - Servidor ASGI de alto rendimiento
- **python-multipart** `0.0.20` - Manejo de formularios multipart (uploads)
- **python-dotenv** `1.1.1` - Gestión de variables de entorno

---

## Procesamiento de Imágenes

### Librerías de Visión Computacional
- **OpenCV** `4.12.0.88` (headless) - Procesamiento de imágenes y computer vision
- **Pillow** `11.3.0` - Manipulación de imágenes
- **pillow-heif** `1.1.0` - Soporte para formatos HEIF/HEIC
- **NumPy** `2.2.6` - Computación numérica y arrays

### Metadata
- **ExifRead** `3.0.0` - Lectura de metadata EXIF (GPS, cámara, etc.)

---

## Visualización y Análisis

### Data Science
- **Pandas** `2.3.2` - Análisis y manipulación de datos
- **Matplotlib** `3.10.5` - Visualización de gráficos y resultados
- **tqdm** `4.67.1` - Barras de progreso

---

## Configuración y Validación

### Configuración
- **PyYAML** `6.0.2` - Parsing de archivos YAML (configuración de datasets)
- **Pydantic** `2.11.7` - Validación de datos y schemas
- **pydantic-settings** `2.1.0` - Gestión de configuración con Pydantic

---

## Seguridad

### Rate Limiting y Validación
- **slowapi** `0.1.9` - Rate limiting para FastAPI
- **python-magic** `0.4.27` - Validación de tipos MIME
- **python-magic-bin** `0.4.14` - Binarios de libmagic para Windows

---

## Utilidades del Sistema

### System Utilities
- **psutil** `7.0.0` - Monitoreo de CPU, memoria, GPU
- **requests** `2.32.4` - Cliente HTTP

---

## Testing

### Testing Framework
- **pytest** `8.4.1` - Framework de testing

---

## Librería Compartida

### Sentrix Shared
- **sentrix_shared** (editable install) - Librería compartida con backend
  - Utilidades de GPS
  - Modelos de datos compartidos
  - Funciones de extracción de metadata

---

## Modelos de IA

### YOLOv11 Variants
El servicio soporta múltiples variantes de YOLOv11 para instance segmentation:

- **yolo11n-seg.pt** - Nano (6.7MB, más rápido)
- **yolo11s-seg.pt** - Small (24MB, balanceado) - Recomendado
- **yolo11m-seg.pt** - Medium (49MB, preciso)
- **yolo11l-seg.pt** - Large (77MB, muy preciso)
- **yolo11x-seg.pt** - Extra Large (140MB, máxima precisión)

### Modelo Personalizado
- **best.pt** - Modelo entrenado específicamente para detección de criaderos de Aedes aegypti
  - 4 clases: Charcos, Basura, Huecos, Calles mal hechas
  - Instance segmentation a nivel pixel
  - Entrenado con dataset anotado de criaderos reales

---

## Hardware y Aceleración

### GPU Support
- **CUDA** `11.8+` - Aceleración GPU (opcional)
- **cuDNN** - Optimizaciones de deep learning (incluido con PyTorch)

### Compatibilidad
- **CPU**: Totalmente funcional (más lento)
- **GPU**: NVIDIA con CUDA 11.8+ recomendado
- **MPS**: Soporte para Apple Silicon (experimental)

---

## Arquitectura del Servicio

### Componentes Principales

**Detector (src/core/detector.py)**
- Motor de detección YOLO
- Procesamiento de imágenes
- Generación de máscaras de segmentación
- Evaluación de riesgo

**Server (server.py)**
- API REST con FastAPI
- Health checks
- Manejo de uploads
- Rate limiting

**CLI (main.py)**
- Detección individual
- Procesamiento batch
- Interfaz de línea de comandos

**Training (train_simple.py)**
- Entrenamiento de modelos
- Fine-tuning
- Transfer learning

---

## Características Técnicas

### Instance Segmentation
- Detección a nivel de pixel
- Polígonos precisos de contorno
- Máscaras binarias por objeto
- Bounding boxes

### Procesamiento de Imágenes
- Soporte multi-formato: JPEG, PNG, HEIC, TIFF, WebP, BMP
- Extracción de GPS desde EXIF
- Generación de imagen procesada con marcadores
- Codificación Base64 para transferencia

### Performance
- Procesamiento asíncrono
- Batch processing
- Auto-detección de hardware (GPU/CPU)
- Optimización CUDA cuando disponible

---

## Formatos Soportados

### Entrada
- **Imágenes**: JPEG, PNG, HEIC, TIFF, WebP, BMP
- **Metadata**: EXIF GPS, orientación, fecha

### Salida
- **JSON**: Detecciones estructuradas
- **Imagen procesada**: JPEG con marcadores de color
- **Polígonos**: Coordenadas de segmentación
- **Métricas**: Confianza, área, riesgo

---

## Métricas de Modelo

### Métricas de Evaluación
- **mAP@50** - Mean Average Precision al 50% IoU
- **mAP@50-95** - mAP promediado de 50% a 95% IoU
- **Precision** - Ratio de detecciones correctas
- **Recall** - Ratio de objetos detectados
- **F1-Score** - Media armónica de precision y recall

### Objetivos de Performance
- mAP@50 > 0.80 (bueno) / 0.90 (excelente)
- Precision > 0.85
- Recall > 0.80
- Tiempo de inferencia < 1s en GPU

---

## Scripts de Desarrollo

### Training (scripts/training/)
- **analyze_dataset.py** - Análisis de distribución y calidad
- **train_optimized.py** - K-fold cross-validation
- **evaluate_final.py** - Evaluación detallada

### Diagnostics (scripts/diagnostics/)
- **diagnostic.py** - Diagnóstico de sistema

### Testing (scripts/testing/)
- **test_new_model.py** - Test rápido de modelos
- **utils.py** - Utilidades compartidas

---

## Patrones y Técnicas de IA

### Data Augmentation
- Rotación aleatoria
- Flip horizontal/vertical
- Ajuste de brillo y contraste
- Mosaic augmentation
- Copy-paste (para clases minoritarias)
- MixUp

### Training Strategies
- Transfer learning desde YOLOv11 pre-entrenado
- Fine-tuning con dataset específico
- K-fold cross-validation para datasets pequeños
- Learning rate scheduling (OneCycleLR, CosineAnnealing)
- Early stopping
- Class balancing

### Optimizaciones
- Automatic Mixed Precision (AMP)
- Gradient accumulation
- Model pruning (experimental)
- Quantization (experimental)

---

## Requisitos de Sistema

### Mínimos
- Python 3.9+
- CPU: 2+ cores
- RAM: 4GB
- Disco: 2GB (5GB con modelos y datasets)

### Recomendados
- Python 3.10+
- GPU: NVIDIA con CUDA 11.8+
- VRAM: 4GB+
- RAM: 8GB+
- Disco: 10GB+ (para entrenamiento)

---

## Performance Benchmarks

### Tiempo por Imagen

| Hardware | Modelo | Tiempo | Throughput |
|----------|--------|--------|------------|
| CPU (4 cores) | yolo11s-seg | 3-5s | 12-20 img/min |
| RTX 3060 | yolo11s-seg | 0.5-1s | 60-120 img/min |
| RTX 4090 | yolo11s-seg | 0.2-0.4s | 150-300 img/min |
| CPU (4 cores) | yolo11m-seg | 5-8s | 7-12 img/min |
| RTX 3060 | yolo11m-seg | 0.8-1.5s | 40-75 img/min |

---

## Documentación y APIs

### Documentación Automática
- **Swagger UI** - Disponible en `/docs`
- **ReDoc** - Disponible en `/redoc`
- **OpenAPI Schema** - Generado automáticamente

### Endpoints Principales
- `POST /detect` - Detección de criaderos
- `GET /health` - Health check con info del modelo

---

**Última actualización:** Noviembre 2025
