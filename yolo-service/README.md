# Sentrix YOLO Service - Core de Detección IA

Servicio central de inteligencia artificial para la detección automatizada de criaderos de *Aedes aegypti* como parte de la plataforma integral Sentrix.

## Descripción

Este servicio constituye el **núcleo de IA** de la plataforma Sentrix, proporcionando capacidades avanzadas de visión por computadora para la detección y segmentación de sitios potenciales de reproducción del mosquito *Aedes aegypti*. Utiliza modelos YOLOv11 optimizados para identificar y analizar:

- **Basura** - Nivel de riesgo medio
- **Calles deterioradas** - Nivel de riesgo alto
- **Acumulaciones de agua** - Nivel de riesgo alto
- **Huecos y depresiones** - Nivel de riesgo alto

## Características Principales

### Core de IA
- **Modelos YOLOv11** optimizados para detección de criaderos de vectores
- **Segmentación de instancias** con precisión a nivel de pixel
- **Múltiples arquitecturas** (nano, small, medium, large, xlarge)
- **Selección automática** de modelo según capacidades de hardware

### Evaluación de Riesgo
- **Algoritmo epidemiológico** para clasificación de riesgo por zona
- **Análisis contextual** de tipos de criaderos detectados
- **Métricas de confianza** y precisión por detección
- **Reportes estructurados** en formato JSON para integración

### Optimización y Rendimiento
- **Aceleración GPU** automática con CUDA
- **Procesamiento por lotes** para análisis masivo de imágenes
- **Arquitectura modular** para fácil mantenimiento y escalabilidad
- **Paths portables** - funciona en cualquier sistema sin modificaciones

### Interfaces de Uso
- **CLI avanzado** con subcomandos intuitivos para diferentes flujos de trabajo
- **API programática** para integración con aplicaciones externas
- **Detección automática** de formato de entrada (imagen individual, directorio, video)
- **Validación de entrada** con manejo robusto de errores

## Instalación

### Requisitos del sistema

- Python 3.8 o superior
- CUDA 11.8+ (requerido para aceleración GPU)
- RAM: 4GB mínimo, 8GB recomendado
- Espacio en disco: 2GB para modelos y dependencias

### Instalación de dependencias

```bash
pip install -r requirements.txt
```

**Nota**: Para entornos con GPU NVIDIA, verificar que las versiones de PyTorch sean compatibles con la versión de CUDA instalada.

## Estructura del Servicio

```
yolo-service/
├── src/                       # Código fuente modular
│   ├── core/                  # Funcionalidades principales de IA
│   │   ├── trainer.py         # Entrenamiento de modelos YOLO
│   │   ├── detector.py        # Detección de criaderos
│   │   └── evaluator.py       # Evaluación de riesgo epidemiológico
│   ├── utils/                 # Utilidades del sistema
│   │   ├── device.py          # Detección automática GPU/CPU
│   │   ├── file_ops.py        # Operaciones de archivos portables
│   │   ├── model_utils.py     # Gestión de modelos YOLO
│   │   └── paths.py           # Paths automáticos multiplataforma
│   └── reports/               # Generación de reportes
│       └── generator.py       # Reportes JSON estructurados
├── configs/                   # Configuración del servicio
│   ├── classes.py            # Definición de clases y niveles de riesgo
│   └── dataset.yaml          # Configuración del dataset YOLO
├── data/                     # Dataset de entrenamiento
│   ├── images/               # Imágenes organizadas por split
│   │   ├── train/            # Imágenes de entrenamiento (57)
│   │   ├── val/              # Imágenes de validación (16)
│   │   └── test/             # Imágenes de prueba
│   └── labels/               # Anotaciones en formato YOLO
│       ├── train/            # Etiquetas de entrenamiento
│       ├── val/              # Etiquetas de validación
│       └── test/             # Etiquetas de prueba
├── models/                   # Modelos entrenados y experimentos
│   ├── test_nano/            # Experimento YOLO11n-seg
│   ├── test_small/           # Experimento YOLO11s-seg (óptimo)
│   ├── test_medium/          # Experimento YOLO11m-seg
│   ├── test_large/           # Experimento YOLO11l-seg
│   └── test_xlarge/          # Experimento YOLO11x-seg
├── scripts/                  # Scripts especializados
│   ├── train_dengue_model.py # Entrenamiento con selección automática
│   ├── batch_detection.py    # Procesamiento por lotes
│   ├── predict_new_images.py # Predicción en imágenes nuevas
│   └── cleanup_failed_runs.py # Limpieza de entrenamientos fallidos
├── tests/                    # Suite de pruebas
│   ├── unit/                 # Tests unitarios por módulo
│   ├── integration/          # Tests de integración
│   ├── test_unified.py       # Suite completa del sistema
│   └── test_complete_system.py # Validación de pipeline completo
├── predictions/              # Outputs de detección
├── results/                  # Resultados de entrenamiento
├── test_images/              # Imágenes de prueba manual
├── main.py                   # CLI principal con subcomandos
├── requirements.txt          # Dependencias Python
└── .gitignore               # Archivos excluidos del repositorio
```

## Uso del sistema

### CLI Principal (Nuevo)

El proyecto ahora incluye un CLI moderno con subcomandos:

#### 1. Entrenamiento
```bash
# Entrenamiento básico
python main.py train --model yolo11n-seg.pt --epochs 100

# Con nombre personalizado
python main.py train --model yolo11s-seg.pt --epochs 200 --name "experimento_final"

# Usando configuración personalizada
python main.py train --model yolo11m-seg.pt --data configs/custom_dataset.yaml
```

#### 2. Detección
```bash
# Detectar en una imagen
python main.py detect --model models/best.pt --source image.jpg

# Con umbral de confianza personalizado
python main.py detect --model models/best.pt --source image.jpg --conf 0.6
```

#### 3. Generación de reportes
```bash
# Generar reporte completo
python main.py report --model models/best.pt --source image.jpg --output results/reporte.json
```

### Scripts especializados

#### Entrenamiento con selección automática de modelo
```bash
# Selección automática según GPU
python scripts/train_dengue_model.py --auto --epochs 100

# Entrenamiento con modelo específico
python scripts/train_dengue_model.py --model s --epochs 100

# Nomenclatura personalizada
python scripts/train_dengue_model.py --auto --epochs 100 --name "experimento_final_v2"
```

#### Detección por lotes
```bash
python scripts/batch_detection.py --model models/best.pt --source path/to/images/ --output results/
```

#### Predicción en imágenes nuevas
```bash
# Directorio completo
python scripts/predict_new_images.py --model models/best.pt --source test_images

# Imagen específica con umbral personalizado
python scripts/predict_new_images.py --model models/best.pt --source test_images/foto.jpg --conf 0.5
```

### Uso programático

```python
from src.core import train_dengue_model, detect_breeding_sites, assess_dengue_risk
from src.reports import generate_report, save_report

# Entrenar modelo
results = train_dengue_model(
    model_path='yolo11n-seg.pt',
    epochs=100
)

# Detectar criaderos
detections = detect_breeding_sites(
    model_path='models/best.pt',
    source='image.jpg',
    conf_threshold=0.5
)

# Evaluar riesgo
risk = assess_dengue_risk(detections)

# Generar reporte
report = generate_report('image.jpg', detections)
save_report(report)
```

## Características de portabilidad

### Paths automáticos
El sistema ahora utiliza **paths automáticos** que se adaptan a cualquier PC:

```python
from src.utils import get_models_dir, get_data_dir, get_configs_dir

# Estos paths se calculan automáticamente
models_dir = get_models_dir()      # {proyecto}/models/
data_dir = get_data_dir()          # {proyecto}/data/
configs_dir = get_configs_dir()    # {proyecto}/configs/
```

### Despliegue simple
1. **Copia la carpeta completa** del proyecto a cualquier ubicación
2. **Instala dependencias**: `pip install -r requirements.txt`
3. **Ejecuta directamente** - no requiere modificar paths

### Compatibilidad multiplataforma
- ✅ **Windows**: `C:\ruta\al\proyecto\`
- ✅ **Linux**: `/ruta/al/proyecto/`
- ✅ **macOS**: `/ruta/al/proyecto/`

## Detección y Evaluación de Riesgo

### Clases de Criaderos Detectados

| ID | Clase | Nivel de Riesgo | Descripción Epidemiológica |
|----|-------|----------------|---------------------------|
| 0 | Basura | MEDIO | Acumulación de desechos con potencial de retención de agua |
| 1 | Calles deterioradas | ALTO | Superficies irregulares que facilitan formación de charcos |
| 2 | Acumulaciones de agua | ALTO | Agua estancada visible, hábitat directo de reproducción |
| 3 | Huecos y depresiones | ALTO | Cavidades que retienen agua de lluvia |

### Algoritmo de Evaluación de Riesgo Epidemiológico

El servicio implementa un algoritmo de clasificación de riesgo basado en criterios epidemiológicos establecidos:

- **ALTO**: ≥3 sitios de riesgo alto, o ≥1 sitio alto + ≥3 sitios medio
- **MEDIO**: ≥1 sitio de riesgo alto, o ≥3 sitios de riesgo medio
- **BAJO**: ≥1 sitio de riesgo medio
- **MÍNIMO**: Sin sitios de riesgo detectados

### Integración con Plataforma Sentrix

Este servicio está diseñado para integrarse con los otros componentes de Sentrix:

- **Backend API**: Recibe resultados vía endpoints REST para almacenamiento geoespacial
- **Frontend Web**: Visualiza detecciones en mapas interactivos y dashboards
- **Análisis Ambiental**: Combina resultados con datos meteorológicos para índices contextuales
- **Participación Ciudadana**: Procesa imágenes cargadas manualmente por usuarios

## Configuración

### Dataset automático
El sistema utiliza configuración automática de paths:

```python
# Se resuelve automáticamente a:
# {proyecto}/configs/dataset.yaml
```

### Configuración del dataset (configs/dataset.yaml)
```yaml
# Los paths ahora son relativos al proyecto
path: ./data
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

### Prevención de carpetas duplicadas

El sistema ahora **evita crear múltiples carpetas** durante el entrenamiento:
- ✅ **Una carpeta por día**: `dengue_seg_s_100ep_20250917`
- ✅ **Reutilización automática** si entrenas varias veces
- ✅ **Sin carpetas vacías** o duplicadas

## Formato de salida

### Reporte de detección (JSON)
```json
{
  "source": "image.jpg",
  "total_detections": 3,
  "timestamp": "2025-01-17T10:30:00",
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
      "Intervención inmediata requerida",
      "Eliminar agua estancada inmediatamente"
    ]
  }
}
```

## Validación del sistema

### Ejecución de tests completos
```bash
# Tests usando nueva estructura modular
python tests/test_unified.py

# Tests específicos
python -m pytest tests/unit/
python -m pytest tests/integration/
```

**Tests incluidos:**
- Verificación de compatibilidad de hardware (CPU/GPU)
- Validación de carga y funcionamiento de modelos YOLO
- Comprobación de funciones de evaluación de riesgo
- Tests de integridad del pipeline completo
- **Nuevo**: Test de prevención de carpetas múltiples

## Solución de problemas comunes

### Verificación de compatibilidad GPU
```python
from src.utils import get_system_info

info = get_system_info()
print(f"CUDA disponible: {info['cuda_available']}")
print(f"GPUs: {info['device_count']}")
```

### Problemas de paths
El sistema ahora maneja automáticamente los paths, pero si necesitas verificar:

```python
from src.utils import get_project_root, get_models_dir

print(f"Raíz del proyecto: {get_project_root()}")
print(f"Directorio de modelos: {get_models_dir()}")
```

### Migración desde versión anterior
Si tienes una versión anterior:

1. **Backup**: Guarda `main.py` como `main_legacy.py` (ya incluido)
2. **Actualiza imports**: Usa `from src.core import ...` en lugar de `from main import ...`
3. **Tests**: Ejecuta `python tests/test_unified.py` para verificar compatibilidad

## Información del Servicio

### Arquitectura y Beneficios
- **Separación de responsabilidades**: Cada módulo tiene una función específica
- **Mantenibilidad**: Código modular fácil de modificar y extender
- **Testabilidad**: Tests organizados por funcionalidad con cobertura completa
- **Portabilidad**: Paths automáticos multiplataforma sin configuración
- **Escalabilidad**: Diseñado para integrarse con sistemas más grandes
- **Interoperabilidad**: API estándar para comunicación con otros servicios

### Contexto en el Proyecto Sentrix
Este servicio YOLO constituye la **Fase 1** del proyecto de investigación Sentrix, completada exitosamente. Proporciona la base de IA para:

- **Procesamiento de imágenes** aéreas (drones) y terrestres (usuarios)
- **Detección automatizada** de criaderos con alta precisión
- **Evaluación de riesgo** epidemiológico contextualizado
- **Integración futura** con análisis ambiental y participación ciudadana

### Limitaciones y Consideraciones
- **Herramienta de apoyo**: Los resultados requieren validación por especialistas en salud pública
- **Especificidad geográfica**: Modelo entrenado con datos regionales específicos
- **Dependencia ambiental**: Rendimiento variable según iluminación y condiciones climáticas
- **Dataset limitado**: Entrenado con 73 imágenes (expandible en futuras versiones)
- **Validación en campo**: Resultados deben compararse con inspecciones manuales

## Especificaciones de rendimiento

### Configuraciones de hardware recomendadas

| Componente | Mínimo | Recomendado | Óptimo |
|------------|--------|-------------|--------|
| **GPU** | GPU Básica (4GB) | GPU Media (6GB) | GPU Alta (10GB+) |
| **CPU** | CPU Básico | CPU Medio | CPU Alto |
| **RAM** | 4GB | 8GB | 16GB+ |
| **Almacenamiento** | 5GB libres | 10GB libres | SSD recomendado |

### Métricas de Rendimiento por Modelo

Basado en experimentos con GPU moderna y dataset de 73 imágenes:

| Modelo | Parámetros | mAP50 | mAP50-95 | GPU Memory | Velocidad | Recomendación |
|--------|------------|-------|----------|------------|-----------|---------------|
| **YOLO11n-seg** | 2.8M | 0.118 | 0.076 | 0.6GB | 8.9 it/s | Recursos limitados |
| **YOLO11s-seg** | 10M | **0.258** | **0.137** | **1.0GB** | **8.6 it/s** | **Óptimo** |
| **YOLO11m-seg** | 22M | 0.250 | 0.118 | 1.8GB | 6.5 it/s | Alto rendimiento |
| **YOLO11l-seg** | 28M | 0.134 | 0.087 | 2.3GB | 5.3 it/s | GPU potente |
| **YOLO11x-seg** | 62M | 0.190 | 0.090 | 4.0GB | 3.2 it/s | Investigación |

**Recomendación**: YOLO11s-seg ofrece el mejor balance rendimiento/recursos para implementación en producción.

### Tiempos de Operación Típicos

| Operación | GPU Moderna | CPU Medio | Descripción |
|-----------|----------------|----------|-------------|
| **Entrenamiento** (5 epochs) | 5-15 minutos | 2-4 horas | Según modelo seleccionado |
| **Inferencia** (imagen 640px) | 15-50ms | 200-600ms | Detección + segmentación |
| **Lote** (100 imágenes) | 10-30 segundos | 30-90 segundos | Procesamiento masivo |

---

**Versión**: 2.0.0 - Core IA de la Plataforma Sentrix
**Estado**: Fase 1 Completa - Integración con Backend/Frontend en desarrollo
**Cronograma**: Julio-Agosto 2024 (Completado) | Septiembre-Octubre 2024 (Integración)
**Última actualización**: Enero 2025