# YOLO Dengue Detection Service

Sistema automatizado de deteccion de criaderos de dengue mediante YOLOv11 con segmentacion de instancias.

## Descripcion

Sistema de vision por computadora diseñado para la deteccion y clasificacion automatica de sitios potenciales de reproduccion del mosquito Aedes aegypti, vector principal de dengue, chikungunya y zika. Implementa el modelo YOLOv11 con segmentacion de instancias para identificar y segmentar:

- **Basura** - Nivel de riesgo medio
- **Calles deterioradas** - Nivel de riesgo alto  
- **Acumulaciones de agua** - Nivel de riesgo alto
- **Huecos y depresiones** - Nivel de riesgo alto

## Caracteristicas principales

- **Segmentacion de instancias** con precisión a nivel de pixel
- **Evaluacion automatica de riesgo epidemiologico** basada en criterios establecidos
- **Generacion de reportes estructurados** en formato JSON
- **Deteccion automatica de GPU/CPU** para optimizacion de rendimiento
- **Procesamiento por lotes** para analisis de multiples imagenes
- **Seleccion inteligente de modelos** segun capacidades de hardware
- **Nomenclatura automatica de experimentos** con timestamp y configuracion

## Instalacion

### Requisitos del sistema

- Python 3.8 o superior
- CUDA 11.8+ (requerido para aceleracion GPU)
- RAM: 4GB minimo, 8GB recomendado
- Espacio en disco: 2GB para modelos y dependencias

### Instalacion de dependencias

```bash
pip install -r requirements.txt
```

**Nota**: Para entornos con GPU NVIDIA, verificar que las versiones de PyTorch sean compatibles con la version de CUDA instalada.

## Estructura del proyecto

```
yolo-service/
├── configs/           # Configuraciones del modelo y dataset
│   ├── classes.py     # Definicion de clases y niveles de riesgo
│   └── dataset.yaml   # Configuracion del dataset YOLO
├── data/              # Dataset de imagenes y anotaciones
│   ├── images/        # Imagenes del dataset
│   └── labels/        # Anotaciones en formato YOLO
├── models/            # Modelos entrenados
├── results/           # Resultados y reportes
├── scripts/           # Scripts de entrenamiento y deteccion
│   ├── train_dengue_model.py
│   └── batch_detection.py
├── tests/             # Tests unificados
│   └── test_unified.py # Tests completos del sistema
├── main.py            # Modulo principal con funciones core
├── utils.py           # Funciones utilitarias compartidas
└── requirements.txt   # Dependencias esenciales
```

## Uso del sistema

### 1. Entrenamiento de modelos

#### Seleccion automatica de modelo (recomendado)
```bash
python scripts/train_dengue_model.py --auto --epochs 100
```
El sistema selecciona automaticamente el modelo optimo segun las capacidades de hardware disponibles.

#### Entrenamiento con modelo especifico
```bash
# Modelo Small (equilibrio velocidad/precision)
python scripts/train_dengue_model.py --model s --epochs 100

# Modelo Large (maxima precision)  
python scripts/train_dengue_model.py --model l --epochs 100
```

#### Nomenclatura personalizada de experimentos
```bash
python scripts/train_dengue_model.py --auto --epochs 100 --name "experimento_final_v2"
```

**Formato automatico**: `dengue_seg_{tamaño}_{epocas}ep_{fecha}_{hora}`  
**Ejemplo**: `models/dengue_seg_s_100ep_20250111_1430/`

### 2. Deteccion en imagenes

#### Deteccion individual:
```python
from main import detect_breeding_sites, generate_report, save_report

# Detectar criaderos en una imagen
detections = detect_breeding_sites(
    model_path='models/best.pt',
    source='path/to/image.jpg',
    conf_threshold=0.5
)

# Generar y guardar reporte
report = generate_report('path/to/image.jpg', detections)
save_report(report, 'results/detection_report.json')
```

#### Deteccion por lotes:
```bash
python scripts/batch_detection.py --model models/best.pt --source path/to/images/ --output results/
```

### 3. Evaluacion de riesgo

```python
from main import assess_dengue_risk

# Evaluar riesgo epidemiologico
risk_assessment = assess_dengue_risk(detections)
print(f"Nivel de riesgo: {risk_assessment['level']}")
print(f"Recomendaciones: {risk_assessment['recommendations']}")
```

## Clasificacion y evaluacion de riesgo

### Clases de deteccion

| ID | Clase | Nivel de Riesgo | Descripcion epidemiologica |
|----|-------|----------------|---------------------------|
| 0 | Basura | MEDIO | Acumulacion de desechos con potencial de retencion de agua |
| 1 | Calles deterioradas | ALTO | Superficies irregulares que facilitan formacion de charcos |
| 2 | Acumulaciones de agua | ALTO | Agua estancada visible, habitat directo de reproduccion |
| 3 | Huecos y depresiones | ALTO | Cavidades que retienen agua de lluvia |

### Algoritmo de evaluacion de riesgo epidemiologico

**ALTO**: ≥3 sitios de riesgo alto, o ≥1 sitio alto + ≥3 sitios medio  
**MEDIO**: ≥1 sitio de riesgo alto, o ≥3 sitios de riesgo medio  
**BAJO**: ≥1 sitio de riesgo medio  
**MINIMO**: Sin sitios de riesgo detectados

## Configuracion

### Dataset (configs/dataset.yaml)
```yaml
path: C:\Users\manolo\Documents\Tesis\yolo-service\data
train: images/train
val: images/val
test: images/test

names:
  0: Basura
  1: Calles mal hechas
  2: Charcos/Cumulo de agua
  3: Huecos

task: segment
nc: 4
```

### Hiperparametros de entrenamiento
- **Epochs**: 100 (con early stopping patience=50)
- **Batch size**: 1 (ajustable segun GPU)
- **Image size**: 640x640
- **Learning rate**: 0.001
- **Weight decay**: 0.001
- **Data augmentation**: Mosaic (0.5), Copy-paste (0.3)

## Formato de salida

### Reporte de deteccion (JSON)
```json
{
  "source": "image.jpg",
  "total_detections": 3,
  "timestamp": "2024-01-15T10:30:00",
  "detections": [
    {
      "class": "Charcos/Cumulo de agua",
      "class_id": 2,
      "confidence": 0.87,
      "polygon": [[x1,y1], [x2,y2], ...],
      "mask_area": 1250.5
    }
  ],
  "risk_assessment": {
    "level": "ALTO",
    "high_risk_sites": 2,
    "medium_risk_sites": 1,
    "recommendations": [
      "Intervencion inmediata requerida",
      "Eliminar agua estancada inmediatamente"
    ]
  }
}
```

## Validacion del sistema

### Ejecucion de tests completos
```bash
python tests/test_unified.py
```

**Tests incluidos:**
- Verificacion de compatibilidad de hardware (CPU/GPU)
- Validacion de carga y funcionamiento de modelos YOLO
- Comprobacion de funciones de evaluacion de riesgo
- Tests de integridad del pipeline completo

## Especificaciones de rendimiento

### Configuraciones de hardware recomendadas

| Componente | Minimo | Recomendado | Optimo |
|------------|--------|-------------|--------|
| **GPU** | GTX 1050 (4GB) | GTX 1660 Ti (6GB) | RTX 3080+ (10GB+) |
| **CPU** | Intel i3 / AMD R3 | Intel i5 / AMD R5 | Intel i7 / AMD R7 |
| **RAM** | 4GB | 8GB | 16GB+ |
| **Almacenamiento** | 5GB libres | 10GB libres | SSD recomendado |

### Metricas de rendimiento aproximadas

| Operacion | GPU (GTX 1660 Ti) | CPU (i5) |
|-----------|-------------------|----------|
| **Entrenamiento** (100 epochs) | 2-3 horas | 12-24 horas |
| **Inferencia** (por imagen) | 50-100ms | 300-800ms |
| **Procesamiento por lotes** (100 imagenes) | 8-15 segundos | 45-120 segundos |

## Solucion de problemas comunes

### Verificacion de compatibilidad GPU
```python
import torch
print(f"CUDA disponible: {torch.cuda.is_available()}")
print(f"Version CUDA: {torch.version.cuda}")
print(f"Dispositivos GPU: {torch.cuda.device_count()}")
```

### Problemas de configuracion del dataset
- Verificar estructura de directorios en `data/images/` y `data/labels/`
- Confirmar que `configs/dataset.yaml` contiene rutas validas
- Asegurar que las anotaciones esten en formato YOLO

### Errores de memoria durante entrenamiento
- Reducir el parametro `--batch` (valor por defecto: 1)
- Utilizar modelos de menor tamaño (nano o small)
- Verificar memoria GPU disponible con `nvidia-smi`

## Informacion del proyecto

### Proposito academico
Este sistema ha sido desarrollado como parte de una investigacion academica enfocada en la aplicacion de tecnicas de vision por computadora para la vigilancia epidemiologica automatizada de vectores de dengue.

### Limitaciones y consideraciones
- **Uso como herramienta de apoyo**: Los resultados deben ser validados por personal especializado en salud publica
- **Contexto geografico**: El modelo ha sido entrenado con datos especificos y puede requerir adaptacion para diferentes regiones
- **Condiciones ambientales**: El rendimiento puede variar segun condiciones de iluminacion, clima y calidad de imagen

### Estructura de archivos generados
```
models/
├── experimento_nombre/
│   ├── weights/
│   │   ├── best.pt          # Modelo con mejores metricas
│   │   └── last.pt          # Ultimo checkpoint
│   ├── results.png          # Graficas de entrenamiento
│   ├── confusion_matrix.png # Matriz de confusion
│   └── args.yaml           # Configuracion utilizada
```

**Nota tecnica**: El sistema implementa limpieza automatica de archivos temporales generados durante el proceso de entrenamiento para mantener la organizacion del proyecto.