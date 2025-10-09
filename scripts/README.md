# Scripts de Utilidad - Sentrix

Scripts para desarrollo, testing y deployment del proyecto Sentrix.

## Estructura

```
scripts/
├── start-all.ps1              # Iniciar todos los servicios (Windows)
├── start-docker.ps1           # Iniciar con Docker (Windows)
├── simple_test.py             # Tests básicos de funcionalidad
├── quick_smoke_tests.py       # Smoke tests de componentes
├── test_deduplication.py      # Tests de deduplicación
├── integration-test.py        # Tests de integración
├── run_comprehensive_tests.py # Runner de tests completo
├── setup/                     # Scripts de configuración inicial
│   ├── setup-env.py          # Configurar entorno
│   └── init-db.sql           # Script SQL inicial
├── maintenance/               # Scripts de mantenimiento
│   ├── comprehensive_fix_imports.py
│   ├── fix_api_routers.py
│   ├── fix_entry_points.py
│   └── fix_imports.py
└── deprecated/                # Scripts antiguos (no usar)
    └── testing/              # Tests antiguos
```

## Scripts de Inicio

### `start-all.ps1`
Inicia todos los servicios del proyecto en desarrollo local.

```powershell
# Windows
.\scripts\start-all.ps1
```

### `start-docker.ps1`
Inicia el proyecto usando Docker Compose.

```powershell
# Windows
.\scripts\start-docker.ps1
```

## Scripts de Testing

### `simple_test.py`
Tests básicos de funcionalidad del sistema.

```bash
python scripts/simple_test.py
```

**Verifica:**
- Shared library
- Nomenclatura estandarizada
- AnalysisService
- SupabaseManager

### `quick_smoke_tests.py`
Verificación rápida de componentes críticos.

```bash
python scripts/quick_smoke_tests.py
```

**Prueba:**
- Importación de módulos
- Generación de nombres
- Detección de formatos
- Clientes (Supabase, YOLO, Analysis)

### `test_deduplication.py`
Tests del sistema de deduplicación.

```bash
python scripts/test_deduplication.py
```

**Valida:**
- Firmas de contenido (SHA-256, MD5)
- Detección de duplicados
- Scoring de similitud
- Ahorro de storage

### `integration-test.py`
Tests de integración entre servicios.

```bash
python scripts/integration-test.py
```

### `run_comprehensive_tests.py`
Runner completo de todos los tests.

```bash
python scripts/run_comprehensive_tests.py
```

## Scripts de Setup

### `setup/setup-env.py`
Configuración automática del entorno.

```bash
python scripts/setup/setup-env.py
```

**Funcionalidad:**
- Crea archivos .env
- Genera secrets seguros
- Valida dependencias

### `setup/init-db.sql`
Script SQL para inicializar base de datos.

```bash
psql -U postgres -d sentrix -f scripts/setup/init-db.sql
```

## Scripts de Mantenimiento

Scripts en `maintenance/` para corrección de código:

- `comprehensive_fix_imports.py` - Corrección masiva de imports
- `fix_api_routers.py` - Corrección de routers API
- `fix_entry_points.py` - Corrección de entry points
- `fix_imports.py` - Corrección básica de imports

**Nota:** Estos scripts ya cumplieron su propósito. Solo usar si hay problemas de imports.

## Flujo de Testing Recomendado

```bash
# 1. Smoke tests (verificación rápida)
python scripts/quick_smoke_tests.py

# 2. Tests básicos
python scripts/simple_test.py

# 3. Tests de deduplicación
python scripts/test_deduplication.py

# 4. Tests completos
python scripts/run_comprehensive_tests.py
```

## Notas

- Scripts en `deprecated/` son antiguos y no se deben usar
- Para tests de producción, usar pytest en `backend/tests/`
- Scripts de Docker están en raíz: `docker-compose.yml`
