# Guía de Contribución - Sentrix

## 📋 Convenciones de Commits

### Formato
```
<tipo>: <descripción>
```

### Tipos de Commit
- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de errores
- `docs:` - Documentación
- `style:` - Cambios de formato (sin afectar funcionalidad)
- `refactor:` - Refactorización de código
- `test:` - Agregar o modificar tests
- `chore:` - Tareas de mantenimiento

### Ejemplos
```
feat: add GPS metadata extraction
fix: resolve image upload timeout
docs: update API documentation
refactor: optimize YOLO detection pipeline
test: add integration tests for backend
chore: update dependencies
```

## 🌿 Convenciones de Ramas

### Formato
```
<tipo>/<componente>/<descripción-corta>
```

### Tipos de Rama
- `feat/` - Nueva funcionalidad
- `fix/` - Corrección de errores
- `hotfix/` - Corrección urgente
- `docs/` - Documentación
- `refactor/` - Refactorización
- `test/` - Tests

### Componentes
- `backend/` - API REST y base de datos
- `frontend/` - Interfaz React
- `yolo-service/` - Servicio de detección IA
- `shared/` - Librería compartida
- `docs/` - Documentación
- `ci/` - CI/CD y scripts

### Ejemplos
```
feat/backend/user-authentication
fix/yolo-service/gpu-memory-leak
feat/frontend/map-visualization
refactor/shared/file-naming-system
docs/api/endpoint-documentation
test/backend/integration-tests
```

## 🏗️ Estructura de Proyecto

```
sentrix/
├── backend/           # API REST (puerto 8000)
│   ├── src/          # Código fuente
│   ├── tests/        # Tests
│   ├── scripts/      # Scripts de utilidad
│   └── alembic/      # Migraciones DB
├── yolo-service/     # Detección IA (puerto 8001)
│   ├── src/          # Código fuente
│   ├── models/       # Modelos entrenados
│   ├── tests/        # Tests
│   └── scripts/      # Scripts de entrenamiento
├── frontend/         # React UI (puerto 3000)
│   ├── src/          # Código fuente
│   ├── public/       # Archivos estáticos
│   └── dist/         # Build de producción
├── shared/           # Librería compartida
│   ├── tests/        # Tests unitarios
│   └── utils/        # Utilidades comunes
├── scripts/          # Scripts de proyecto
└── docs/            # Documentación adicional
```

## 🔄 Flujo de Trabajo

### 1. Crear Nueva Rama
```bash
git checkout main
git pull origin main
git checkout -b feat/componente/descripcion
```

### 2. Desarrollo
```bash
# Hacer cambios
git add .
git commit -m "feat: descripción clara y concisa"
```

### 3. Push y PR
```bash
git push origin feat/componente/descripcion
# Crear Pull Request en GitHub
```

### 4. Merge
```bash
# Solo después de revisión
git checkout main
git pull origin main
git branch -d feat/componente/descripcion
```

## 📦 Versionado

### Formato SemVer
```
v<MAJOR>.<MINOR>.<PATCH>
```

### Criterios
- **MAJOR**: Cambios incompatibles en API
- **MINOR**: Nueva funcionalidad compatible
- **PATCH**: Correcciones de errores

### Ejemplos
```
v1.0.0 - Primera versión estable
v1.1.0 - Agregar autenticación OAuth
v1.1.1 - Fix bug en upload de imágenes
v2.0.0 - Cambio mayor en API REST
```

## 🧪 Testing

### Antes de Commit
```bash
# Backend
cd backend && python -m pytest tests/ -v

# YOLO Service
cd yolo-service && python -m pytest tests/ -v

# Frontend
cd frontend && npm test

# Scripts de validación
python scripts/quick_smoke_tests.py
```

### Cobertura Mínima
- **Backend**: 80%
- **YOLO Service**: 75%
- **Shared Library**: 85%

## 📝 Documentación

### README Updates
- Actualizar versión en README principal
- Documentar nuevas funcionalidades
- Actualizar instrucciones de instalación

### API Documentation
- Documentar nuevos endpoints
- Actualizar schemas de respuesta
- Mantener ejemplos actualizados

## 🚀 Release Process

### 1. Preparación
```bash
# Verificar tests
python scripts/run_comprehensive_tests.py

# Actualizar documentación
# Revisar CHANGELOG.md
```

### 2. Tag y Release
```bash
git tag v1.x.x
git push origin v1.x.x
# Crear release en GitHub
```

### 3. Deploy
```bash
# Producción
./scripts/deploy-production.sh

# Verificar servicios
curl http://api.sentrix.com/health
```

## 🛠️ Herramientas Recomendadas

### Desarrollo
- **IDE**: VSCode con extensiones Python/TypeScript
- **Git Client**: GitKraken o línea de comandos
- **API Testing**: Postman o Insomnia
- **Database**: pgAdmin para PostgreSQL

### Debugging
```bash
# Diagnóstico completo
python backend/diagnostic.py
python yolo-service/diagnostic.py

# Tests rápidos
python scripts/simple_test.py
```

## 🔧 Configuración Local

### Variables de Entorno
```bash
cp .env.example .env
# Editar configuración local
```

### Servicios
```bash
# Inicio automático
./start-all.ps1

# Manual por servicio
cd backend && python app.py
cd yolo-service && python server.py
cd frontend && npm run dev
```

---

**Mantener este archivo actualizado con cada cambio significativo en el proyecto.**