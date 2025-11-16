# Scripts de Desarrollo y Utilidades - YOLO Service

Esta carpeta contiene scripts de utilidad para entrenamiento avanzado, evaluación de modelos, análisis de datasets y diagnóstico del servicio YOLO.

## Estructura

```
scripts/
├── training/        # Scripts avanzados de entrenamiento y análisis
├── diagnostics/     # Scripts de diagnóstico del sistema
└── testing/        # Scripts de testing y utilidades
```

---

## training/

Scripts para entrenamiento avanzado y análisis de datasets:

### analyze_dataset.py
Análisis comprehensivo del dataset de criaderos.

**Características:**
- Distribución de clases e índices de desbalance
- Estadísticas de calidad de imágenes
- Recomendaciones para split estratificado (k-fold)
- Estrategias de augmentación recomendadas

**Uso:**
```bash
cd scripts/training
python analyze_dataset.py --data ../../data --output analysis_report.json
```

### train_optimized.py
Script de entrenamiento avanzado con k-fold cross-validation.

**Características:**
- K-fold cross-validation para datasets pequeños
- Augmentación específica por clase (copy-paste para minoritarias)
- Learning rate scheduling dinámico (OneCycleLR, CosineAnnealing)
- Reproducibilidad con semilla global
- Logging de augmentación por batch
- Oversampling para clases minoritarias

**Uso:**
```bash
cd scripts/training
python train_optimized.py --model yolo11s-seg.pt --kfolds 5 --epochs 100 --batch 8
```

### evaluate_final.py
Evaluación avanzada de modelos entrenados.

**Características:**
- Métricas detalladas por clase
- Agregación de resultados k-fold
- Recomendaciones automáticas para recolección de datos
- Export JSON para tracking
- Análisis estadístico (media, std, intervalos de confianza)

**Uso:**
```bash
cd scripts/training
python evaluate_final.py --model ../../models/best.pt --data ../../data
```

---

## diagnostics/

Scripts para diagnóstico del sistema:

### diagnostic.py
Diagnóstico completo del sistema YOLO Service.

**Información proporcionada:**
- Hardware disponible (CPU, RAM, GPU)
- Versión de PyTorch y CUDA
- Modelos disponibles y ubicaciones
- Performance estimado por hardware
- Estado de dependencias

**Uso:**
```bash
cd scripts/diagnostics
python diagnostic.py
```

**Output ejemplo:**
```
YOLO Service System Diagnostic
Hardware: GPU (NVIDIA RTX 3050) - CUDA 11.8
Models: 3 found
- models/best.pt (42.3 MB)
- models/yolo11s-seg.pt (24.1 MB)
Estimated performance: 0.5-1s per image
```

---

## testing/

Scripts para testing y utilidades:

### test_new_model.py
Test rápido de modelo recién entrenado.

**Características:**
- Carga automática del último modelo entrenado
- Test con imágenes de prueba predefinidas
- Visualización rápida de resultados

**Uso:**
```bash
cd scripts/testing
python test_new_model.py
```

### utils.py
Funciones de utilidad compartidas.

**Contenido:**
- Helpers para procesamiento de imágenes
- Funciones de conversión de formatos
- Utilidades comunes entre scripts

---

## Notas Importantes

### Ejecutar desde raíz del proyecto
Para asegurar imports correctos, algunos scripts deben ejecutarse considerando el directorio raíz:

```bash
# Desde raíz del proyecto
cd /path/to/yolo-service
python scripts/training/train_optimized.py --epochs 100
```

### Requisitos
Todos los scripts requieren las dependencias listadas en `requirements.txt` del proyecto principal.

### Scripts vs CLI Principal
- Scripts en `scripts/`: Herramientas avanzadas de desarrollo y análisis
- `train_simple.py` (raíz): Script de entrenamiento estándar recomendado
- `main.py` (raíz): CLI para detección y operaciones básicas
- `server.py` (raíz): Servidor FastAPI de producción

---

## Workflows Comunes

### Workflow de Entrenamiento Avanzado

```bash
# 1. Analizar dataset
python scripts/training/analyze_dataset.py

# 2. Entrenamiento con k-fold
python scripts/training/train_optimized.py --kfolds 5 --epochs 100

# 3. Evaluar resultados
python scripts/training/evaluate_final.py

# 4. Test rápido
python scripts/testing/test_new_model.py
```

### Diagnóstico del Sistema

```bash
# Verificar configuración antes de entrenar
python scripts/diagnostics/diagnostic.py

# Verificar que todo está OK para producción
python scripts/diagnostics/diagnostic.py > system_check.txt
```

---

## Referencias

- Script de entrenamiento estándar: `../train_simple.py`
- Servidor de producción: `../server.py`
- CLI principal: `../main.py`
- Documentación YOLOv11: https://docs.ultralytics.com/
