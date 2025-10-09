# Backend API - Sentrix

API REST basada en FastAPI para la plataforma Sentrix, que proporciona servicios backend para detección y análisis de criaderos de Aedes aegypti.

## Descripción General

El backend de Sentrix es el servidor principal que coordina el análisis de imágenes con inteligencia artificial, gestión de usuarios, persistencia de datos y evaluación de riesgo epidemiológico. Se integra con el servicio de detección YOLO y provee una API REST completa para la aplicación frontend.

### Funcionalidades Principales

- **Análisis con IA** - Integración con el servicio YOLO para detección automatizada de criaderos
- **Almacenamiento Dual** - Guardado automático de imágenes originales y procesadas con marcadores de detección
- **Deduplicación Inteligente** - Detección de contenido duplicado basada en hash para optimizar almacenamiento
- **Nomenclatura Estandarizada** - Sistema de nombres de archivo profesional con metadatos codificados
- **Datos Geoespaciales** - Extracción automática de GPS y almacenamiento con PostGIS
- **Gestión de Usuarios** - Autenticación basada en roles (USER, ADMIN, EXPERT)
- **Validación por Expertos** - Flujo de trabajo para verificación de detecciones
- **Generación de Reportes** - Exportación a PDF y CSV con filtros personalizables
- **Limitación de Tasa** - Protección contra abuso de recursos

## Arquitectura

### Stack Tecnológico

| Componente | Tecnología | Propósito |
|-----------|-----------|-----------|
| **Framework** | FastAPI 0.104+ | Framework web asincrónico de alto rendimiento |
| **Base de Datos** | PostgreSQL 14+ | Almacenamiento principal con extensión PostGIS |
| **ORM** | SQLAlchemy 2.0+ | Modelado y consultas de base de datos |
| **Storage** | Supabase Storage | Almacenamiento en la nube para imágenes |
| **Autenticación** | JWT (python-jose) | Autenticación basada en tokens |
| **Validación** | Pydantic 2.0+ | Validación de requests/responses |
| **Imágenes** | Pillow 11+ | Extracción de metadatos EXIF |
| **Testing** | pytest | Testing unitario e integración |

### Estructura del Proyecto

```
backend/
├── app.py                      # Punto de entrada de la aplicación
├── main.py                     # Punto de entrada alternativo
├── requirements.txt            # Dependencias Python
├── pytest.ini                  # Configuración de tests
├── Dockerfile                  # Definición de imagen Docker
│
├── src/                        # Código fuente
│   ├── __init__.py
│   ├── config.py              # Configuración de la app
│   │
│   ├── api/                   # Rutas de API
│   │   └── v1/               # API versión 1
│   │       ├── analyses.py   # Endpoints de análisis
│   │       ├── auth.py       # Endpoints de autenticación
│   │       ├── detections.py # Endpoints de detecciones
│   │       ├── reports.py    # Generación de reportes
│   │       └── users.py      # Gestión de usuarios
│   │
│   ├── core/                  # Funcionalidad central
│   │   ├── security.py       # Utilidades de seguridad
│   │   └── storage.py        # Integración con storage
│   │
│   ├── database/              # Capa de base de datos
│   │   ├── connection.py     # Gestión de conexiones
│   │   ├── base.py           # Base de SQLAlchemy
│   │   ├── models/           # Modelos ORM
│   │   │   ├── models.py     # Modelos principales
│   │   │   └── enums.py      # Enums de BD
│   │   └── migrations/       # Migraciones Alembic
│   │
│   ├── schemas/               # Schemas Pydantic
│   │   ├── analyses.py       # Schemas de análisis
│   │   ├── auth.py           # Schemas de autenticación
│   │   ├── detections.py     # Schemas de detecciones
│   │   ├── reports.py        # Schemas de reportes
│   │   ├── settings.py       # Schemas de configuración
│   │   └── users.py          # Schemas de usuarios
│   │
│   ├── services/              # Lógica de negocio
│   │   ├── analysis_service.py    # Operaciones de análisis
│   │   ├── report_service.py      # Generación de reportes
│   │   ├── storage_service.py     # Almacenamiento de archivos
│   │   ├── supabase_manager.py    # Integración Supabase
│   │   └── user_service.py        # Operaciones de usuarios
│   │
│   ├── middleware/            # Middleware HTTP
│   │   ├── cors.py           # Configuración CORS
│   │   └── rate_limit.py     # Limitación de tasa
│   │
│   └── utils/                 # Utilidades
│       ├── auth.py           # Helpers de autenticación
│       ├── config_validator.py    # Validación de config
│       └── helpers.py        # Utilidades generales
│
├── tests/                     # Suite de tests
├── alembic/                   # Migraciones de BD
├── logs/                      # Logs de aplicación
├── uploads/                   # Subidas temporales
└── data/                      # Datos de runtime
```

## Instalación

### Requisitos Previos

- Python 3.8 o superior (se recomienda 3.9+)
- PostgreSQL 14+ con extensión PostGIS
- Cuenta de Supabase (o instalación local de Supabase)
- Acceso al servicio YOLO (ejecutándose en puerto 8001)

### Pasos de Configuración

1. **Crear entorno virtual**
   ```bash
   python -m venv venv

   # Windows
   .\venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**

   Crear archivo `.env` en la raíz del proyecto (un nivel arriba de `backend/`):

   ```bash
   # Configuración del Servidor
   BACKEND_PORT=8000
   ENVIRONMENT=development

   # Base de Datos
   DATABASE_URL=postgresql://user:password@localhost:5432/sentrix

   # Supabase
   SUPABASE_URL=https://tu-proyecto.supabase.co
   SUPABASE_KEY=tu-service-role-key
   SUPABASE_ANON_KEY=tu-anon-key

   # Seguridad
   SECRET_KEY=tu-clave-secreta-minimo-32-caracteres
   JWT_SECRET_KEY=tu-clave-jwt
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   REFRESH_TOKEN_EXPIRE_DAYS=7

   # Servicio YOLO
   YOLO_SERVICE_URL=http://localhost:8001
   YOLO_SERVICE_PORT=8001

   # Almacenamiento
   MAX_UPLOAD_SIZE_MB=10
   ALLOWED_IMAGE_EXTENSIONS=.jpg,.jpeg,.png,.heic,.tiff,.webp
   ```

4. **Inicializar base de datos**

   Ejecutar el script de creación de schema:
   ```bash
   psql -U postgres -d sentrix -f ../supabase-schema.sql
   ```

   O usar migraciones de Alembic:
   ```bash
   alembic upgrade head
   ```

5. **Ejecutar la aplicación**
   ```bash
   # Modo desarrollo con auto-reload
   python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000

   # O usando el script
   python app.py
   ```

6. **Verificar instalación**

   - Documentación API: http://localhost:8000/docs
   - Health check: http://localhost:8000/health
   - Verificación YOLO: http://localhost:8000/health/yolo

## Configuración

### Variables de Entorno

#### Variables Requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | String de conexión PostgreSQL | `postgresql://user:pass@localhost:5432/sentrix` |
| `SUPABASE_URL` | URL del proyecto Supabase | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | Service role key de Supabase | `eyJhbG...` |
| `SECRET_KEY` | Clave secreta de aplicación (32+ chars) | Generada de forma segura |
| `JWT_SECRET_KEY` | Clave para firmar JWT | Generada de forma segura |

#### Variables Opcionales

| Variable | Por Defecto | Descripción |
|----------|-------------|-------------|
| `BACKEND_PORT` | `8000` | Puerto del servidor |
| `ENVIRONMENT` | `development` | Nombre del entorno |
| `YOLO_SERVICE_URL` | `http://localhost:8001` | Endpoint del servicio YOLO |
| `MAX_UPLOAD_SIZE_MB` | `10` | Tamaño máximo de subida |
| `LOG_LEVEL` | `INFO` | Nivel de logging |
| `RATE_LIMIT_ENABLED` | `true` | Activar limitación de tasa |

### Configuración de Base de Datos

El backend usa PostgreSQL con PostGIS para datos geoespaciales. El schema incluye:

#### Tablas

**user_profiles** - Cuentas de usuario y autenticación
- Campos: `id`, `email`, `hashed_password`, `role`, `display_name`, `organization`, `is_active`, `is_verified`, `created_at`, `updated_at`, `last_login`

**user_settings** - Preferencias de usuario (almacenamiento JSON)
- Campos: `id`, `user_id`, `settings` (JSONB), `created_at`, `updated_at`

**analyses** - Registros de análisis de imágenes
- Campos: `id`, `user_id`, `image_url`, `processed_image_url`, `image_filename`, `total_detections`, `high_risk_count`, `medium_risk_count`, `low_risk_count`, `risk_level`, `risk_score`, `confidence_threshold`, `processing_time_ms`, `has_gps_data`, `latitude`, `longitude`, `altitude_meters`, `location_source`, `content_hash`, `is_duplicate_reference`, `duplicate_of_analysis_id`, `created_at`

**detections** - Detecciones individuales dentro de análisis
- Campos: `id`, `analysis_id`, `breeding_site_type`, `risk_level`, `confidence`, `validated_by`, `validation_status`, `validation_notes`, `polygon_coordinates`, `mask_area_pixels`, `created_at`, `validated_at`

#### Enums

- `user_role_enum` - USER, ADMIN, EXPERT
- `detection_risk_enum` - ALTO, MEDIO, BAJO, MINIMO
- `breeding_site_type_enum` - Basura, Calles mal hechas, Charcos/Cumulo de agua, Huecos
- `validation_status_enum` - pending_validation, validated_positive, validated_negative, requires_review
- `location_source_enum` - EXIF_GPS, MANUAL, ESTIMATED

## Documentación de la API

### Endpoints de Autenticación

#### Registrar Usuario
```http
POST /api/v1/register
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "password": "ClaveSegura123!",
  "display_name": "Juan Pérez"
}
```

#### Iniciar Sesión
```http
POST /api/v1/token
Content-Type: application/x-www-form-urlencoded

username=usuario@ejemplo.com&password=ClaveSegura123!
```

Respuesta:
```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "usuario@ejemplo.com",
    "role": "USER"
  }
}
```

#### Obtener Usuario Actual
```http
GET /api/v1/me
Authorization: Bearer <token>
```

### Endpoints de Análisis

#### Crear Análisis
```http
POST /api/v1/analyses
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <archivo de imagen>
confidence_threshold: 0.5 (opcional)
latitude: -34.603722 (opcional)
longitude: -58.381592 (opcional)
include_gps: true (opcional)
```

#### Listar Análisis
```http
GET /api/v1/analyses?limit=10&offset=0&risk_level=ALTO
Authorization: Bearer <token>
```

#### Obtener Detalles de Análisis
```http
GET /api/v1/analyses/{analysis_id}
Authorization: Bearer <token>
```

### Endpoints de Reportes

#### Generar Reporte
```http
POST /api/v1/reports/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "type": "summary",
  "format": "pdf",
  "date_from": "2024-01-01T00:00:00Z",
  "date_to": "2024-12-31T23:59:59Z",
  "filters": {
    "risk_level": "ALTO",
    "has_gps": true
  }
}
```

### Gestión de Usuarios (Solo Admin/Expert)

#### Listar Usuarios
```http
GET /api/v1/users
Authorization: Bearer <admin_token>
```

#### Actualizar Rol de Usuario
```http
PUT /api/v1/users/{user_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "role": "EXPERT"
}
```

## Funcionalidades Clave

### 1. Nomenclatura Estandarizada de Archivos

Cada imagen subida se renombra automáticamente usando un formato estandarizado que codifica metadatos:

```
SENTRIX_YYYYMMDD_HHMMSS_DISPOSITIVO_UBICACION_ID.ext
```

**Ejemplo:**
```
SENTRIX_20241008_143052_IPHONE15_LATn34p604_LONn58p382_a1b2c3d4.jpg
```

**Componentes:**
- `SENTRIX` - Identificador del proyecto
- `20241008_143052` - Timestamp del análisis (YYYYMMDD_HHMMSS)
- `IPHONE15` - Dispositivo detectado desde datos EXIF
- `LATn34p604_LONn58p382` - Coordenadas GPS codificadas
- `a1b2c3d4` - Hash único de 8 caracteres
- `.jpg` - Extensión del archivo original

Beneficios:
- Identificación instantánea del origen del archivo
- Ordenamiento por fecha
- Datos de ubicación embebidos
- Unicidad garantizada
- Aspecto profesional

### 2. Almacenamiento Dual de Imágenes

Para cada análisis se almacenan dos imágenes:

**Imagen Original** (`original_SENTRIX_...jpg`)
- Archivo sin modificaciones para análisis futuros
- Metadatos EXIF preservados

**Imagen Procesada** (`processed_SENTRIX_...jpg`)
- Con polígonos azules alrededor de los sitios detectados
- Etiquetas de clase y scores de confianza
- Generada automáticamente por el servicio YOLO

### 3. Deduplicación Inteligente

El sistema detecta automáticamente imágenes duplicadas usando hashing basado en contenido:

**Método de Detección:**
- Hash SHA-256 de datos binarios de imagen
- Comparación de metadatos EXIF (cámara, timestamp)
- Scoring de similitud de coordenadas GPS

**Optimización de Almacenamiento:**
- Imágenes duplicadas crean solo referencias en base de datos
- Sin almacenamiento redundante de archivos
- Tracking de métrica `storage_saved_bytes`
- Historial completo de análisis mantenido

**Ejemplo:**
```python
# Primera subida - almacena archivo
Análisis 1: content_hash=abc123, is_duplicate_reference=False

# Subida duplicada - solo referencia
Análisis 2: content_hash=abc123, is_duplicate_reference=True,
            duplicate_of_analysis_id=<analysis_1_id>
```

### 4. Funcionalidades Geoespaciales

**Extracción Automática de GPS:**
- Lee tags GPS de EXIF de las imágenes
- Almacena como tipo Geography de PostGIS
- Soporta entrada manual de coordenadas
- Trackea fuente de ubicación (EXIF_GPS, MANUAL, ESTIMATED)

**Consultas Espaciales:**
```python
# Encontrar análisis cerca de una ubicación
analyses_nearby = db.query(Analysis).filter(
    func.ST_DWithin(
        Analysis.location,
        func.ST_MakePoint(longitude, latitude),
        1000  # metros
    )
).all()
```

### 5. Control de Acceso Basado en Roles

Tres roles de usuario con diferentes permisos:

| Rol | Permisos |
|------|-------------|
| **USER** | Crear análisis, ver datos propios, generar reportes personales |
| **EXPERT** | Todos los permisos USER + validar detecciones, acceso a cola de validación |
| **ADMIN** | Todos los permisos + gestión de usuarios, configuración del sistema |

**Implementación:**
```python
from src.utils.auth import require_role

@router.get("/admin/stats")
async def admin_stats(current_user = Depends(require_role(["ADMIN"]))):
    # Solo admins pueden acceder
    ...
```

### 6. Flujo de Validación por Expertos

Las detecciones pueden ser validadas por expertos para aseguramiento de calidad:

**Estados de Validación:**
- `pending_validation` - Esperando revisión de experto
- `validated_positive` - Confirmada como detección correcta
- `validated_negative` - Falso positivo, rechazada
- `requires_review` - Necesita atención adicional de experto

**Flujo de Trabajo:**
```
1. Usuario sube imagen → Análisis creado
2. YOLO detecta sitios → Detecciones con pending_validation
3. Experto revisa → Actualiza validation_status
4. Sistema trackea → validated_by, validation_notes, validated_at
```

## Desarrollo

### Ejecutar Tests

```bash
# Ejecutar todos los tests con cobertura
pytest tests/ -v --cov=src --cov-report=html

# Ejecutar archivo específico de test
pytest tests/test_analyses.py -v

# Ejecutar con marcador específico
pytest tests/ -v -m "integration"

# Script de conveniencia Windows
.\run_tests.ps1

# Script de conveniencia Linux/Mac
./run_tests.sh
```

### Calidad de Código

```bash
# Formatear código
black src/ tests/

# Linting
ruff check src/ tests/

# Type checking (si se usa mypy)
mypy src/
```

### Migraciones de Base de Datos

```bash
# Crear nueva migración
alembic revision --autogenerate -m "Descripción de cambios"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Ver historial de migraciones
alembic history

# Ver versión actual
alembic current
```

### Debugging

```bash
# Ejecutar con logging de debug
LOG_LEVEL=DEBUG python -m uvicorn app:app --reload

# Usar herramienta de diagnóstico
python diagnostic.py
```

La herramienta de diagnóstico proporciona:
- Información del sistema (OS, versión Python, memoria)
- Estado de conexión a base de datos
- Conectividad con servicio YOLO
- Validación de variables de entorno
- Verificación de disponibilidad de puertos
- Verificación de dependencias

## Deployment

### Deployment con Docker

```bash
# Construir imagen
docker build -t sentrix-backend -f Dockerfile .

# Ejecutar contenedor
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name sentrix-backend \
  sentrix-backend
```

### Configuraciones por Entorno

**Desarrollo:**
```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Producción:**
```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://tudominio.com
RATE_LIMIT_ENABLED=true
```

## Solución de Problemas

### Problemas Comunes

**Problema:** `ModuleNotFoundError: No module named 'shared'`

**Solución:** Asegurar que el directorio `shared/` esté en el directorio padre y el Python path esté configurado:
```python
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
```

**Problema:** Errores de conexión a base de datos

**Solución:**
1. Verificar que PostgreSQL esté ejecutándose
2. Revisar formato de `DATABASE_URL`
3. Asegurar que la base de datos exista: `createdb sentrix`
4. Probar conexión: `psql <DATABASE_URL>`

**Problema:** Servicio YOLO no responde

**Solución:**
1. Verificar que servicio YOLO esté ejecutándose: `curl http://localhost:8001/health`
2. Revisar `YOLO_SERVICE_URL` en `.env`
3. Revisar logs del servicio YOLO

**Problema:** Errores de rate limit

**Solución:** Deshabilitar temporalmente o ajustar límites:
```bash
RATE_LIMIT_ENABLED=false
# O aumentar límites en src/middleware/rate_limit.py
```

## Optimización de Rendimiento

### Optimización de Base de Datos

- Usar connection pooling (configurado en SQLAlchemy)
- Crear índices en columnas consultadas frecuentemente
- Usar `EXPLAIN ANALYZE` para optimizar consultas lentas
- Considerar réplicas de lectura para tráfico pesado

### Optimización de Almacenamiento

- Activar deduplicación (por defecto)
- Implementar compresión de imágenes para thumbnails
- Usar CDN para imágenes accedidas frecuentemente
- Configurar políticas de lifecycle para archivos antiguos

### Rendimiento de API

- Activar caché de respuestas para endpoints de lectura pesada
- Usar endpoints asincrónicos para operaciones I/O
- Implementar paginación para conjuntos de resultados grandes
- Usar optimización de consultas de base de datos (evitar N+1 queries)

## Integración con Otros Servicios

### Servicio YOLO

El backend se comunica con el servicio YOLO para análisis de imágenes:

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        f"{YOLO_SERVICE_URL}/detect",
        files={"file": image_bytes},
        data={"confidence_threshold": 0.5}
    )
    result = response.json()
```

### Supabase Storage

Las imágenes se almacenan en buckets de Supabase Storage:

- `sentrix-images` - Imágenes originales
- `sentrix-processed` - Imágenes procesadas con marcadores

```python
from src.services.supabase_manager import SupabaseManager

manager = SupabaseManager()
url = manager.upload_image(file_bytes, filename, bucket="sentrix-images")
```

### Librería Compartida

Funcionalidad común se importa desde la librería compartida:

```python
from shared.data_models import DetectionRiskEnum, UserRoleEnum
from shared.risk_assessment import assess_dengue_risk
from shared.file_utils import generate_standardized_filename
from shared.image_deduplication import check_image_duplicate
```

## Licencia

Este proyecto está licenciado bajo la Licencia MIT.

---

**Versión:** 2.5.0
**Python:** 3.8+
**Estado:** Listo para Producción
**Última Actualización:** Octubre 2024
