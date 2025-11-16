# Stack Tecnológico - Backend Sentrix

Documentación completa de todas las herramientas, frameworks y librerías utilizadas en el backend del proyecto Sentrix.

---

## Core Framework

### FastAPI y ASGI
- **FastAPI** `0.116.1` - Framework web moderno y de alto rendimiento para construir APIs
- **Uvicorn** `0.35.0` - Servidor ASGI de alto rendimiento
- **email-validator** `2.3.0` - Validación de emails en Pydantic models

---

## Base de Datos

### PostgreSQL y ORM
- **SQLAlchemy** `2.0.23` - ORM (Object-Relational Mapping) para Python
- **Alembic** `1.16.5` - Herramienta de migración de base de datos
- **asyncpg** `0.29.0` - Driver asíncrono de PostgreSQL
- **psycopg2-binary** `2.9.9` - Driver PostgreSQL para Python

### Geoespacial (PostGIS)
- **GeoAlchemy2** `0.18.0` - Extensión de SQLAlchemy para tipos geoespaciales
- **Shapely** `2.0.2` - Manipulación y análisis de objetos geométricos
- **NumPy** `<2.0` - Computación científica (requerido por Shapely)

---

## Autenticación y Seguridad

### JWT y Encriptación
- **python-jose** `3.3.0` - Implementación de JOSE (JSON Object Signing and Encryption)
- **bcrypt** `4.0.1` - Hashing de contraseñas
- **python-multipart** `0.0.20` - Parsing de formularios multipart

### Rate Limiting y Validación
- **slowapi** `0.1.9` - Rate limiting para FastAPI
- **python-magic** `0.4.27` - Validación de tipos MIME
- **python-magic-bin** `0.4.14` - Binarios de libmagic para Windows

---

## Procesamiento de Imágenes y Archivos

### Imágenes
- **Pillow** `11.3.0` - Procesamiento y manipulación de imágenes
- **pillow-heif** `1.1.0` - Soporte para formatos HEIF/HEIC

### Generación de PDFs
- **ReportLab** `4.4.4` - Generación de documentos PDF

---

## Cliente HTTP y Resiliencia

### HTTP Client
- **httpx** `0.28.1` - Cliente HTTP asíncrono
- **tenacity** `8.2.3` - Reintentos con backoff exponencial
- **pybreaker** `1.2.0` - Implementación del patrón Circuit Breaker

---

## Integración con Servicios Externos

### Supabase
- **supabase** `2.19.0` - Cliente principal de Supabase
- **postgrest** `2.19.0` - Cliente para PostgREST API
- **storage3** `2.19.0` - Cliente para Supabase Storage
- **realtime** `2.19.0` - Suscripciones en tiempo real
- **supabase-auth** `2.19.0` - Autenticación de Supabase

---

## Logging y Observabilidad

### Structured Logging
- **structlog** `25.4.0` - Logging estructurado para Python
- **python-json-logger** `2.0.7` - Formateador JSON para logs

### OpenTelemetry (Distributed Tracing)
- **opentelemetry-api** `1.22.0` - API de OpenTelemetry
- **opentelemetry-sdk** `1.22.0` - SDK de OpenTelemetry
- **opentelemetry-instrumentation-fastapi** `0.43b0` - Instrumentación para FastAPI
- **opentelemetry-instrumentation-httpx** `0.43b0` - Instrumentación para httpx
- **opentelemetry-instrumentation-redis** `0.43b0` - Instrumentación para Redis
- **opentelemetry-instrumentation-sqlalchemy** `0.43b0` - Instrumentación para SQLAlchemy
- **opentelemetry-instrumentation-celery** `0.43b0` - Instrumentación para Celery
- **opentelemetry-exporter-otlp** `1.22.0` - Exportador OTLP
- **opentelemetry-exporter-jaeger** `1.22.0` - Exportador Jaeger

---

## Procesamiento Asíncrono

### Task Queue
- **Celery** `5.3.4` - Cola de tareas distribuida
- **Redis** `7.0.0` - Broker y backend para Celery, caching
- **hiredis** `3.3.0` - Parser de protocolo Redis de alto rendimiento
- **Flower** `2.0.1` - Monitoreo en tiempo real de Celery

---

## Configuración y Ambiente

### Environment Management
- **python-dotenv** `1.0.0` - Carga de variables de entorno desde archivos .env
- **pydantic-settings** `2.1.0` - Gestión de configuración con Pydantic

---

## Desarrollo y Testing

### Testing Framework
- **pytest** `8.4.1` - Framework de testing
- **pytest-asyncio** `1.2.0` - Soporte para tests asíncronos
- **pytest-cov** `7.0.0` - Plugin de cobertura de código
- **pytest-mock** `3.12.0` - Plugin para mocking
- **coverage** `7.10.6` - Medición de cobertura de código

### Code Quality
- **black** `25.9.0` - Formateador de código Python
- **ruff** `0.13.1` - Linter extremadamente rápido para Python

### System Utilities
- **psutil** `5.9.6` - Utilidades de sistema (CPU, memoria, procesos)

---

## Librería Compartida

### Sentrix Shared
- **sentrix_shared** (editable install) - Librería compartida entre backend y YOLO service
  - Utilidades de GPS
  - Modelos compartidos
  - Funciones comunes

---

## Infraestructura y Servicios

### Servicios Requeridos
- **PostgreSQL** `14+` con extensión **PostGIS** - Base de datos principal
- **Redis** `7.0+` - Cache y broker de Celery
- **YOLO Service** - Servicio de detección de objetos (puerto 8001)
- **Supabase** - Storage de imágenes y autenticación

### Herramientas de Desarrollo
- **Alembic** - Migraciones de base de datos
- **Flower** - Dashboard de monitoreo de Celery
- **OpenTelemetry Collector** (opcional) - Recolección de trazas
- **Jaeger** (opcional) - Visualización de trazas distribuidas

---

## Arquitectura de Patrones

### Patrones Implementados
- **Circuit Breaker** - Protección contra fallos en servicios externos (YOLO)
- **Retry Pattern** - Reintentos automáticos con backoff exponencial
- **Repository Pattern** - Abstracción de acceso a datos
- **Service Layer** - Lógica de negocio separada de endpoints
- **Dependency Injection** - Inyección de dependencias con FastAPI
- **JWT Authentication** - Autenticación stateless con tokens
- **Rate Limiting** - Limitación de requests por usuario
- **Structured Logging** - Logs estructurados en formato JSON

### Seguridad
- **CORS** configurado
- **JWT tokens** con refresh tokens
- **Password hashing** con bcrypt
- **Row Level Security (RLS)** en Supabase
- **MIME type validation** en uploads
- **Rate limiting** por usuario y endpoint

---

## Performance y Optimización

### Estrategias Implementadas
- **Async/Await** - Operaciones asíncronas en toda la aplicación
- **Connection Pooling** - Pool de conexiones a PostgreSQL
- **Redis Caching** - Cache de datos frecuentemente accedidos
- **Índices de base de datos** - Optimización de queries
- **Lazy Loading** - Carga diferida de relaciones
- **Batch Operations** - Operaciones en lote cuando es posible

---

## Versiones de Python

**Python** `3.9+` requerido

---

## Documentación y APIs

### Documentación Automática
- **Swagger UI** - Disponible en `/docs`
- **ReDoc** - Disponible en `/redoc`
- **OpenAPI Schema** - Generado automáticamente por FastAPI

---

**Última actualización:** Noviembre 2025
