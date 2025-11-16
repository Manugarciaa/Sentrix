# Sentrix - Sistema de Detección IA de Criaderos de Aedes aegypti

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![YOLO v11](https://img.shields.io/badge/YOLO-v11-brightgreen.svg)](https://github.com/ultralytics/ultralytics)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.2-61dafb.svg)](https://reactjs.org/)

Sistema de inteligencia artificial para detección automatizada de criaderos de *Aedes aegypti* (vector del dengue). Combina visión por computadora YOLOv11, evaluación de riesgo epidemiológico y geolocalización GPS.

---

## Quick Start

```bash
# 1. Clonar e instalar
git clone https://github.com/Manugarciaa/Sentrix.git
cd Sentrix
./scripts/install-all.sh  # o install-all.ps1 en Windows

# 2. Configurar entorno
cp .env.example .env
# Editar .env con tus credenciales

# 3. Iniciar servicios
./scripts/start-all.sh  # o start-all.ps1 en Windows
```

**Accesos:**
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs
- YOLO Service: http://localhost:8001/docs

---

## Arquitectura

<div align="center">

```mermaid
%%{init: {'theme':'neutral','themeVariables':{'fontSize':'13px'}}}%%
graph TB
    subgraph Client["Cliente"]
        UI[React Frontend<br/>:5173]
    end

    subgraph Services["Backend Services"]
        API[FastAPI Backend<br/>:8000]
        YOLO[YOLO Service<br/>:8001]
    end

    subgraph Data["Almacenamiento"]
        DB[(PostgreSQL<br/>+PostGIS)]
        S3[Supabase<br/>Storage]
        REDIS[(Redis<br/>Cache)]
    end

    UI-->|REST API|API
    API-->|Detección IA|YOLO
    API-->DB
    API-->S3
    API-->REDIS

    style UI fill:#1976d2,stroke:#333,color:#fff,stroke-width:2px
    style API fill:#00897b,stroke:#333,color:#fff,stroke-width:2px
    style YOLO fill:#43a047,stroke:#333,color:#fff,stroke-width:2px
    style DB fill:#5e35b1,stroke:#333,color:#fff,stroke-width:2px
    style S3 fill:#f4511e,stroke:#333,color:#fff,stroke-width:2px
    style REDIS fill:#d32f2f,stroke:#333,color:#fff,stroke-width:2px
```

</div>

---

## Screenshots

### Interfaz de Usuario

<div align="center">

<img src="./docs/imagenes/homepage.png" alt="Homepage" width="600"/>

*Página principal con información del proyecto y acceso al sistema*

<img src="./docs/imagenes/dashboard.png" alt="Dashboard" width="600"/>

*Vista del dashboard con estadísticas, filtros y visualización de análisis*

<img src="./docs/imagenes/upload_analisis_modal.png" alt="Upload Modal" width="600"/>

*Modal de carga de imágenes y procesamiento en tiempo real*

<img src="./docs/imagenes/analisispage.png" alt="Analysis Page" width="600"/>

*Vista detallada de análisis con detecciones, mapa y evaluación de riesgo*

</div>

### Tecnología: Detección con YOLOv11

<div align="center">

<img src="./docs/imagenes/figura_8_1_grid_detecciones.png" alt="YOLO Detections Grid" width="700"/>

*Ejemplos de detección de criaderos: charcos, basura, huecos y calles en mal estado con segmentación a nivel pixel*

</div>

---

## Características Principales

### Detección con IA
- **YOLOv11 Instance Segmentation**: Detección precisa a nivel pixel
- **4 Tipos de Criaderos**: Charcos, basura, huecos, calles mal hechas
- **GPU Accelerated**: Soporte CUDA para procesamiento rápido

### Geolocalización
- **Extracción GPS Automática**: Lee metadatos EXIF de imágenes
- **Mapas de Calor**: Visualización geoespacial con Leaflet
- **PostGIS**: Análisis espacial avanzado

### Evaluación de Riesgo
- **Algoritmo Epidemiológico**: Clasificación en ALTO, MEDIO, BAJO, MÍNIMO
- **Scoring Automático**: Basado en cantidad y tipo de criaderos
- **Reportes PDF**: Generación automatizada de informes

### Seguridad y Performance
- **Autenticación JWT**: Sistema seguro de tokens
- **Circuit Breaker**: Protección contra fallos en cascada
- **Rate Limiting**: Redis-based con límites configurables
- **Varios cientos de tests**: Cobertura 78-100% en módulos críticos

---

## Documentación por Componente

| Componente | Descripción | Stack Principal |
|------------|-------------|-----------------|
| **[Backend](./backend/README.md)** | API REST, lógica de negocio | FastAPI, PostgreSQL, SQLAlchemy |
| **[YOLO Service](./yolo-service/README.md)** | Servicio de detección IA | YOLOv11, PyTorch, CUDA |
| **[Frontend](./frontend/README.md)** | Interfaz de usuario | React 18, TypeScript, Vite |
| **[Shared Library](./shared/README.md)** | Código compartido | Python, Enums, Utils |
| **[Scripts](./scripts/README.md)** | Testing y deployment | Bash, PowerShell, Python |

### Documentación Técnica Detallada

La carpeta [`docs/`](./docs) contiene documentación técnica exhaustiva sobre cada componente:

- **[Stack del Backend](./docs/BACKEND_STACK.md)** - Tecnologías y arquitectura del backend
- **[Stack del Frontend](./docs/FRONTEND_STACK.md)** - Tecnologías y arquitectura del frontend
- **[Stack del YOLO Service](./docs/YOLO_STACK.md)** - Tecnologías del servicio de IA
- **[Stack Compartido](./docs/SHARED_STACK.md)** - Librería sentrix_shared
- **[Funcionamiento del Backend](./docs/FUNCIONAMIENTO_BACKEND.md)** - Flujos y procesos del backend
- **[Funcionamiento del Frontend](./docs/FUNCIONAMIENTO_FRONTEND.md)** - Flujos y procesos del frontend
- **[Funcionamiento del YOLO Service](./docs/FUNCIONAMIENTO_YOLO_SERVICE.md)** - Procesos de detección IA

---

## Instalación Completa

### Requisitos

| Componente | Versión | Propósito |
|-----------|---------|-----------|
| Python | 3.9+ | Backend y YOLO |
| Node.js | 18+ LTS | Frontend |
| PostgreSQL | 14+ | Base de datos |
| Redis | 7+ | Caché y rate limiting |
| CUDA | 11.8+ (opcional) | Aceleración GPU |

### Instalación Manual

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

### Con Docker Compose

```bash
docker-compose up -d
```

---

## Configuración

Archivo `.env` en la raíz del proyecto:

```bash
# Servicios
BACKEND_PORT=8000
YOLO_SERVICE_PORT=8001
FRONTEND_PORT=5173

# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/sentrix

# Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key
SUPABASE_SERVICE_ROLE_KEY=tu-service-role-key

# Redis (opcional)
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=tu-secret-key-32-chars-minimo
JWT_SECRET_KEY=tu-jwt-secret-key-32-chars-minimo
```

Ver `.env.example` para configuración completa.

---

## Ejecución

### Desarrollo Local

```bash
# Terminal 1 - Backend
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2 - YOLO Service
cd yolo-service && python server.py

# Terminal 3 - Frontend
cd frontend && npm run dev
```

### Con Scripts

```bash
# Linux/Mac
./scripts/start-all.sh

# Windows
.\scripts\start-all.ps1
```

### Con Docker

```bash
docker-compose up
```

### Deployment en Dokploy

Para desplegar en producción con Dokploy (Backend + YOLO + PostgreSQL):

```bash
# Ver guía completa de deployment
cat DEPLOYMENT.md
```

Configuración incluida:
- Docker Compose optimizado para Dokploy
- Health checks automáticos
- Volúmenes persistentes
- Variables de entorno template en `.env.dokploy.example`

Ver **[DEPLOYMENT.md](./DEPLOYMENT.md)** para instrucciones completas.

---

## Testing

```bash
# Backend (varios cientos de tests)
cd backend
pytest tests/ -v --cov=src --cov-report=html

# Frontend
cd frontend
npm run test

# Tests rápidos
python scripts/quick_smoke_tests.py
```

Ver [Backend Tests](./backend/tests/) para detalles completos.

---

## Estructura del Proyecto

```
Sentrix/
├── backend/                # API REST FastAPI
│   ├── src/               # Código fuente
│   ├── scripts/           # Scripts de desarrollo
│   ├── tests/             # Tests unitarios (563+)
│   ├── app.py             # Servidor web principal
│   └── main.py            # CLI de gestión
│
├── yolo-service/          # Servicio de detección IA
│   ├── src/               # Código fuente
│   ├── scripts/           # Scripts de entrenamiento
│   ├── models/            # Modelos YOLO
│   ├── server.py          # Servidor FastAPI
│   └── train_simple.py    # Entrenamiento de modelos
│
├── frontend/              # Aplicación React
│   ├── src/               # Código fuente
│   ├── public/            # Assets estáticos
│   └── vite.config.ts     # Configuración Vite
│
├── shared/                # Librería compartida (sentrix_shared)
│   └── sentrix_shared/    # Código Python compartido
│
├── docs/                  # Documentación técnica
│   ├── imagenes/          # Screenshots del sistema
│   ├── BACKEND_STACK.md   # Stack del backend
│   ├── FRONTEND_STACK.md  # Stack del frontend
│   ├── YOLO_STACK.md      # Stack del YOLO service
│   ├── SHARED_STACK.md    # Librería compartida
│   ├── FUNCIONAMIENTO_BACKEND.md     # Funcionamiento backend
│   ├── FUNCIONAMIENTO_FRONTEND.md    # Funcionamiento frontend
│   └── FUNCIONAMIENTO_YOLO_SERVICE.md # Funcionamiento YOLO
│
├── scripts/               # Scripts de instalación y deployment
├── docker-compose.yml     # Orquestación de contenedores
├── .env.example          # Template de variables de entorno
├── .gitignore            # Archivos ignorados por Git
├── LICENSE               # Licencia MIT
├── CITATION.cff          # Citación académica
└── README.md             # Este archivo
```

---

## Stack Tecnológico

### Backend
- **FastAPI** 0.104+ - Framework web moderno
- **PostgreSQL** 14+ - Base de datos relacional
- **PostGIS** - Extensión geoespacial
- **SQLAlchemy** - ORM
- **Redis** - Caché y rate limiting
- **Celery** - Tareas asíncronas

### YOLO Service
- **YOLOv11** - Modelo de detección
- **PyTorch** - Framework de deep learning
- **Ultralytics** - Librería YOLO
- **OpenCV** - Procesamiento de imágenes
- **FastAPI** - API del servicio

### Frontend
- **React** 18.2 - Librería UI
- **TypeScript** 5.9 - Tipado estático
- **Vite** 4.5 - Build tool
- **TailwindCSS** 3.3 - Estilos
- **React Leaflet** - Mapas interactivos
- **Zustand** - State management
- **TanStack Query** - Data fetching

---

## Health Checks

```bash
# Backend
curl http://localhost:8000/health

# YOLO Service
curl http://localhost:8001/health

# Frontend
curl http://localhost:5173
```

---

## Troubleshooting

### Puerto en uso
```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Base de datos no conecta
- Verificar PostgreSQL ejecutándose: `pg_isready`
- Revisar DATABASE_URL en `.env`
- Verificar credenciales

### YOLO Service falla
- Verificar modelo descargado en `yolo-service/models/`
- Para CPU: `YOLO_DEVICE=cpu` en `.env`
- Ver logs: `tail -f yolo-service/logs/yolo-service.log`

Ver documentación completa en cada componente para más detalles.

---

## Autores

- Manuel Antonio Garcia
- Ricardo Laudani
- Mercedes Warnes

---

## Licencia

MIT License con restricciones adicionales:
- Uso académico e investigación en salud pública
- Prohibido uso político/electoral
- Ver [LICENSE](./LICENSE) para términos completos

---

**Versión**: 2.7.1 | **Actualizado**: Noviembre 2025
