# Sentrix Backend - API y Sistema de Gestión Geoespacial

Backend principal de la plataforma integral Sentrix que proporciona APIs REST robustas para la gestión completa de análisis epidemiológicos de *Aedes aegypti* mediante inteligencia artificial.

## Descripción

Este servicio constituye el **núcleo backend** de la plataforma Sentrix, proporcionando una infraestructura escalable y moderna para la gestión integral de:

- **Análisis de imágenes con IA** - Procesamiento y almacenamiento de resultados YOLO
- **Detecciones georreferenciadas** - Gestión de sitios de cría con coordenadas GPS
- **Validación por expertos** - Sistema de revisión y aseguramiento de calidad
- **Usuarios y autenticación** - Gestión de roles y permisos granulares
- **Reportes epidemiológicos** - Análisis estadístico y métricas de riesgo

## Características Principales

### API REST Moderna
- **FastAPI framework** con documentación automática OpenAPI/Swagger
- **Endpoints RESTful** siguiendo estándares de la industria
- **Validación automática** con esquemas Pydantic y type hints
- **Manejo robusto de errores** con códigos HTTP apropiados
- **CORS configurado** para integración con frontend

### Base de Datos Geoespacial
- **PostgreSQL con PostGIS** para almacenamiento y consultas geoespaciales
- **SQLAlchemy ORM** con migraciones Alembic automáticas
- **Modelos relacionales** optimizados para consultas epidemiológicas
- **Soporte completo GPS** con extracción de metadatos EXIF
- **Índices geoespaciales** para consultas de proximidad eficientes

### Integración con YOLO Service
- **Cliente HTTP asíncrono** para comunicación optimizada con servicio YOLO
- **Procesamiento por lotes** de análisis de imágenes
- **Mapeo automático** de clases YOLO a enums del backend
- **Validación de respuestas** y manejo de errores del servicio IA
- **Caché inteligente** para optimizar rendimiento

### Sistema de Autenticación y Autorización
- **Integración Supabase** para autenticación robusta
- **Roles granulares** (admin, expert, analyst, user) con permisos específicos
- **JWT tokens** para autenticación stateless
- **Middleware de seguridad** con rate limiting integrado

### Validación por Expertos
- **Sistema de revisión** para validación manual de detecciones
- **Métricas de calidad** y estadísticas de precisión
- **Sugerencias de reentrenamiento** basadas en feedback de expertos
- **Workflow de aprobación** para casos de alto riesgo

## Instalación

### Requisitos del Sistema

- Python 3.9 o superior
- PostgreSQL 13+ con extensión PostGIS
- Redis 6+ (para caché y tareas asíncronas)
- Cuenta Supabase (para autenticación)
- 4GB RAM mínimo, 8GB recomendado

### Instalación de Dependencias

```bash
# Clonar repositorio y navegar
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Configuración del Entorno

1. **Variables de entorno** - Copiar `.env.example` a `.env`:

```bash
# Base de datos PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/sentrix

# Servicios integrados
YOLO_SERVICE_URL=http://localhost:8001
REDIS_URL=redis://localhost:6379

# Autenticación Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Configuración de API
DEBUG=true
SECRET_KEY=your-super-secret-key
```

2. **Configurar PostgreSQL con PostGIS**:

```sql
-- Crear base de datos
CREATE DATABASE sentrix;

-- Conectar a la base de datos y habilitar PostGIS
\\c sentrix;
CREATE EXTENSION IF NOT EXISTS postgis;
```

3. **Ejecutar migraciones**:

```bash
python run_migrations.py
```

## Estructura del Servicio

```
backend/
├── src/                        # Código fuente modular
│   ├── core/                   # Funcionalidades principales
│   │   ├── api_manager.py      # Gestor principal de API
│   │   ├── analysis_processor.py # Procesamiento por lotes
│   │   ├── detection_validator.py # Validación de expertos
│   │   └── services/           # Servicios externos
│   │       └── yolo_service.py # Cliente YOLO service
│   ├── database/               # Gestión de base de datos
│   │   ├── connection.py       # Conexiones y configuración
│   │   ├── models/             # Modelos SQLAlchemy
│   │   │   ├── models.py       # Definiciones de modelos
│   │   │   └── enums.py        # Enumeraciones y constantes
│   │   └── migrations.py       # Utilidades de migración
│   ├── schemas/                # Esquemas Pydantic
│   │   └── analyses.py         # Schemas de análisis y detecciones
│   └── utils/                  # Utilidades del sistema
│       ├── paths.py            # Gestión automática de paths
│       ├── database_utils.py   # Utilidades de base de datos
│       ├── auth_utils.py       # Utilidades de autenticación
│       └── integrations/       # Integraciones externas
├── configs/                    # Configuración del servicio
│   └── settings.py             # Configuraciones principales
├── app/                        # Aplicación FastAPI (legacy)
│   ├── api/                    # Endpoints REST estructurados
│   │   └── v1/                 # API versión 1
│   │       ├── health.py       # Health checks del sistema
│   │       └── analyses.py     # Endpoints de análisis
│   └── main.py                 # Aplicación principal FastAPI
├── alembic/                    # Migraciones de base de datos
│   ├── env.py                  # Configuración Alembic
│   └── versions/               # Versiones de migración
├── tests/                      # Suite completa de testing
│   ├── unit/                   # Tests unitarios por módulo
│   ├── integration/            # Tests de integración
│   ├── test_models.py          # Tests de modelos de datos
│   ├── test_yolo_integration.py # Tests de integración YOLO
│   └── test_complete_system.py # Validación del sistema completo
├── scripts/                    # Scripts de utilidad y mantenimiento
│   ├── setup_development.py   # Configuración de desarrollo
│   ├── database_maintenance.py # Mantenimiento de BD
│   └── test_yolo_integration.py # Test de integración YOLO
├── logs/                       # Logs del sistema (auto-creado)
├── main.py                     # CLI principal con subcomandos
├── run_server.py               # Servidor de desarrollo
├── run_migrations.py           # Ejecutor de migraciones
├── run_tests.py                # Ejecutor de tests
└── requirements.txt            # Dependencias Python
```

## Uso del Sistema

### Servidor de Desarrollo

```bash
# Iniciar servidor FastAPI
python run_server.py

# El servidor estará disponible en:
# http://localhost:8000 - API principal
# http://localhost:8000/docs - Documentación Swagger interactiva
# http://localhost:8000/redoc - Documentación ReDoc
```

### CLI Principal (Nuevo)

El proyecto incluye un CLI moderno siguiendo el patrón de yolo-service:

#### 1. Gestión de base de datos
```bash
# Verificar estado de la base de datos
python main.py db status

# Ejecutar migraciones
python main.py db migrate

# Crear datos de prueba
python main.py db seed --sample-data
```

#### 2. Análisis de imágenes
```bash
# Procesar imagen individual
python main.py analyze --image path/to/image.jpg --user-id 1

# Procesamiento por lotes
python main.py batch --directory path/to/images/ --user-id 1

# Con umbral de confianza personalizado
python main.py analyze --image image.jpg --confidence 0.7
```

#### 3. Validación de expertos
```bash
# Listar detecciones pendientes
python main.py validate list --priority high_risk

# Validar detección específica
python main.py validate approve --detection-id 123 --expert-id 5
```

### Scripts Especializados

#### Configuración de desarrollo
```bash
# Configurar entorno completo de desarrollo
python scripts/setup_development.py --with-sample-data

# Solo verificar dependencias
python scripts/setup_development.py --check-only
```

#### Mantenimiento de base de datos
```bash
# Limpiar análisis antiguos (soft delete)
python scripts/database_maintenance.py --cleanup --days 90

# Optimizar índices
python scripts/database_maintenance.py --optimize-indexes

# Backup de datos críticos
python scripts/database_maintenance.py --backup --output backups/
```

### Uso Programático

```python
from src.core import SentrixAPIManager, AnalysisProcessor, DetectionValidator
from src.database import get_db_session
from src.schemas.analyses import AnalysisCreate

# Inicializar gestores
api_manager = SentrixAPIManager()
processor = AnalysisProcessor()
validator = DetectionValidator()

# Crear análisis
analysis_data = AnalysisCreate(
    image_path="/path/to/image.jpg",
    user_id=1,
    confidence_threshold=0.6
)
result = await api_manager.create_analysis(analysis_data)

# Procesamiento por lotes
batch_results = await processor.batch_process_images(
    image_paths=["/path/img1.jpg", "/path/img2.jpg"],
    user_id=1,
    include_gps=True
)

# Validación de expertos
pending = validator.get_pending_validations(priority="high_risk")
validation_result = validator.validate_detection(
    detection_id=123,
    expert_id=5,
    is_valid=True,
    expert_notes="Detección correcta, alta confianza"
)
```

## Características de Portabilidad

### Paths Automáticos
El sistema utiliza **paths automáticos** siguiendo el patrón de yolo-service:

```python
from src.utils import get_project_root, get_configs_dir, get_logs_dir

# Estos paths se calculan automáticamente
project_root = get_project_root()    # {proyecto}/
configs_dir = get_configs_dir()      # {proyecto}/configs/
logs_dir = get_logs_dir()            # {proyecto}/logs/
```

### Despliegue Simple
1. **Copia la carpeta completa** del backend a cualquier ubicación
2. **Configura variables de entorno** en `.env`
3. **Instala dependencias**: `pip install -r requirements.txt`
4. **Ejecuta migraciones**: `python run_migrations.py`
5. **Inicia el servidor** - no requiere modificar paths

### Compatibilidad Multiplataforma
- ✅ **Windows**: `C:\\ruta\\al\\proyecto\\`
- ✅ **Linux**: `/ruta/al/proyecto/`
- ✅ **macOS**: `/ruta/al/proyecto/`
- ✅ **Docker**: Configuración de contenedores incluida

## API Endpoints

### Análisis de Imágenes

| Endpoint | Método | Descripción | Autenticación |
|----------|--------|-------------|---------------|
| `/api/v1/analyses` | POST | Crear nuevo análisis | Requerida |
| `/api/v1/analyses` | GET | Listar análisis con filtros | Requerida |
| `/api/v1/analyses/{id}` | GET | Obtener análisis específico | Requerida |
| `/api/v1/analyses/batch` | POST | Procesamiento por lotes | Requerida |
| `/api/v1/analyses/{id}/export` | GET | Exportar análisis a JSON/CSV | Requerida |

### Detecciones y Validación

| Endpoint | Método | Descripción | Rol Requerido |
|----------|--------|-------------|---------------|
| `/api/v1/analyses/{id}/detections` | GET | Detecciones de un análisis | User+ |
| `/api/v1/detections/{id}/validate` | PUT | Validar detección | Expert+ |
| `/api/v1/detections/pending` | GET | Detecciones pendientes | Expert+ |
| `/api/v1/detections/batch-validate` | POST | Validación por lotes | Expert+ |

### Reportes y Estadísticas

| Endpoint | Método | Descripción | Rol Requerido |
|----------|--------|-------------|---------------|
| `/api/v1/reports/statistics` | GET | Estadísticas generales | Analyst+ |
| `/api/v1/reports/quality-metrics` | GET | Métricas de calidad | Expert+ |
| `/api/v1/reports/validation-stats` | GET | Estadísticas de validación | Expert+ |

### Sistema y Monitoreo

| Endpoint | Método | Descripción | Autenticación |
|----------|--------|-------------|---------------|
| `/api/v1/health` | GET | Estado básico del sistema | No |
| `/api/v1/health/detailed` | GET | Estado detallado con dependencias | Admin |
| `/api/v1/system/info` | GET | Información del sistema | Admin |

## Esquemas de Datos

### Análisis de Imágenes
```json
{
  "id": 123,
  "image_path": "/uploads/image_20250117_123456.jpg",
  "user_id": 1,
  "total_detections": 3,
  "risk_level": "ALTO",
  "confidence_threshold": 0.5,
  "created_at": "2025-01-17T10:30:00Z",
  "processing_time_ms": 1250,
  "has_gps_data": true
}
```

### Detecciones con Geolocalización
```json
{
  "id": 456,
  "analysis_id": 123,
  "class_name": "Charcos/Cumulo de agua",
  "class_id": 2,
  "confidence": 0.87,
  "polygon_data": [[x1,y1], [x2,y2], ...],
  "mask_area": 1250.5,
  "location_data": {
    "has_location": true,
    "coordinates": "10.123456,-84.567890",
    "accuracy": "high",
    "source": "gps_exif"
  },
  "validation": {
    "is_validated": true,
    "expert_validation": true,
    "expert_notes": "Detección precisa",
    "validated_by": 5,
    "validated_at": "2025-01-17T11:00:00Z"
  }
}
```

## Desarrollo y Testing

### Estándares de Código

- **PEP 8** para estilo de código Python con formateo automático
- **Type hints** obligatorios en todas las funciones públicas
- **Docstrings** bilingües (español/inglés) para clases y métodos principales
- **Tests unitarios** con cobertura mínima del 85%
- **Logging estructurado** para monitoreo en producción

### Configuración de Base de Datos

```bash
# Crear nueva migración después de cambios en modelos
alembic revision --autogenerate -m "descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Ver historial de migraciones
alembic history
```

### Ejecución de Tests

```bash
# Suite completa de tests
python run_tests.py

# Tests por categoría
pytest tests/unit/ -v                    # Tests unitarios
pytest tests/integration/ -v             # Tests de integración
pytest tests/test_complete_system.py -v  # Test del sistema completo

# Tests con cobertura
pytest --cov=src tests/ --cov-report=html

# Tests de integración YOLO (requiere servicio activo)
pytest tests/test_yolo_integration.py -v
```

**Tests incluidos:**
- Verificación de modelos de base de datos y relaciones
- Validación de endpoints API con autenticación
- Tests de integración con YOLO service
- Pruebas de procesamiento por lotes
- Validación de extracción de metadatos GPS
- Tests de sistema completo end-to-end

## Despliegue

### Entorno de Desarrollo

```bash
# Usando el servidor de desarrollo FastAPI
python run_server.py

# Con auto-reload habilitado
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Producción con Docker

```dockerfile
# Dockerfile incluido en el proyecto
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

```bash
# Construir y ejecutar
docker build -t sentrix-backend .
docker run -p 8000:8000 --env-file .env sentrix-backend
```

### Producción con Gunicorn

```bash
# Instalar Gunicorn si no está en requirements.txt
pip install gunicorn

# Ejecutar con múltiples workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Con configuración avanzada
gunicorn app.main:app --config gunicorn.conf.py
```

## Monitoreo y Observabilidad

### Health Checks Automáticos
- **Endpoint básico**: `/api/v1/health` - Estado rápido sin autenticación
- **Endpoint detallado**: `/api/v1/health/detailed` - Estado completo con dependencias
- **Verificación de servicios**: Base de datos, Redis, YOLO service
- **Métricas de rendimiento**: Tiempos de respuesta y uso de recursos

### Logging Estructurado
```python
# Configuración de logs en producción
{
  "timestamp": "2025-01-17T10:30:00Z",
  "level": "INFO",
  "service": "sentrix-backend",
  "endpoint": "/api/v1/analyses",
  "user_id": 123,
  "processing_time_ms": 1250,
  "detections_found": 3
}
```

### Métricas de Negocio
- **Análisis procesados por día/hora**
- **Distribución de niveles de riesgo**
- **Precisión del sistema (validaciones de expertos)**
- **Tiempo promedio de procesamiento**
- **Cobertura de validación por expertos**

## Configuración

### Variables de Entorno Completas

```bash
# Base de datos
DATABASE_URL=postgresql://user:pass@localhost:5432/sentrix
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Servicios externos
YOLO_SERVICE_URL=http://localhost:8001
YOLO_SERVICE_TIMEOUT=30
REDIS_URL=redis://localhost:6379
REDIS_TTL=3600

# Autenticación
SUPABASE_URL=https://project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
JWT_SECRET_KEY=your-super-secret-key
JWT_EXPIRATION_HOURS=24

# API Configuration
DEBUG=false
SECRET_KEY=production-secret-key
CORS_ORIGINS=["https://app.sentrix.com", "https://admin.sentrix.com"]
RATE_LIMIT_PER_MINUTE=100

# File uploads
UPLOAD_DIR=/var/uploads/sentrix
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=["jpg", "jpeg", "png", "tiff"]

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/sentrix/backend.log
```

### Configuración de Settings (configs/settings.py)

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str
    database_pool_size: int = 10

    # External services
    yolo_service_url: str
    redis_url: str

    # Authentication
    supabase_url: str
    supabase_key: str
    jwt_secret_key: str

    class Config:
        env_file = ".env"
```

## Integración con Plataforma Sentrix

Este backend forma parte de una arquitectura de microservicios integrada:

### Servicios Conectados
- **[YOLO Service](../yolo-service/)** - Núcleo de IA para detección de criaderos
- **Frontend Mobile** - Aplicación móvil React Native para ciudadanos
- **Dashboard Web** - Panel de administración y análisis para expertos
- **API Gateway** - Balanceador de carga y gestión de tráfico

### Flujo de Datos
1. **Captura** - Imágenes desde app móvil o dashboard web
2. **Procesamiento** - Backend coordina análisis con YOLO service
3. **Almacenamiento** - Resultados con geolocalización en PostgreSQL/PostGIS
4. **Validación** - Expertos revisan detecciones de alto riesgo
5. **Reportes** - Estadísticas epidemiológicas y métricas de calidad

### APIs de Integración
- **REST API** para frontend web y móvil
- **GraphQL endpoint** para consultas complejas (futuro)
- **WebSocket** para notificaciones en tiempo real
- **Webhook** para integración con sistemas externos

## Solución de Problemas Comunes

### Verificación de Estado del Sistema
```python
from src.utils import get_system_info, validate_connection
from src.core.services.yolo_service import YOLOServiceClient

# Verificar base de datos
db_info = get_system_info()
print(f"Base de datos: {'✓' if db_info['connection_valid'] else '❌'}")

# Verificar YOLO service
yolo_client = YOLOServiceClient()
yolo_status = await yolo_client.health_check()
print(f"YOLO Service: {'✓' if yolo_status else '❌'}")
```

### Problemas de Conexión
```bash
# Verificar conectividad con dependencias
python -c "
from src.database.connection import test_connection
from src.utils.database_utils import validate_connection
print('DB Connection:', test_connection())
print('DB Validation:', validate_connection())
"
```

### Migración desde Versión Anterior
Si tienes una versión anterior del backend:

1. **Backup de datos**:
```bash
pg_dump sentrix > backup_$(date +%Y%m%d).sql
```

2. **Actualizar imports**:
```python
# Anterior
from app.models import Analysis
from app.services.yolo_service import YOLOServiceClient

# Nuevo
from src.database.models import Analysis
from src.core.services.yolo_service import YOLOServiceClient
```

3. **Ejecutar migraciones**:
```bash
python run_migrations.py
```

4. **Verificar integridad**:
```bash
python tests/test_complete_system.py
```

## Especificaciones de Rendimiento

### Configuraciones de Hardware Recomendadas

| Componente | Desarrollo | Producción | Alta Carga |
|------------|-----------|------------|------------|
| **CPU** | 4 cores | 8 cores | 16+ cores |
| **RAM** | 8GB | 16GB | 32GB+ |
| **Storage** | SSD 50GB | SSD 200GB | NVMe 500GB+ |
| **Network** | 100 Mbps | 1 Gbps | 10 Gbps |
| **PostgreSQL** | Local | Dedicado 4GB RAM | Cluster |

### Métricas de Rendimiento Esperadas

| Operación | Desarrollo | Producción | Notas |
|-----------|------------|------------|-------|
| **Análisis individual** | 2-5 segundos | 1-3 segundos | Incluye YOLO + BD |
| **Procesamiento por lotes** (10 imágenes) | 15-30 segundos | 10-20 segundos | Paralelo |
| **Consulta análisis** | <100ms | <50ms | Con índices |
| **Validación experto** | <200ms | <100ms | Operación simple |
| **Generación reporte** | 1-2 segundos | <1 segundo | Consultas agregadas |

### Límites y Capacidades

- **Análisis simultáneos**: 50 (desarrollo) / 500+ (producción)
- **Usuarios concurrentes**: 100 (desarrollo) / 1000+ (producción)
- **Tamaño máximo imagen**: 50MB por defecto
- **Retención de datos**: 2 años (configurable)
- **Backup automático**: Diario (producción)

---

**Versión**: 2.0.0 - Backend Integrado de la Plataforma Sentrix
**Estado**: Fase 1 Completa - Integración con YOLO Service activa
**Próximas fases**: GraphQL API, WebSocket notifications, Analytics avanzado
**Última actualización**: Enero 2025