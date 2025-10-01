# Sentrix - Detección IA de Criaderos de Aedes aegypti

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![YOLO v11](https://img.shields.io/badge/YOLO-v11-brightgreen.svg)](https://github.com/ultralytics/ultralytics)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

Plataforma de inteligencia artificial para la detección automatizada de criaderos de mosquitos del dengue usando visión por computadora, evaluación de riesgo epidemiológico y sistema avanzado de gestión de imágenes.

## Descripción

Sistema completo de detección de sitios de reproducción de *Aedes aegypti* que combina:

- **Detección IA** - Modelos YOLOv11 para identificar criaderos en imágenes
- **Evaluación de riesgo** - Algoritmos epidemiológicos para clasificación automática
- **API REST** - Backend completo con base de datos PostgreSQL
- **Geolocalización** - Extracción automática de coordenadas GPS desde metadatos EXIF
- **Gestión Inteligente de Imágenes** - Sistema de nomenclatura estandarizada y deduplicación automática
- **Almacenamiento Dual** - Imágenes originales y procesadas con marcadores de detección

## Arquitectura

```
sentrix/
├── backend/                # API REST (puerto 8000)
├── yolo-service/           # Detección IA (puerto 8001)
├── shared/                 # Librería compartida
├── frontend/               # Interfaz web React (puerto 3000)
└── scripts/                # Scripts de configuración
```

## Inicio Rápido

### 1. Configuración del Entorno

```bash
# Configurar variables de entorno
python scripts/setup-env.py

# Editar configuración
cp .env.example .env
```

### 2. Ejecutar Servicios

**Opción A: Script Automático (Recomendado)**
```powershell
# Ejecutar script de inicio automático (Windows)
.\start-all.ps1
```

**Opción B: Manual**
```bash
# Terminal 1: Backend API (puerto 8000)
cd backend && python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Servicio YOLO (puerto 8001)
cd yolo-service && python server.py

# Terminal 3: Frontend React (puerto 3000/3001)
cd frontend && npm run dev
```

### 3. Probar Detección

```bash
# API completa con almacenamiento
curl -X POST "http://localhost:8000/api/v1/analyses" \
  -F "file=@imagen.jpg" \
  -F "confidence_threshold=0.5"

# Detección directa YOLO
curl -X POST "http://localhost:8001/detect" \
  -F "file=@imagen.jpg"
```

## Capacidades de Detección

| Tipo de Criadero | Nivel de Riesgo | Descripción |
|------------------|-----------------|-------------|
| **Basura** | Medio | Acumulación de residuos con retención de agua |
| **Calles deterioradas** | Alto | Superficies irregulares que forman charcos |
| **Acumulaciones de agua** | Alto | Agua estancada visible, hábitat directo |
| **Huecos/depresiones** | Alto | Cavidades que retienen agua de lluvia |

## Funcionalidades Avanzadas

### Sistema de Nomenclatura Estandarizada
```
SENTRIX_YYYYMMDD_HHMMSS_DEVICE_LOCATION_ID.ext
```
- **Fecha/Hora**: Timestamp del análisis en formato ISO
- **Dispositivo**: Detección automática desde EXIF (IPHONE15, SAMSUNG, etc.)
- **Ubicación**: Codificación GPS (LATn34p604_LONn58p382) o NOLOC
- **ID único**: Hash de 8 caracteres para evitar colisiones

### Almacenamiento Dual Inteligente
- **Imagen Original**: Archivo sin modificaciones para análisis futuro
- **Imagen Procesada**: Con marcadores azules de detecciones YOLO
- **Nomenclatura Diferenciada**: Prefijos `original_` y `processed_`

### Sistema de Deduplicación
- **Detección por Contenido**: Hash SHA-256 de datos binarios
- **Scoring de Similitud**: Metadatos de cámara y ubicación GPS
- **Almacenamiento Referencial**: Duplicados no almacenan archivos físicos
- **Optimización Automática**: Ahorro de espacio transparente al usuario

## Componentes

### [YOLO Service](./yolo-service/README.md)
- Detección con modelos YOLOv11 optimizados
- Servidor FastAPI en puerto 8001
- Extracción automática de GPS/EXIF
- Generación de imágenes procesadas con marcadores
- Soporte para JPEG, PNG, HEIC, TIFF

### [Backend](./backend/README.md)
- API REST con FastAPI
- Base de datos PostgreSQL/Supabase
- Autenticación y gestión de usuarios
- Integración automática con YOLO service
- Sistema de nomenclatura estandarizada
- Almacenamiento dual de imágenes (Supabase Storage)
- Deduplicación automática de contenido

### [Frontend](./frontend/README.md)
- Interfaz React con TypeScript
- Dashboard interactivo con mapas
- Sistema de upload y análisis
- Autenticación y gestión de roles

### [Shared Library](./shared/README.md)
- Enums unificados para consistencia
- Algoritmos de evaluación de riesgo
- Utilidades de archivos e imágenes avanzadas
- Sistema de nomenclatura estandarizada
- Deduplicación inteligente de imágenes
- Sistema de logging centralizado

### [Scripts de Utilidad](./scripts/README.md)
- `scripts/comprehensive_fix_imports.py` - Corrección automática de errores de importación
- `scripts/fix_entry_points.py` - Corrección específica para entry points
- `scripts/fix_api_routers.py` - Solución para imports en routers API
- `scripts/simple_test.py` - Pruebas básicas de funcionalidad del sistema
- `scripts/quick_smoke_tests.py` - Verificación rápida de componentes críticos
- `scripts/test_deduplication.py` - Pruebas específicas del sistema de deduplicación
- `start-all.ps1` - Script de inicio automático para todos los servicios

## Estado del Proyecto

| Componente | Estado | Puerto |
|-----------|--------|--------|
| **YOLO Service** | ✅ Completo | 8001 |
| **Backend API** | ✅ Completo | 8000 |
| **Frontend React** | ✅ Completo | 3000 |
| **Shared Library** | ✅ Completo | - |

## Configuración

El proyecto utiliza configuración centralizada a través de variables de entorno:

```bash
# Puertos estandarizados
BACKEND_PORT=8000
YOLO_SERVICE_PORT=8001

# Base de datos
DATABASE_URL=postgresql://...
SUPABASE_URL=tu_url_supabase

# IA y modelos
YOLO_MODEL_PATH=models/best.pt
YOLO_CONFIDENCE_THRESHOLD=0.5
```

## Requisitos

- **Python 3.8+**
- **4GB RAM** (8GB recomendado)
- **GPU NVIDIA** (opcional, para acelerar detección)
- **PostgreSQL** (o cuenta Supabase)

## Instalación

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/sentrix.git
cd sentrix

# Configurar entorno
python scripts/setup-env.py

# Instalar dependencias backend
pip install -r backend/requirements.txt
pip install -r yolo-service/requirements.txt

# Instalar dependencias frontend
cd frontend && npm install && cd ..

# Configurar base de datos
cd backend && python main.py db migrate
```

## Testing y Validación

### Verificación Rápida del Sistema
```bash
# Pruebas básicas de funcionalidad
python scripts/simple_test.py

# Verificación rápida de componentes críticos
python scripts/quick_smoke_tests.py

# Pruebas específicas de deduplicación
python scripts/test_deduplication.py
```

### Verificación de Servicios
```bash
# Verificar que todos los servicios estén ejecutándose
curl http://localhost:8000/health    # Backend
curl http://localhost:8001/health    # YOLO Service
curl http://localhost:3000           # Frontend

# Test de funcionalidad avanzada
curl -X POST "http://localhost:8000/api/v1/analyses" \
  -F "file=@test_image.jpg" \
  -F "confidence_threshold=0.5"
```

### Tests Unitarios y de Integración
```bash
# Tests por componente
cd backend && python -m pytest tests/ -v
cd yolo-service && python -m pytest tests/ -v

# Test de integración completa con almacenamiento dual
curl -X POST "http://localhost:8001/detect" -F "file=@test_image.jpg"
```

## Diagnóstico del Sistema

```bash
# Diagnóstico del YOLO Service (GPU, modelos, hardware)
cd yolo-service && python diagnostic.py

# Diagnóstico del Backend (conexiones, dependencias, puertos)
cd backend && python diagnostic.py
```

**Los scripts de diagnóstico proporcionan:**
- Estado completo del hardware y software
- Recomendaciones de modelos YOLO según GPU disponible
- Verificación de conexiones entre servicios
- Estado de dependencias y configuración

## Evaluación de Riesgo

El sistema calcula automáticamente el nivel de riesgo epidemiológico:

- **ALTO**: ≥3 sitios de alto riesgo O ≥1 alto + ≥3 medio
- **MEDIO**: ≥1 sitio de alto riesgo O ≥3 sitios de riesgo medio
- **BAJO**: ≥1 sitio de riesgo medio
- **MÍNIMO**: Sin sitios de riesgo detectados

## Proyecto de Investigación

**Objetivo**: Desarrollar un sistema de IA para la detección, geolocalización y análisis de focos de *Aedes aegypti* en zonas urbanas.

**Metodología**: Modelos YOLOv11 + algoritmos epidemiológicos + integración ambiental

**Resultados**: Sistema funcional con 56.1% de cobertura GPS en dataset argentino

## Documentación

- [Backend API](./backend/README.md) - Documentación completa del backend
- [YOLO Service](./yolo-service/README.md) - Servicio de detección IA
- [Shared Library](./shared/README.md) - Librería compartida
- [Import Conventions](./shared/IMPORT_CONVENTIONS.md) - Convenciones de código

## Licencia

MIT License - Ver [LICENSE](LICENSE) para detalles.

---

**Versión**: 2.3.0 | **Estado**: Sistema completo con funcionalidades avanzadas | **Actualizado**: Octubre 2025

---

## Actualizaciones Recientes (v2.3.0)

### Nuevas Funcionalidades Implementadas:
- **Sistema de Nomenclatura Estandarizada**: Archivos con formato profesional y trazabilidad
- **Almacenamiento Dual Inteligente**: Imágenes originales y procesadas con marcadores YOLO
- **Deduplicación Automática**: Prevención de overflow de storage con detección de contenido duplicado
- **Gestión Avanzada de Metadatos**: Extracción y codificación de GPS, cámara y timestamps

### Mejoras en Componentes:
- **Frontend**: Nuevos componentes UI (Dialog, Select, Tabs), AuthLayout mejorado, configuración ESLint optimizada
- **Backend**: Sistema de referencias para duplicados, optimización de storage, integración Supabase mejorada
- **YOLO Service**: Generación automática de imágenes procesadas con marcadores azules
- **Shared Library**: Utilidades avanzadas de archivos y sistema de deduplicación
- **Testing**: Suite completa de pruebas para nuevas funcionalidades

### Servicios Verificados Como Funcionales:
- **Backend** (Puerto 8000): API con almacenamiento dual y deduplicación
- **YOLO Service** (Puerto 8001): Procesamiento con imágenes marcadas
- **Frontend** (Puerto 3000): Interfaz actualizada con nuevas capacidades
- **Sistema de Storage**: Optimización automática sin pérdida de funcionalidad

### Impacto en Rendimiento:
- **Ahorro de Storage**: Sistema de referencias evita almacenamiento duplicado
- **Trazabilidad**: Nomenclatura estandarizada permite seguimiento completo
- **Profesionalización**: Eliminación de caracteres no estándar en archivos

**El proyecto incluye ahora un sistema completo de gestión inteligente de imágenes, optimizado para uso profesional y académico con almacenamiento eficiente.**