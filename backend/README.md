# Sentrix Backend - API REST y Sistema de Gestión

Backend principal de la plataforma Sentrix que proporciona APIs REST para la gestión completa de análisis epidemiológicos de *Aedes aegypti* mediante inteligencia artificial.

## Descripción

Este servicio constituye el **núcleo backend** de la plataforma Sentrix, proporcionando una infraestructura escalable para:

- **Análisis de imágenes con IA** - Integración con servicio YOLO para detección de criaderos
- **Gestión georreferenciada** - Almacenamiento de detecciones con coordenadas GPS
- **Validación por expertos** - Sistema de revisión y aseguramiento de calidad
- **Autenticación y usuarios** - Gestión de roles y permisos
- **Reportes epidemiológicos** - Análisis estadístico y métricas de riesgo

## Arquitectura

### Estructura del Proyecto

```
backend/
├── app/                    # Aplicación FastAPI principal
│   ├── api/v1/            # Endpoints de API REST
│   │   ├── analyses.py    # Gestión de análisis
│   │   ├── auth.py        # Autenticación y usuarios
│   │   ├── health.py      # Health checks
│   │   └── reports.py     # Reportes y estadísticas
│   ├── models/            # Modelos de datos
│   ├── schemas/           # Esquemas Pydantic
│   └── services/          # Lógica de negocio
├── src/                   # Código fuente core
│   ├── database/          # Modelos SQLAlchemy y configuración
│   ├── schemas/           # Esquemas de validación
│   └── utils/             # Utilidades y integraciones
├── config/                # Configuración centralizada
├── scripts/               # Scripts de utilidad
├── tests/                 # Tests automatizados
└── alembic/              # Migraciones de base de datos
```

### Tecnologías Principales

- **FastAPI** - Framework web moderno con documentación automática
- **SQLAlchemy** - ORM para manejo de base de datos
- **Supabase** - Base de datos PostgreSQL en la nube
- **Alembic** - Migraciones de base de datos
- **Pydantic** - Validación de datos y serialización

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
alembic upgrade head

# Ejecutar servidor de desarrollo
python scripts/run_server.py
```

## API Endpoints

### Autenticación
- `POST /api/v1/auth/register` - Registro de usuarios
- `POST /api/v1/auth/login` - Inicio de sesión
- `POST /api/v1/auth/refresh` - Renovar token

### Análisis
- `POST /api/v1/analyses` - Crear nuevo análisis
- `GET /api/v1/analyses` - Listar análisis
- `GET /api/v1/analyses/{id}` - Obtener análisis específico
- `POST /api/v1/analyses/batch` - Análisis por lotes

### Reportes
- `GET /api/v1/reports/statistics` - Estadísticas generales
- `GET /api/v1/reports/risk-assessment` - Evaluación de riesgo
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

# Utilidades de archivos
from shared.file_utils import validate_image_file

# Logging centralizado
from shared.logging_utils import setup_backend_logging
```

## Base de Datos

### Tablas Principales

- **user_profiles** - Usuarios y roles del sistema
- **analyses** - Análisis de imágenes realizados
- **detections** - Detecciones individuales encontradas

### Enums Unificados

- `DetectionRiskEnum` - Niveles de riesgo (ALTO, MEDIO, BAJO, MINIMO)
- `BreedingSiteTypeEnum` - Tipos de criaderos
- `ValidationStatusEnum` - Estados de validación
- `UserRoleEnum` - Roles de usuario

## Desarrollo

### Ejecutar Tests

```bash
# Tests básicos
python -m pytest tests/test_simple.py -v

# Tests de API
python -m pytest tests/test_api_endpoints.py -v

# Tests de integración
python -m pytest tests/ -v
```

### Servidor de Desarrollo

```bash
# Iniciar servidor (puerto 8000)
python scripts/run_server.py

# Documentación API disponible en:
# http://localhost:8000/docs
```

### Scripts Útiles

- `scripts/run_server.py` - Servidor de desarrollo
- `scripts/setup_development.py` - Configuración inicial
- `scripts/run_tests.py` - Ejecutor de tests

## Configuración de Puertos

- **Backend API**: Puerto 8000
- **YOLO Service**: Puerto 8001 (configurado automáticamente)
- **Frontend**: Puerto 3000

## Documentación Adicional

- [Convenciones de Imports](../shared/IMPORT_CONVENTIONS.md)
- [Configuración de Entorno](../scripts/setup-env.py)
- [Tests de Integración](../scripts/simple-validation.py)