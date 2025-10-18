# Sentrix - Detección IA de Criaderos de Aedes aegypti

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![YOLO v11](https://img.shields.io/badge/YOLO-v11-brightgreen.svg)](https://github.com/ultralytics/ultralytics)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/tests-532+-success.svg)](./backend/tests/)
[![Coverage](https://img.shields.io/badge/coverage-69--91%25-yellow.svg)](./PENDING_IMPROVEMENTS.md)

Sistema de inteligencia artificial para la detección automatizada de criaderos de mosquitos del dengue usando visión por computadora y evaluación de riesgo epidemiológico.

## Características Principales

- **Detección IA**: Modelos YOLOv11 para identificar criaderos en imágenes
- **Evaluación de Riesgo**: Clasificación automática de riesgo epidemiológico (ALTO/MEDIO/BAJO/MÍNIMO)
- **API REST**: Backend completo con FastAPI, PostgreSQL/Supabase y circuit breakers
- **Geolocalización**: Extracción automática de coordenadas GPS desde metadatos EXIF
- **Gestión Inteligente**: Nomenclatura estandarizada y deduplicación automática de imágenes
- **Almacenamiento Dual**: Imágenes originales y procesadas con marcadores de detección
- **Testing Robusto**: 532+ tests con cobertura del 69-91% en módulos críticos
- **Observabilidad**: Logging estructurado, OpenTelemetry y health checks completos

## Arquitectura

```
sentrix/
├── backend/          # API REST (FastAPI, puerto 8000)
│   ├── src/          # Código fuente (api, services, database, core)
│   └── tests/        # 532+ tests (unit, integration, performance)
├── yolo-service/     # Servicio de detección IA (puerto 8001)
│   ├── src/          # Detector, evaluator, trainer
│   ├── models/       # Modelos YOLO entrenados
│   └── tests/        # Tests de detección e inferencia
├── shared/           # Paquete sentrix_shared
│   └── sentrix_shared/  # Librería compartida (enums, risk assessment, utils)
├── frontend/         # Interfaz web React + TypeScript (puerto 5173)
│   └── src/          # Componentes, hooks, servicios
├── scripts/          # Scripts de utilidad y deployment
└── docs/             # Documentación técnica completa
```

### Flujo de Datos

```
Usuario → Frontend → Backend API → YOLO Service → Modelo AI
                ↓           ↓
            Supabase   PostgreSQL
              (Storage)  (Database)
```

## Inicio Rápido

### Requisitos
- Python 3.8+, Node.js 16+, Redis, PostgreSQL (Supabase)
- 4GB RAM mínimo (8GB recomendado)

### Instalación

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e ../shared

# YOLO Service
cd ../yolo-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Configuración

**Importante**: Sentrix usa un solo archivo `.env` centralizado en la raíz del proyecto. Todos los servicios (backend, yolo-service, frontend) leen desde este único archivo.

```bash
# Copiar .env.example a .env
cp .env.example .env

# Editar .env con tus valores
nano .env  # o tu editor preferido
```

Variables mínimas para desarrollo:

```bash
# En el archivo .env (raíz del proyecto)
ENVIRONMENT=development
DEBUG=true

# Servicios
YOLO_SERVICE_URL=http://localhost:8001
REDIS_URL=redis://localhost:6379/0

# Base de datos
DATABASE_URL=sqlite:///./test.db

# Seguridad (generar en producción)
SECRET_KEY=dev-secret-key-change-in-production-min32chars
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production-min32chars

# Supabase (si usas Supabase)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_key_aqui
```

**Nota**: No crear `.env` en subdirectorios (backend/, yolo-service/). Solo usa el `.env` en la raíz.

### Ejecución

```bash
# Terminal 1: Backend API
cd backend && python -m uvicorn app:app --reload

# Terminal 2: YOLO Service
cd yolo-service && python server.py

# Terminal 3: Frontend
cd frontend && npm run dev

# Terminal 4 (opcional): Celery Worker
cd backend && celery -A src.celery_app worker --loglevel=info
```

### Acceso
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- YOLO Health: http://localhost:8001/health

## Uso Básico

```bash
# Análisis completo con almacenamiento
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
| Charcos/Cúmulo de agua | ALTO | Agua estancada visible, hábitat directo |
| Basura | ALTO | Acumulación de residuos con retención de agua |
| Huecos | MEDIO | Cavidades que retienen agua de lluvia |
| Calles mal hechas | MEDIO | Superficies irregulares que forman charcos |

**Clasificación de Riesgo:**
- **ALTO**: ≥3 sitios alto riesgo O ≥1 alto + ≥3 medio
- **MEDIO**: ≥1 sitio alto riesgo O ≥3 sitios medio
- **BAJO**: ≥1 sitio medio riesgo O ≥5 detecciones totales
- **MÍNIMO**: Sin sitios detectados

## Testing

El proyecto cuenta con **532+ tests** con cobertura del **69-91%** en módulos críticos.

```bash
# Backend (532+ tests)
cd backend && python -m pytest tests/ -v

# Con cobertura
cd backend && pytest tests/ --cov=src --cov-report=html --cov-report=term

# Tests específicos
cd backend && pytest tests/test_yolo_service_unit.py -v       # 29 tests (91% coverage)
cd backend && pytest tests/test_analysis_service.py -v        # 39 tests (69% coverage)
cd backend && pytest tests/test_transformers.py -v             # 49 tests (100% coverage)
cd backend && pytest tests/integration/ -v -m integration      # 4 tests E2E
cd backend && pytest tests/performance/ -v -m performance      # 11 tests de performance

# YOLO Service
cd yolo-service && python -m pytest tests/ -v

# Shared Library
cd shared && python -m pytest tests/ -v

# Scripts de utilidad
python scripts/simple_test.py
python scripts/quick_smoke_tests.py
```

### Cobertura por Módulo (Backend)

| Módulo | Coverage | Tests |
|--------|----------|-------|
| `transformers/` | 100% | 49 tests |
| `validators/` | 100% | 52 tests |
| `core/services/yolo_service.py` | 91% | 29 tests |
| `schemas/analyses.py` | 95% | Incluidos |
| `services/analysis_service.py` | 69% | 39 tests |

## Documentación

- **[Documentación Técnica](./docs/)**: Arquitectura, implementaciones, fases del proyecto
- **[Backend](./backend/README.md)**: API REST, endpoints, configuración
- **[YOLO Service](./yolo-service/README.md)**: Servicio de detección IA
- **[Shared Library](./shared/README.md)**: Librería compartida, risk assessment
- **[Scripts](./scripts/README.md)**: Scripts de utilidad y deployment

## Licencia

MIT License - Sistema desarrollado para investigación en control epidemiológico del dengue.

---

**Versión**: 2.6.0 | **Actualizado**: Octubre 2025