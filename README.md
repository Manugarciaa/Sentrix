# Sentrix - Detección IA de Criaderos de Aedes aegypti

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![YOLO v11](https://img.shields.io/badge/YOLO-v11-brightgreen.svg)](https://github.com/ultralytics/ultralytics)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

Plataforma de inteligencia artificial para la detección automatizada de criaderos de mosquitos del dengue usando visión por computadora y evaluación de riesgo epidemiológico.

## Descripción

Sistema completo de detección de sitios de reproducción de *Aedes aegypti* que combina:

- **Detección IA** - Modelos YOLOv11 para identificar criaderos en imágenes
- **Evaluación de riesgo** - Algoritmos epidemiológicos para clasificación automática
- **API REST** - Backend completo con base de datos PostgreSQL
- **Geolocalización** - Extracción automática de coordenadas GPS desde metadatos EXIF

## Arquitectura

```
sentrix/
├── backend/                # API REST + Base de datos
├── yolo-service/          # Servicio de detección IA
├── shared/                # Librería compartida
├── scripts/               # Scripts de configuración
└── frontend/              # Interfaz web (próximamente)
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

```bash
# Terminal 1: Servicio YOLO (puerto 8001)
cd yolo-service && python server.py

# Terminal 2: Backend API (puerto 8000)
cd backend && python scripts/run_server.py
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

## Componentes

### 🤖 [YOLO Service](./yolo-service/README.md)
- Detección con modelos YOLOv11 optimizados
- Servidor FastAPI en puerto 8001
- Extracción automática de GPS/EXIF
- Soporte para JPEG, PNG, HEIC, TIFF

### 🔧 [Backend](./backend/README.md)
- API REST con FastAPI
- Base de datos PostgreSQL/Supabase
- Autenticación y gestión de usuarios
- Integración automática con YOLO service

### 📚 [Shared Library](./shared/README.md)
- Enums unificados para consistencia
- Algoritmos de evaluación de riesgo
- Utilidades de archivos e imágenes
- Sistema de logging centralizado

### ⚙️ Scripts de Configuración
- `scripts/setup-env.py` - Configuración automática del entorno
- `scripts/simple-validation.py` - Validación de integración
- Configuración centralizada de puertos y servicios

## Estado del Proyecto

| Componente | Estado | Puerto |
|-----------|--------|--------|
| **YOLO Service** | ✅ Completo | 8001 |
| **Backend API** | ✅ Completo | 8000 |
| **Shared Library** | ✅ Completo | - |
| **Frontend Web** | 🔄 En desarrollo | 3000 |

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

# Instalar dependencias
pip install -r backend/requirements.txt
pip install -r yolo-service/requirements.txt

# Configurar base de datos
cd backend && alembic upgrade head
```

## Testing

```bash
# Validación completa del sistema
python scripts/simple-validation.py

# Tests por componente
cd backend && python -m pytest tests/ -v
cd yolo-service && python -m pytest tests/ -v
```

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

**Versión**: 2.1.0 | **Estado**: Sistema completo backend + YOLO | **Actualizado**: Enero 2025