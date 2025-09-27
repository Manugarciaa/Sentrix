# Sentrix Backend - API REST y Sistema de Gestión

Backend principal de la plataforma Sentrix que proporciona APIs REST para la gestión completa de análisis epidemiológicos de *Aedes aegypti* mediante inteligencia artificial.

## Descripción

Este servicio constituye el **núcleo backend** de la plataforma Sentrix, proporcionando una infraestructura escalable para:

- **Análisis de imágenes con IA** - Integración con servicio YOLO para detección de criaderos
- **Gestión georreferenciada** - Almacenamiento de detecciones con coordenadas GPS
- **Sistema de Nomenclatura Estandarizada** - Archivos con formato profesional y trazabilidad
- **Almacenamiento Dual Inteligente** - Imágenes originales y procesadas con marcadores
- **Deduplicación Automática** - Prevención de overflow con detección de contenido duplicado
- **Validación por expertos** - Sistema de revisión y aseguramiento de calidad
- **Autenticación y usuarios** - Gestión de roles y permisos
- **Reportes epidemiológicos** - Análisis estadístico y métricas de riesgo

## Arquitectura

### Estructura del Proyecto

```
backend/
├── app.py                 # Punto de entrada FastAPI
├── main.py                # CLI avanzado (DB, análisis)
├── src/                   # Código fuente unificado
│   ├── api/v1/           # Endpoints REST
│   │   ├── analyses.py   # Análisis de imágenes
│   │   ├── auth.py       # Autenticación
│   │   ├── health.py     # Health checks
│   │   └── reports.py    # Reportes
│   ├── services/         # Lógica de negocio
│   ├── schemas/          # Validación Pydantic
│   ├── database/         # Modelos + conexión
│   ├── utils/            # Utilidades
│   └── core/             # Funcionalidad central
├── testing/              # Scripts de testing
├── scripts/              # Scripts de producción
└── alembic/              # Migraciones DB
```

### Tecnologías Principales

- **FastAPI** - Framework web moderno con documentación automática
- **SQLAlchemy** - ORM para manejo de base de datos
- **Supabase** - Base de datos PostgreSQL + Storage en la nube
- **Alembic** - Migraciones de base de datos
- **Pydantic** - Validación de datos y serialización
- **Shared Library** - Sistema unificado de nomenclatura y deduplicación

## Configuración

### Variables de Entorno

Copia `.env.example` a `.env` y configura:

```bash
# Configuración de puertos
BACKEND_PORT=8000
YOLO_SERVICE_PORT=8001

# Base de datos
DATABASE_URL=postgresql://user:pass@localhost:5432/sentrix
SUPABASE_URL=tu_url_de_supabase
SUPABASE_KEY=tu_clave_de_supabase

# Seguridad
SECRET_KEY=tu_clave_secreta
JWT_SECRET_KEY=tu_clave_jwt

# Servicios externos
YOLO_SERVICE_URL=http://localhost:8001
```

### Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
python main.py db migrate

# Ejecutar servidor de desarrollo
python app.py
```

## Funcionalidades Avanzadas

### Sistema de Nomenclatura Estandarizada
El backend implementa un sistema de nomenclatura profesional para todos los archivos:

```
SENTRIX_20250926_143052_IPHONE15_LATn34p604_LONn58p382_a1b2c3d4.jpg
```

**Componentes del nombre:**
- **SENTRIX**: Prefijo del proyecto
- **YYYYMMDD_HHMMSS**: Timestamp del análisis
- **DEVICE**: Dispositivo detectado automáticamente (IPHONE15, SAMSUNG, etc.)
- **LOCATION**: Coordenadas GPS codificadas o NOLOC
- **ID**: Hash único de 8 caracteres

### Almacenamiento Dual en Supabase
Cada análisis genera dos archivos:

1. **Imagen Original** (`original_SENTRIX_...jpg`)
   - Archivo sin modificaciones para análisis futuro
   - Metadatos EXIF preservados

2. **Imagen Procesada** (`processed_SENTRIX_...jpg`)
   - Con marcadores azules de detecciones YOLO
   - Generada automáticamente por el sistema

### Sistema de Deduplicación Inteligente
- **Detección por Contenido**: Hash SHA-256 de datos binarios
- **Referencias Automáticas**: Duplicados no almacenan archivos físicos
- **Scoring de Similitud**: Considera metadatos de cámara y GPS
- **Optimización Transparente**: Ahorro de storage sin pérdida de funcionalidad

## API Endpoints

### Autenticación
- `POST /api/v1/auth/register` - Registro de usuarios
- `POST /api/v1/auth/login` - Inicio de sesión
- `POST /api/v1/auth/refresh` - Renovar token

### Análisis
- `POST /api/v1/analyses` - Crear nuevo análisis con almacenamiento dual
- `GET /api/v1/analyses` - Listar análisis con información de deduplicación
- `GET /api/v1/analyses/{id}` - Obtener análisis específico
- `POST /api/v1/analyses/batch` - Análisis por lotes con optimización

### Reportes
- `GET /api/v1/reports/statistics` - Estadísticas generales
- `GET /api/v1/reports/risk-assessment` - Evaluación de riesgo
- `GET /api/v1/reports/deduplication` - Métricas de deduplicación y ahorro de storage
- `GET /api/v1/reports/export` - Exportar datos

### Health Check
- `GET /health` - Estado del servicio
- `GET /health/yolo` - Estado del servicio YOLO

## Integración con Shared Library

El backend utiliza la librería compartida para:

```python
# Importación de enums unificados
from shared.data_models import (
    DetectionRiskEnum,
    BreedingSiteTypeEnum,
    ValidationStatusEnum
)

# Evaluación de riesgo
from shared.risk_assessment import assess_dengue_risk

# Sistema de nomenclatura estandarizada
from shared.file_utils import (
    generate_standardized_filename,
    create_filename_variations,
    parse_standardized_filename
)

# Sistema de deduplicación
from shared.image_deduplication import (
    check_image_duplicate,
    calculate_content_signature,
    get_deduplication_manager
)

# Utilidades de archivos avanzadas
from shared.file_utils import validate_image_file

# Logging centralizado
from shared.logging_utils import setup_backend_logging
```

## Base de Datos

### Tablas Principales

- **user_profiles** - Usuarios y roles del sistema
- **analyses** - Análisis de imágenes realizados con nomenclatura estandarizada
- **detections** - Detecciones individuales encontradas
- **Campos de Deduplicación** - `content_hash`, `is_duplicate_reference`, `storage_saved_bytes`

### Enums Unificados

- `DetectionRiskEnum` - Niveles de riesgo (ALTO, MEDIO, BAJO, MINIMO)
- `BreedingSiteTypeEnum` - Tipos de criaderos
- `ValidationStatusEnum` - Estados de validación
- `UserRoleEnum` - Roles de usuario

## Desarrollo

### Ejecutar Tests

```bash
# Tests consolidados
cd testing && python run_tests.py

# Tests individuales
python -m pytest tests/ -v

# Tests específicos de nuevas funcionalidades
python scripts/simple_test.py           # Pruebas básicas
python scripts/test_deduplication.py    # Sistema de deduplicación
python scripts/quick_smoke_tests.py     # Verificación rápida
```

### Diagnóstico del Sistema

```bash
# Diagnóstico completo del backend
python diagnostic.py
```

**Información proporcionada:**
- Estado del sistema y recursos
- Variables de entorno configuradas
- Conexión con base de datos
- Conectividad con YOLO Service
- Estado de puertos y dependencias
- Estructura de archivos del proyecto

### Servidor de Desarrollo

```bash
# Método recomendado con uvicorn
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Documentación API: http://localhost:8000/docs
# Health check: http://localhost:8000/health
```

### CLI Avanzado

```bash
# Gestión de base de datos
python main.py db status
python main.py db migrate

# Análisis desde CLI
python main.py analyze imagen.jpg
python main.py batch directorio/
```

## Configuración de Puertos

- **Backend API**: Puerto 8000
- **YOLO Service**: Puerto 8001 (configurado automáticamente)
- **Frontend**: Puerto 3000

## Documentación Adicional

- [Scripts de Corrección](../scripts/README.md)
- [Convenciones de Imports](../shared/IMPORT_CONVENTIONS.md)
- [Librería Compartida](../shared/README.md)

---

## Actualizaciones Recientes (v2.3.0)

### Nuevas Funcionalidades Implementadas:
- **Sistema de Nomenclatura Estandarizada**: Archivos con formato profesional y trazabilidad completa
- **Almacenamiento Dual en Supabase**: Imágenes originales y procesadas con marcadores YOLO
- **Deduplicación Automática**: Prevención de overflow con referencias a contenido duplicado
- **AnalysisService Mejorado**: Integración completa con shared library y funcionalidades avanzadas

### Mejoras en API:
- **Endpoint de Análisis**: Retorna URLs de imágenes originales y procesadas
- **Reportes de Deduplicación**: Métricas de ahorro de storage y optimización
- **Integración YOLO**: Procesamiento automático con imágenes marcadas
- **Gestión de Metadatos**: Extracción y codificación de GPS, cámara y timestamps

### Optimizaciones de Storage:
- **Referencias Inteligentes**: Duplicados no almacenan archivos físicos
- **Nomenclatura Consistente**: Sistema unificado para todos los archivos
- **Trazabilidad Completa**: Seguimiento de origen y procesamiento de cada imagen
- **Ahorro Automático**: Optimización transparente sin pérdida de funcionalidad

### Estado Actual:
- **Backend funcionando** en puerto 8000 con funcionalidades avanzadas
- **Sistema de Storage** optimizado y operativo
- **Deduplicación** verificada y funcional
- **Integration** completa con shared library y YOLO Service

**El backend incluye ahora un sistema completo de gestión inteligente de imágenes con optimización automática de storage.**