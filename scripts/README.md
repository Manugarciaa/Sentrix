# Scripts de Utilidad - Sentrix

Esta carpeta contiene scripts de utilidad creados durante el desarrollo, mantenimiento y testing del proyecto Sentrix. Incluye tanto herramientas de corrección de código como scripts de verificación y testing del sistema.

## Contenido

### `comprehensive_fix_imports.py`
**Propósito:** Script principal para corregir errores de importación en todo el proyecto.

**Funcionalidad:**
- Analiza 123+ archivos Python en todo el proyecto
- Corrige patrones de import incorrectos automáticamente
- Convierte imports absolutos a relativos donde corresponde
- Maneja casos especiales para entry points vs módulos

**Uso:**
```bash
python scripts/comprehensive_fix_imports.py
```

**Resultado:** Aplicó 29 correcciones críticas que solucionaron los errores de importación masivos.

---

### `fix_entry_points.py`
**Propósito:** Corrección específica para archivos de entry point que requieren imports absolutos.

**Funcionalidad:**
- Identifica entry points: `server.py`, `main.py`, scripts de batch
- Convierte imports relativos problemáticos a absolutos
- Soluciona el error "attempted relative import beyond top-level package"

**Archivos objetivo:**
- `yolo-service/scripts/batch_detection.py`
- `yolo-service/scripts/predict_new_images.py`
- `yolo-service/scripts/train_dengue_model.py`

---

### `fix_api_routers.py`
**Propósito:** Solución específica para problemas de imports en routers de la API.

**Funcionalidad:**
- Corrige imports en `backend/src/api/v1/auth.py`
- Corrige imports en `backend/src/api/v1/reports.py`
- Maneja casos donde los módulos existen pero los imports relativos fallan

---

### `fix_imports.py`
**Propósito:** Script inicial de corrección de imports (versión temprana).

**Funcionalidad:**
- Primera versión del sistema de corrección de imports
- Funcionalidad básica para patrones comunes
- Evolucionó hacia `comprehensive_fix_imports.py`

---

### `simple_test.py`
**Propósito:** Pruebas básicas de funcionalidad del sistema completo.

**Funcionalidad:**
- Verifica importación correcta de shared library
- Prueba generación de nomenclatura estandarizada
- Valida servicios del backend (AnalysisService, SupabaseManager)
- Verifica workflow completo de análisis

**Uso:**
```bash
python scripts/simple_test.py
```

**Resultado:** Suite de 4 tests que verifican funcionalidad básica del sistema.

---

### `quick_smoke_tests.py`
**Propósito:** Verificación rápida de componentes críticos del sistema.

**Funcionalidad:**
- Tests de importación de módulos principales
- Verificación de generación y parsing de nombres de archivos
- Pruebas de detección de formatos de imagen
- Validación de creación de clientes (Supabase, YOLO, Analysis Service)
- Tests de variaciones de nombres de archivos

**Uso:**
```bash
python scripts/quick_smoke_tests.py
```

**Cobertura:** 7 tests que verifican componentes básicos funcionando correctamente.

---

### `test_deduplication.py`
**Propósito:** Pruebas específicas del sistema de deduplicación de imágenes.

**Funcionalidad:**
- Verifica cálculo de firmas de contenido (SHA-256, MD5)
- Prueba detección de duplicados por contenido
- Valida sistema de scoring por similitud de metadatos
- Tests de estimación de ahorro de storage
- Verificación de integración con AnalysisService

**Uso:**
```bash
python scripts/test_deduplication.py
```

**Resultado:** Suite especializada para validar prevención de overflow de storage.

---

## Scripts de Corrección de Código

---

### `comprehensive_fix_imports.py`
**Propósito:** Script principal para corregir errores de importación en todo el proyecto.

**Funcionalidad:**
- Analiza 123+ archivos Python en todo el proyecto
- Corrige patrones de import incorrectos automáticamente
- Convierte imports absolutos a relativos donde corresponde
- Maneja casos especiales para entry points vs módulos

**Uso:**
```bash
python scripts/comprehensive_fix_imports.py
```

**Resultado:** Aplicó 29 correcciones críticas que solucionaron los errores de importación masivos.

---

## Resultado del Proceso de Corrección y Testing

**Estado inicial:** 123 archivos con errores de importación masivos
**Estado final:** Proyecto completamente funcional con funcionalidades avanzadas

**Servicios verificados como funcionando:**
- Backend (Puerto 8000) - Con nomenclatura estandarizada y deduplicación
- YOLO Service (Puerto 8001) - Con generación de imágenes procesadas
- Frontend (Puerto 3000) - Con visualización dual de imágenes
- Shared Library - Sistema completo de gestión inteligente de archivos

**Testing implementado:**
- Tests básicos de funcionalidad (simple_test.py)
- Smoke tests de componentes críticos (quick_smoke_tests.py)
- Tests específicos de deduplicación (test_deduplication.py)
- Cobertura completa de nuevas funcionalidades

## Notas Técnicas

### Patrones Corregidos:
```python
# Antes (Problemático)
from src.core import train_dengue_model
from app.database import get_db
from backend.src.utils import validate_file

# Después (Correcto)
from ..core import train_dengue_model  # Para módulos
from src.core import train_dengue_model  # Para entry points
from ...database.connection import get_db  # Para API routers
```

### Principios Aplicados:
1. **Entry Points** = Imports absolutos (desde src/)
2. **Módulos internos** = Imports relativos (.., ..., etc.)
3. **API Routers** = Imports relativos profundos (...modules)

## Scripts de Testing y Validación

### Flujo de Testing Recomendado:
```bash
# 1. Verificación rápida de componentes básicos
python scripts/quick_smoke_tests.py

# 2. Tests completos de funcionalidad
python scripts/simple_test.py

# 3. Validación específica de deduplicación
python scripts/test_deduplication.py
```

### Cobertura de Testing:
- **Importaciones**: Verificación de módulos críticos
- **Nomenclatura**: Sistema estandarizado de archivos
- **Deduplicación**: Prevención de overflow de storage
- **Servicios**: Backend, YOLO, y Supabase clients
- **Workflow**: Flujo completo de análisis de imágenes

### Métricas de Calidad:
- **Tests de humo**: 7 verificaciones críticas
- **Tests básicos**: 4 validaciones de funcionalidad
- **Tests especializados**: 2 verificaciones de deduplicación
- **Tiempo de ejecución**: < 3 segundos por suite

---

## Evolución del Proyecto

### Fase 1: Corrección de Errores
Scripts para solucionar errores masivos de importación y hacer el proyecto funcional.

### Fase 2: Funcionalidades Avanzadas
Implementación de nomenclatura estandarizada, deduplicación y almacenamiento dual.

### Fase 3: Testing y Validación
Scripts para verificar y validar todas las funcionalidades implementadas.

---

*Estos scripts fueron fundamentales para transformar el proyecto de un estado con errores masivos a un sistema completamente funcional con gestión inteligente de imágenes para la tesis académica.*