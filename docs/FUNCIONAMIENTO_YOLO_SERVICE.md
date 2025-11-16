# Cómo Funciona YOLO Service

Documentación detallada del funcionamiento interno del servicio de detección IA de Sentrix.

---

# YOLO SERVICE - Servicio de Detección IA

## Descripción General

El YOLO Service es el cerebro de la detección. Recibe imágenes, las analiza con inteligencia artificial y devuelve información detallada sobre los criaderos de Aedes aegypti detectados.

---

## Flujo Completo de Detección

### 1. Recepción de Imagen

**Endpoint:** `POST /detect`

**Input:**
- Imagen (JPEG, PNG, HEIC, TIFF, BMP, WebP)
- Umbral de confianza (opcional, default: 0.5)

**Validaciones de Seguridad:**
```
1. Tamaño máximo: 50MB
2. MIME type validation (python-magic)
3. Rate limiting: Por IP
4. Sanitización de nombre de archivo
5. Almacenamiento temporal seguro
```

---

### 2. Extracción de Metadata GPS

**Proceso:**

```python
# 1. Lee metadata EXIF de la imagen
exif_data = image.getexif()

# 2. Busca tags GPS específicos
- GPSLatitude
- GPSLongitude
- GPSAltitude
- GPSDateStamp
- GPSTimeStamp

# 3. Convierte coordenadas
# De formato: Grados/Minutos/Segundos
# A formato: Decimal (-34.603722, -58.381592)

# 4. Extrae info de cámara
- Marca (Apple, Samsung, etc.)
- Modelo (iPhone 15, Galaxy S23, etc.)
- Fecha de captura
- Orientación
```

**Output GPS:**
```json
{
  "has_gps": true,
  "latitude": -34.603722,
  "longitude": -58.381592,
  "altitude": 520.5,
  "coordinates": "-34.603722, -58.381592",
  "gps_date": "2025-11-15 14:30:00",
  "location_source": "EXIF_GPS",
  "camera_info": {
    "make": "Apple",
    "model": "iPhone 15 Pro",
    "capture_date": "2025-11-15 14:30:00"
  }
}
```

**Casos sin GPS:**
```json
{
  "has_location": false,
  "reason": "No GPS coordinates in image EXIF"
}
```

---

### 3. Detección con YOLOv11

**Proceso de Inferencia:**

```python
# 1. Carga del modelo
model = YOLO('models/best.pt')  # Modelo entrenado

# 2. Configuración de detección
- Task: 'segment' (instance segmentation)
- Confidence threshold: 0.5 (configurable)
- Device: auto (GPU si disponible, CPU sino)

# 3. Ejecución de inferencia
results = model(image, conf=0.5, task='segment')

# 4. Por cada detección:
for detection in results:
    - Class ID (0-3: tipo de criadero)
    - Confidence score (0.0-1.0)
    - Bounding box (x, y, width, height)
    - Segmentation mask (polígono a nivel pixel)
    - Mask area (área en pixels)
```

**Clases de Criaderos:**
```python
DENGUE_CLASSES = {
    0: 'Basura',
    1: 'Calles mal hechas',
    2: 'Charcos/Cumulo de agua',
    3: 'Huecos'
}

RISK_LEVEL_BY_ID = {
    0: 'ALTO',      # Basura
    1: 'MEDIO',     # Calles mal hechas
    2: 'ALTO',      # Charcos/Agua
    3: 'MEDIO'      # Huecos
}
```

---

### 4. Procesamiento de Máscaras

**Extracción de Polígonos:**

```python
# 1. YOLO devuelve máscaras binarias (matriz de 0s y 1s)
mask = [[0,0,0,1,1,1,0,0],
        [0,0,1,1,1,1,1,0],
        [0,1,1,1,1,1,1,1],
        ...]

# 2. Se extraen coordenadas del contorno
polygon = mask.xy[0]  # Array de [x,y] puntos

# 3. Se calcula área
area = mask.data.sum()  # Suma de pixels = 1

# 4. Resultado:
{
    "polygon": [[x1,y1], [x2,y2], ...],
    "mask_area": 12450.5,  # pixels
    "bounding_box": {
        "x_min": 100,
        "y_min": 150,
        "x_max": 300,
        "y_max": 400
    }
}
```

---

### 5. Generación de Imagen Procesada

**Proceso de Dibujo:**

```python
# 1. Lee imagen original
image = cv2.imread(source_path)

# 2. Define colores por tipo de criadero (formato BGR)
COLORS = {
    'Basura': (0, 140, 255),           # Naranja
    'Charcos/Cumulo de agua': (255, 100, 0),  # Azul
    'Huecos': (0, 200, 0),             # Verde
    'Calles mal hechas': (0, 0, 255)  # Rojo
}

# 3. Por cada detección:
for detection in detections:
    # a) Dibuja polígono de segmentación
    polygon_points = detection['polygon']
    cv2.polylines(image, [polygon_points],
                  isClosed=True,
                  color=COLORS[detection['class']],
                  thickness=3)

    # b) Rellena con transparencia (30%)
    overlay = image.copy()
    cv2.fillPoly(overlay, [polygon_points],
                 color=COLORS[detection['class']])
    image = cv2.addWeighted(overlay, 0.3, image, 0.7, 0)

    # c) Agrega etiqueta con clase y confianza
    label = f"{detection['class']}: {detection['confidence']:.2f}"
    cv2.putText(image, label,
                (x_min, y_min - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6, COLORS[detection['class']], 2)

# 4. Guarda imagen procesada
output_path = 'processed/image_processed.jpg'
cv2.imwrite(output_path, image)

# 5. Convierte a Base64 para transferencia
with open(output_path, 'rb') as f:
    image_bytes = f.read()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
```

**Resultado Visual:**
```
Imagen original con:
- Polígonos de colores delineando criaderos
- Relleno semi-transparente del área detectada
- Etiquetas con tipo y confianza
- Colores distintivos por clase
```

---

### 6. Evaluación de Riesgo

**Algoritmo de Risk Assessment:**

```python
from sentrix_shared.risk_assessment import assess_dengue_risk

# Input: Lista de detecciones
detections = [
    {"class": "Charcos/Cumulo de agua", "confidence": 0.85},
    {"class": "Basura", "confidence": 0.75},
    {"class": "Huecos", "confidence": 0.65}
]

# Proceso:
# 1. Clasifica por nivel de riesgo
high_risk = ['Basura', 'Charcos/Cumulo de agua']
medium_risk = ['Huecos', 'Calles mal hechas']

# 2. Cuenta detecciones por nivel
high_risk_count = 2
medium_risk_count = 1

# 3. Aplica lógica de evaluación
if high_risk_count >= 3:
    overall_risk = 'ALTO'
elif high_risk_count >= 1 and medium_risk_count >= 3:
    overall_risk = 'ALTO'
elif high_risk_count >= 1:
    overall_risk = 'MEDIO'
elif medium_risk_count >= 3:
    overall_risk = 'MEDIO'
elif medium_risk_count >= 1:
    overall_risk = 'BAJO'
else:
    overall_risk = 'MINIMO'

# 4. Calcula risk score (0.0-1.0)
risk_score = (high_risk_count * 0.3 + medium_risk_count * 0.15)
```

**Output:**
```json
{
  "overall_risk_level": "ALTO",
  "risk_score": 0.75,
  "high_risk_sites": 2,
  "medium_risk_sites": 1,
  "total_detections": 3,
  "risk_distribution": {
    "ALTO": 2,
    "MEDIO": 1
  }
}
```

---

### 7. Response Final

**Estructura Completa de Respuesta:**

```json
{
  "analysis_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",

  "detections": [
    {
      "class_name": "Charcos/Cumulo de agua",
      "class_id": 2,
      "confidence": 0.853,
      "risk_level": "ALTO",

      "bounding_box": {
        "x_min": 100,
        "y_min": 150,
        "x_max": 300,
        "y_max": 400,
        "width": 200,
        "height": 250
      },

      "polygon": [
        [120, 160],
        [280, 165],
        [290, 380],
        [110, 390]
      ],

      "mask_area": 12450.5,

      "location": {
        "has_location": true,
        "latitude": -34.603722,
        "longitude": -58.381592,
        "coordinates": "-34.603722, -58.381592",
        "altitude_meters": 520.5,
        "gps_date": "2025-11-15T14:30:00Z",
        "location_source": "EXIF_GPS",

        "backend_integration": {
          "geo_point": "POINT(-58.381592 -34.603722)",
          "risk_level": "ALTO",
          "breeding_site_type": "Charcos/Cumulo de agua",
          "confidence_score": 0.853,
          "area_square_pixels": 12450.5,
          "requires_verification": true,

          "verification_urls": {
            "google_maps": "https://maps.google.com/?q=-34.603722,-58.381592",
            "google_earth": "https://earth.google.com/web/search/-34.603722,-58.381592"
          }
        }
      },

      "image_metadata": {
        "source_file": "IMG_20251115_143000.jpg",
        "camera_info": {
          "make": "Apple",
          "model": "iPhone 15 Pro",
          "capture_date": "2025-11-15T14:30:00Z"
        }
      }
    }
  ],

  "risk_assessment": {
    "overall_risk_level": "ALTO",
    "risk_score": 0.75,
    "high_risk_count": 2,
    "medium_risk_count": 1,
    "total_detections": 3,
    "risk_distribution": {
      "ALTO": 2,
      "MEDIO": 1
    }
  },

  "location": {
    "latitude": -34.603722,
    "longitude": -58.381592,
    "altitude": 520.5,
    "source": "EXIF_GPS",
    "gps_timestamp": "2025-11-15T14:30:00Z"
  },

  "processed_image": {
    "format": "jpeg",
    "base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "size_bytes": 245678,
    "encoding": "base64"
  },

  "processing_time_ms": 847,
  "model_version": "yolo11s-seg-dengue-v2.3",
  "confidence_threshold": 0.5,
  "device_used": "cuda"
}
```

---

## Características Técnicas

### Performance

**GPU (NVIDIA RTX 3050):**
- Tiempo de detección: 0.5-1s por imagen
- Throughput: 60-120 imágenes/minuto
- VRAM usage: ~2GB

**CPU (4 cores):**
- Tiempo de detección: 3-5s por imagen
- Throughput: 12-20 imágenes/minuto
- RAM usage: ~1GB

### Seguridad

**Validaciones:**
1. MIME type real (no solo extensión)
2. Tamaño máximo de archivo (50MB)
3. Rate limiting por IP
4. Sanitización de nombres
5. Limpieza automática de temporales
6. ThreadPoolExecutor para no bloquear

**Rate Limits:**
- 100 requests/hour por IP
- 10 requests/minute para detección

---

## Casos de Uso

### Caso 1: Imagen con GPS
```
Input: IMG_iPhone.jpg (con EXIF GPS)
↓
1. Extrae GPS: -34.603722, -58.381592
2. Detecta: 2 charcos, 1 basura
3. Genera imagen procesada con polígonos
4. Evalúa riesgo: ALTO
5. Response con ubicación completa
```

### Caso 2: Imagen sin GPS
```
Input: screenshot.png (sin EXIF)
↓
1. GPS: None (has_location: false)
2. Detecta: 1 hueco
3. Genera imagen procesada
4. Evalúa riesgo: BAJO
5. Response sin ubicación
```

### Caso 3: Sin Detecciones
```
Input: paisaje.jpg
↓
1. Extrae GPS (si tiene)
2. Detecta: 0 criaderos
3. No genera imagen procesada
4. Evalúa riesgo: MINIMO
5. Response con array vacío
```

---

## Integración con Shared Library

### Módulos Compartidos Usados:

**1. sentrix_shared.gps_utils:**
- `extract_image_gps()` - Extracción de coordenadas
- `get_image_camera_info()` - Info de cámara

**2. sentrix_shared.risk_assessment:**
- `assess_dengue_risk()` - Evaluación de riesgo

**3. sentrix_shared.data_models:**
- `CLASS_ID_TO_BREEDING_SITE` - Mapeo de clases
- `DetectionRiskEnum` - Enums de riesgo

---

## Referencias

- Documentación YOLOv11: https://docs.ultralytics.com/
- Especificación EXIF GPS: https://exiftool.org/TagNames/GPS.html
- OpenCV Documentation: https://docs.opencv.org/
- Backend Integration: ../backend/FUNCIONAMIENTO.md
- Scripts de entrenamiento: ./scripts/README.md
