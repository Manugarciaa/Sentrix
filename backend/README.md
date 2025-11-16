# Backend - Sentrix API

![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-316192)
![Tests](https://img.shields.io/badge/tests-varios%20cientos-success)
![Coverage](https://img.shields.io/badge/coverage-78--100%25-brightgreen)

API REST del sistema Sentrix. Gestión de análisis, usuarios, autenticación JWT, integración con YOLO service y base de datos PostgreSQL+PostGIS.

---

## Quick Start

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e ../shared

cp .env.example .env
# Editar .env con credenciales

# Opción 1: Servidor web (API REST)
python app.py
# o
uvicorn app:app --reload --port 8000

# Opción 2: CLI para comandos de gestión
python main.py --help
```

**Acceso API**: http://localhost:8000/docs

---

## Arquitectura

<div align="center">

```mermaid
%%{init: {'theme':'neutral','themeVariables':{'fontSize':'13px'}}}%%
graph TB
    Client[Cliente]-->|HTTP|API[FastAPI<br/>:8000]
    API-->Auth[Auth JWT]
    API-->Services[Business<br/>Services]
    Services-->DB[(PostgreSQL<br/>+PostGIS)]
    Services-->Storage[Supabase<br/>Storage]
    Services-->YOLO[YOLO Service<br/>:8001]
    Services-->Redis[(Redis<br/>Cache)]

    style API fill:#00897b,stroke:#333,color:#fff,stroke-width:2px
    style Auth fill:#1976d2,stroke:#333,color:#fff,stroke-width:2px
    style Services fill:#43a047,stroke:#333,color:#fff,stroke-width:2px
    style DB fill:#5e35b1,stroke:#333,color:#fff,stroke-width:2px
    style Storage fill:#f4511e,stroke:#333,color:#fff,stroke-width:2px
    style YOLO fill:#7cb342,stroke:#333,color:#fff,stroke-width:2px
    style Redis fill:#d32f2f,stroke:#333,color:#fff,stroke-width:2px
```

</div>

---

## Estructura

```
backend/
├── app.py                    # App FastAPI - Servidor web principal
├── main.py                   # CLI - Comandos de gestión y análisis batch
├── requirements.txt          # Dependencias Python
├── .env.example             # Template de variables de entorno
├── pytest.ini               # Configuración de pytest
├── Dockerfile               # Imagen Docker
├── run_tests.sh/.ps1        # Scripts para ejecutar tests
│
├── src/                     # Código fuente principal
│   ├── api/
│   │   └── v1/             # Endpoints REST API v1
│   │       ├── analyses.py  # CRUD análisis
│   │       ├── auth.py      # Login/register/me
│   │       ├── detections.py # Gestión de detecciones
│   │       ├── reports.py   # Generación de reportes
│   │       └── health.py    # Health checks
│   │
│   ├── core/               # Lógica de negocio core
│   │   └── services/       # Servicios principales
│   │       └── yolo_service.py
│   │
│   ├── services/           # Servicios de aplicación
│   │   ├── analysis_service.py
│   │   └── supabase_manager.py
│   │
│   ├── database/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── repositories/   # Patrones repository
│   │   ├── migrations/     # Scripts de migración Alembic
│   │   └── connection.py   # Configuración de DB
│   │
│   ├── schemas/            # Pydantic schemas (request/response)
│   │   ├── analyses.py
│   │   ├── auth.py
│   │   └── users.py
│   │
│   ├── middleware/         # Middlewares de FastAPI
│   │   ├── rate_limit.py
│   │   └── request_id.py
│   │
│   ├── utils/              # Utilidades
│   │   ├── supabase_client.py
│   │   ├── config_validator.py
│   │   └── integrations/   # Integraciones externas
│   │
│   ├── validators/         # Validadores personalizados
│   ├── transformers/       # Transformadores de datos
│   ├── tasks/             # Tareas asíncronas (Celery)
│   ├── tracing/           # OpenTelemetry tracing
│   ├── cache/             # Gestión de caché
│   ├── config.py          # Configuración global
│   └── logging_config.py  # Configuración de logs estructurados
│
├── alembic/               # Migraciones de base de datos
│   └── versions/
│
├── scripts/               # Scripts de desarrollo y utilidades
│   ├── tests/            # Scripts de testing
│   ├── migrations/       # Scripts de migración manual
│   ├── diagnostics/      # Scripts de diagnóstico
│   └── sql/             # Scripts SQL
│
├── tests/                # Suite de tests (varios cientos)
│   ├── integration/      # Tests de integración
│   └── performance/      # Tests de performance
│
├── data/                 # Datos temporales (gitignored)
├── logs/                 # Logs de aplicación (gitignored)
└── uploads/              # Uploads temporales (gitignored)
```

---

## API Endpoints

### Autenticación

```bash
POST /api/v1/auth/register    # Registro
POST /api/v1/auth/login       # Login (retorna JWT)
GET  /api/v1/auth/me          # Usuario actual
```

### Análisis

```bash
GET    /api/v1/analyses                  # Listar análisis
POST   /api/v1/analyses                  # Crear análisis (upload imagen)
GET    /api/v1/analyses/{id}             # Detalle análisis
PATCH  /api/v1/analyses/{id}/validate    # Validar (EXPERT/ADMIN)
DELETE /api/v1/analyses/{id}             # Eliminar (ADMIN)
```

### Usuarios

```bash
GET    /api/v1/users          # Listar usuarios (ADMIN)
GET    /api/v1/users/{id}     # Detalle usuario
PATCH  /api/v1/users/{id}     # Actualizar usuario
```

**Documentación completa**: http://localhost:8000/docs

---

## Modelos de Datos

### Analysis
```python
{
  "analysis_id": "uuid",
  "user_id": "uuid",
  "status": "COMPLETED",
  "original_image_path": "path/to/image.jpg",
  "processed_image_path": "path/to/processed.jpg",
  "detections": [...],  # JSON de detecciones
  "risk_level": "ALTO",
  "latitude": -34.603722,
  "longitude": -58.381592,
  "created_at": "2025-11-07T10:00:00Z"
}
```

### User
```python
{
  "user_id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "USER",  # USER, EXPERT, ADMIN
  "is_active": true,
  "created_at": "2025-11-07T10:00:00Z"
}
```

---

## Servicios

### AnalysisService
- Gestión de análisis (CRUD)
- Integración con YOLO service
- Evaluación de riesgo
- Upload a Supabase

### YoloClient
- Client HTTP para YOLO service
- Circuit breaker pattern
- Retry automático
- Timeout configurab le

### SupabaseManager
- Upload de imágenes
- Gestión de storage buckets
- Generación de URLs públicas
- Nomenclatura estandarizada

---

## Autenticación

Sistema JWT con refresh tokens:

```python
# Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password"
}

# Response
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}

# Usar token
curl -H "Authorization: Bearer eyJ..." http://localhost:8000/api/v1/analyses
```

---

## Roles y Permisos

| Acción | USER | EXPERT | ADMIN |
|--------|------|--------|-------|
| Ver análisis propios | ✓ | ✓ | ✓ |
| Ver todos los análisis | ✗ | ✓ | ✓ |
| Crear análisis | ✓ | ✓ | ✓ |
| Validar análisis | ✗ | ✓ | ✓ |
| Eliminar análisis | ✗ | ✗ | ✓ |
| Gestionar usuarios | ✗ | ✗ | ✓ |

---

## Testing

```bash
# Todos los tests (varios cientos)
pytest tests/ -v

# Con cobertura
pytest tests/ -v --cov=src --cov-report=html

# Tests específicos
pytest tests/test_analyses.py -v
pytest tests/test_auth.py -v
pytest tests/test_services/ -v
```

**Cobertura por módulo:**
- `analyses.py`: 91%
- `auth.py`: 100%
- `analysis_service.py`: 85%
- `yolo_client.py`: 100%
- `supabase_client.py`: 78%

---

## Variables de Entorno

```bash
# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/sentrix

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# YOLO Service
YOLO_SERVICE_URL=http://localhost:8001

# JWT
SECRET_KEY=your-secret-key-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis (opcional)
REDIS_URL=redis://localhost:6379/0
ENABLE_RATE_LIMITING=true

# Servidor
BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0
```

---

## CLI de Gestión (main.py)

El backend incluye una interfaz de línea de comandos para gestión y operaciones batch:

```bash
# Ver comandos disponibles
python main.py --help

# Gestión de base de datos
python main.py db status
python main.py db migrate
python main.py db info

# Análisis de imágenes
python main.py analyze --image imagen.jpg --user-id 1
python main.py batch --directory imagenes/ --user-id 1

# Validación por expertos
python main.py validate list --priority high_risk
python main.py validate approve --detection-id 123 --expert-id 5
python main.py validate reject --detection-id 124 --notes "Falso positivo"

# Setup inicial
python main.py setup --sample-data
```

---

## Scripts de Desarrollo

En la carpeta `scripts/` se encuentran herramientas de utilidad organizadas por categoría:

- **scripts/tests/** - Scripts de testing y validación
- **scripts/migrations/** - Scripts de migración manual de base de datos
- **scripts/diagnostics/** - Scripts de diagnóstico y verificación del sistema
- **scripts/sql/** - Scripts SQL para configuración inicial y seguridad

Ver [scripts/README.md](scripts/README.md) para más detalles.

---

## Desarrollo

### Migraciones (Alembic)

```bash
# Generar migración
alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
alembic upgrade head

# Revertir
alembic downgrade -1
```

### Linting y Format

```bash
# Format con black
black src/ tests/

# Linting
ruff check src/ tests/

# Type checking
mypy src/
```

---

## Performance

### Circuit Breaker
Protección contra fallos del YOLO service:
- 5 fallos consecutivos → OPEN
- 30s timeout → HALF_OPEN
- Test request → CLOSED

### Rate Limiting (Redis)
- 10 requests/min para análisis (upload)
- Configuración ajustable vía variables de entorno
- Headers: `X-RateLimit-*`

### Caching
- Análisis: 5 minutos
- Usuarios: 10 minutos
- Configuración: 1 hora

---

## Troubleshooting

### Error: Database connection failed
```bash
# Verificar PostgreSQL
pg_isready -h localhost -p 5432

# Verificar DATABASE_URL en .env
# Verificar que la DB existe:
psql -U postgres -c "CREATE DATABASE sentrix;"
```

### Error: YOLO service unavailable
```bash
# Verificar YOLO service corriendo
curl http://localhost:8001/health

# Verificar YOLO_SERVICE_URL en .env
```

### Error: Supabase upload failed
```bash
# Verificar credenciales en .env
# Verificar bucket creado en Supabase dashboard
# Bucket name: "image-uploads" (configurado)
```

---

## Documentación Relacionada

- [README Principal](../README.md)
- [YOLO Service](../yolo-service/README.md)
- [Frontend](../frontend/README.md)
- [Shared Library](../shared/README.md)

---

**Versión**: 2.7.1 | **Actualizado**: Noviembre 2025
