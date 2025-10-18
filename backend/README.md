# Backend API - Sentrix

API REST basada en FastAPI para la plataforma Sentrix de detección de criaderos de *Aedes aegypti*.

## Descripción

Backend completo que coordina análisis de imágenes con IA, gestión de usuarios, persistencia de datos y evaluación de riesgo epidemiológico. Se integra con el servicio YOLO y provee API REST para el frontend.

### Funcionalidades Principales

- **Análisis con IA**: Integración con servicio YOLO para detección automatizada
- **Almacenamiento Dual**: Imágenes originales y procesadas con marcadores
- **Deduplicación Inteligente**: Detección de contenido duplicado por hash
- **Nomenclatura Estandarizada**: Sistema profesional de nombres con metadatos
- **Datos Geoespaciales**: Extracción automática GPS y almacenamiento PostGIS
- **Gestión de Usuarios**: Autenticación basada en roles (USER, ADMIN, EXPERT)
- **Validación por Expertos**: Flujo de verificación de detecciones
- **Generación de Reportes**: Exportación PDF y CSV con filtros
- **Circuit Breaker**: Protección contra fallos del servicio YOLO
- **Procesamiento Asíncrono**: Cola de tareas con Celery y Redis
- **Logging Estructurado**: Trazabilidad completa de requests
- **OpenTelemetry**: Trazas distribuidas para observabilidad

## Stack Tecnológico

- **Framework**: FastAPI 0.104+, Uvicorn
- **Base de Datos**: PostgreSQL 14+ con PostGIS
- **ORM**: SQLAlchemy 2.0+
- **Storage**: Supabase Storage
- **Autenticación**: JWT (python-jose)
- **Validación**: Pydantic 2.0+
- **Queue**: Celery, Redis
- **Observabilidad**: OpenTelemetry, Jaeger
- **Testing**: pytest

## Estructura del Proyecto

```
backend/
├── app.py                       # Punto de entrada principal de FastAPI
├── main.py                      # Configuración de la aplicación
├── requirements.txt             # Dependencias Python
├── pytest.ini                   # Configuración de tests
├── src/
│   ├── api/v1/                 # API REST Endpoints
│   │   ├── analyses.py         # Análisis de imágenes (POST, GET, heatmap)
│   │   ├── auth.py             # Autenticación y registro
│   │   ├── health.py           # Health checks y readiness
│   │   ├── reports.py          # Generación de reportes PDF/CSV
│   │   └── detections.py       # Gestión de detecciones
│   ├── core/                   # Lógica de negocio central
│   │   ├── services/           # Servicios externos
│   │   │   └── yolo_service.py # Cliente del servicio YOLO
│   │   ├── analysis_processor.py # Procesador de análisis
│   │   ├── api_manager.py      # Gestor de API calls
│   │   └── detection_validator.py # Validador de detecciones
│   ├── services/               # Capa de servicios de negocio
│   │   ├── analysis_service.py # Lógica de análisis (69% coverage)
│   │   ├── report_service.py   # Generación de reportes
│   │   └── user_service.py     # Gestión de usuarios
│   ├── database/               # Capa de persistencia
│   │   ├── models/             # Modelos SQLAlchemy
│   │   │   ├── models.py       # UserProfile, Analysis, Detection
│   │   │   ├── enums.py        # Enums de base de datos
│   │   │   └── base.py         # Base declarativa
│   │   ├── repositories/       # Patrón Repository
│   │   │   ├── base.py         # Repositorio base
│   │   │   ├── analysis_repository.py
│   │   │   ├── detection_repository.py
│   │   │   └── user_repository.py
│   │   ├── connection.py       # Conexión a base de datos
│   │   └── migrations/         # Migraciones Alembic
│   ├── schemas/                # Schemas Pydantic de validación
│   │   ├── analyses.py         # Schemas de análisis (95% coverage)
│   │   ├── auth.py             # Schemas de autenticación
│   │   └── settings.py         # Settings de usuario
│   ├── transformers/           # Transformadores de datos (100% coverage)
│   │   └── analysis_transformers.py # Transforma YOLO → DB schemas
│   ├── validators/             # Validadores de negocio (100% coverage)
│   │   └── analysis_validators.py # Validación de análisis
│   ├── middleware/             # Middleware de FastAPI
│   │   ├── rate_limit.py       # Rate limiting por IP
│   │   └── request_id.py       # Request ID tracking
│   ├── cache/                  # Capa de caching con Redis
│   │   ├── cache_service.py    # Servicio de cache
│   │   ├── decorators.py       # Decoradores @cached
│   │   └── middleware.py       # Cache middleware
│   ├── tasks/                  # Tareas asíncronas Celery
│   │   └── analysis_tasks.py   # Tasks de análisis en background
│   ├── tracing/                # Observabilidad OpenTelemetry
│   │   ├── config.py           # Configuración OTEL
│   │   ├── decorators.py       # @traced decorator
│   │   └── instrumentation.py  # Auto-instrumentación
│   ├── utils/                  # Utilidades compartidas
│   │   ├── auth.py             # Helpers de autenticación JWT
│   │   ├── supabase_client.py  # Cliente de Supabase
│   │   ├── integrations/       # Integraciones externas
│   │   │   └── yolo_integration.py
│   │   ├── image_conversion.py # Conversión HEIC/HEIF
│   │   ├── temporal_validity.py # Validez temporal GPS
│   │   └── config_validator.py # Validación de configuración
│   ├── config.py               # Configuración centralizada (Pydantic Settings)
│   ├── logging_config.py       # Logging estructurado (structlog)
│   ├── exceptions.py           # Excepciones personalizadas
│   └── celery_app.py          # Configuración de Celery
├── tests/                      # Suite de tests (532+ tests)
│   ├── test_analysis_service.py      # Tests de analysis_service (39 tests)
│   ├── test_yolo_service_unit.py     # Tests de YOLO service (29 tests)
│   ├── test_transformers.py          # Tests de transformers (49 tests)
│   ├── test_validators.py            # Tests de validators (52 tests)
│   ├── integration/                  # Tests E2E (4 tests)
│   │   └── test_complete_flow.py
│   ├── performance/                  # Tests de performance (11 tests)
│   │   └── test_api_performance.py
│   └── conftest.py                   # Fixtures globales de pytest
├── scripts/                    # Scripts de utilidad
│   ├── run_server.py          # Script para iniciar servidor
│   └── database_maintenance.py # Mantenimiento de BD
└── logs/                       # Logs de aplicación
```

## Instalación Rápida

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
pip install -e ../shared

# Configurar .env (ver .env.example)
cp .env.example .env

# Ejecutar servicios
# Terminal 1: Redis
redis-server

# Terminal 2: Backend
python -m uvicorn app:app --reload --port 8000

# Terminal 3: Celery Worker (opcional)
celery -A src.celery_app worker --loglevel=info
```

## Variables de Entorno Requeridas

```bash
# Servidor
BACKEND_PORT=8000
ENVIRONMENT=development

# Base de Datos
DATABASE_URL=postgresql://user:pass@localhost:5432/sentrix
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-service-role-key

# Seguridad
SECRET_KEY=genera-clave-segura-32chars
JWT_SECRET_KEY=genera-jwt-secret

# Servicios
YOLO_SERVICE_URL=http://localhost:8001
REDIS_URL=redis://localhost:6379/0

# OpenTelemetry (opcional)
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

## API Endpoints Principales

### Autenticación
- `POST /api/v1/register` - Registrar usuario
- `POST /api/v1/token` - Iniciar sesión (obtener JWT)
- `GET /api/v1/me` - Obtener usuario actual

### Análisis
- `POST /api/v1/analyses` - Crear análisis (síncrono)
- `POST /api/v1/analyses/async` - Crear análisis (asíncrono con Celery)
- `GET /api/v1/analyses` - Listar análisis con filtros
- `GET /api/v1/analyses/{id}` - Detalles de análisis
- `GET /api/v1/analyses/status/{job_id}` - Estado de job asíncrono

### Health Checks
- `GET /api/v1/health` - Health check básico
- `GET /api/v1/health/ready` - Readiness (incluye deps)
- `GET /api/v1/health/circuit-breakers` - Estado de circuit breakers

### Reportes
- `POST /api/v1/reports/generate` - Generar reporte PDF/CSV

### Usuarios (Admin)
- `GET /api/v1/users` - Listar usuarios
- `PUT /api/v1/users/{id}` - Actualizar rol

## Uso Básico

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Registrar usuario
curl -X POST http://localhost:8000/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Test123!","display_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/v1/token \
  -d "username=user@test.com&password=Test123!"

# Análisis de imagen
curl -X POST http://localhost:8000/api/v1/analyses \
  -H "Authorization: Bearer <token>" \
  -F "file=@imagen.jpg" \
  -F "confidence_threshold=0.5"

# Análisis asíncrono
curl -X POST http://localhost:8000/api/v1/analyses/async \
  -H "Authorization: Bearer <token>" \
  -F "file=@imagen.jpg"
```

## Base de Datos

### Tablas Principales

- **user_profiles**: Cuentas de usuario y autenticación
- **analyses**: Registros de análisis de imágenes
- **detections**: Detecciones individuales por análisis

### Enums

- `user_role_enum`: USER, ADMIN, EXPERT
- `detection_risk_enum`: ALTO, MEDIO, BAJO, MINIMO
- `breeding_site_type_enum`: Basura, Calles mal hechas, Charcos/Cumulo de agua, Huecos
- `validation_status_enum`: pending_validation, validated_positive, validated_negative, requires_review
- `location_source_enum`: EXIF_GPS, MANUAL, ESTIMATED

## Testing

El backend cuenta con una suite completa de tests con **532+ tests** y cobertura del **69-91%** en módulos críticos.

### Ejecutar Tests

```bash
# Ejecutar todos los tests
python -m pytest tests/ -v

# Con cobertura
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Tests específicos por categoría
pytest tests/test_analysis_service.py -v      # 39 tests del servicio de análisis
pytest tests/test_yolo_service_unit.py -v     # 29 tests del cliente YOLO
pytest tests/test_transformers.py -v           # 49 tests de transformadores
pytest tests/test_validators.py -v             # 52 tests de validadores

# Tests de integración E2E
pytest tests/integration/ -v -m integration    # 4 tests E2E

# Tests de performance
pytest tests/performance/ -v -m performance    # 11 tests de performance

# Ver reporte HTML de cobertura
pytest tests/ --cov=src --cov-report=html
# Abre: htmlcov/index.html
```

### Cobertura por Módulo

| Módulo | Coverage | Tests |
|--------|----------|-------|
| `transformers/` | 100% | 49 tests |
| `validators/` | 100% | 52 tests |
| `schemas/analyses.py` | 95% | Incluidos en suite |
| `core/services/yolo_service.py` | 91% | 29 tests |
| `services/analysis_service.py` | 69% | 39 tests |
| `exceptions.py` | 76% | Incluidos en suite |
| `config.py` | 72% | Incluidos en suite |
| `logging_config.py` | 65% | Incluidos en suite |

### Categorías de Tests

- **Tests Unitarios**: 503+ tests de lógica de negocio
- **Tests de Integración**: 4 tests E2E del flujo completo
- **Tests de Performance**: 11 tests de latencia, throughput y carga
- **Tests de API**: Validación de endpoints y responses
- **Tests de Servicios**: Análisis, YOLO, autenticación, reportes

## Funcionalidades Avanzadas

### 1. Nomenclatura Estandarizada
```
SENTRIX_YYYYMMDD_HHMMSS_DEVICE_LOCATION_ID.ext
Ejemplo: SENTRIX_20241008_143052_IPHONE15_LATn34p604_LONn58p382_a1b2c3d4.jpg
```

### 2. Deduplicación
- Hash SHA-256 de contenido binario
- Sin almacenamiento redundante de archivos
- Referencias en BD para duplicados

### 3. Circuit Breaker
- Protección contra fallos del servicio YOLO
- Auto-recuperación tras 60 segundos
- Fallback a responses por defecto

### 4. Procesamiento Asíncrono
- Cola Celery con Redis
- Jobs de larga duración en background
- Monitoreo con Flower (puerto 5555)

### 5. OpenTelemetry
- Trazas distribuidas entre servicios
- Exportación a Jaeger/OTLP
- Decoradores `@traced` para instrumentación manual

## Desarrollo

```bash
# Formatear código
black src/ tests/

# Linting
ruff check src/ tests/

# Migraciones
alembic upgrade head
alembic revision --autogenerate -m "descripción"
```

## Deployment

```bash
# Docker
docker build -t sentrix-backend .
docker run -d -p 8000:8000 --env-file .env sentrix-backend

# O usar docker-compose (raíz del proyecto)
docker-compose up backend
```

## Solución de Problemas

**Error: `ModuleNotFoundError: No module named 'sentrix_shared'`**
```bash
cd ../shared && pip install -e .
# Verificar instalación
python -c "from sentrix_shared import risk_assessment; print('OK')"
```

**Error: Conexión a base de datos**
```bash
# Verificar PostgreSQL
psql $DATABASE_URL

# Crear BD si no existe
createdb sentrix
```

**Error: Servicio YOLO no responde**
```bash
# Verificar YOLO service
curl http://localhost:8001/health

# Ver estado del circuit breaker
curl http://localhost:8000/api/v1/health/circuit-breakers
```

**Error: Redis no disponible**
```bash
# Iniciar Redis
redis-server

# Verificar
redis-cli ping
```

## Documentación Adicional

- **[Documentación completa](../docs/)**: Arquitectura, implementaciones, guías
- **[API Docs](http://localhost:8000/docs)**: Documentación interactiva Swagger
- **[Shared Library](../shared/README.md)**: Librería compartida

---

**Versión**: 2.6.0 | **Python**: 3.8+ | **Estado**: Producción | **Tests**: 532+ | **Coverage crítico**: 69-91% | **Actualizado**: Octubre 2025
