# Scripts de Desarrollo y Utilidades

Esta carpeta contiene scripts de utilidad para desarrollo, testing, migraciones y diagnóstico del backend de Sentrix.

## Estructura

```
scripts/
├── tests/              # Scripts de testing y validación
├── migrations/         # Scripts de migración de base de datos
├── diagnostics/        # Scripts de diagnóstico y verificación
└── sql/               # Scripts SQL para configuración
```

---

## tests/

Scripts para probar funcionalidad específica:

- **test_env.py** - Verifica variables de entorno
- **test_gps_extraction.py** - Prueba extracción de coordenadas GPS de imágenes
- **test_gps_debug.py** - Debug de funcionalidad GPS
- **check_supabase_bucket.py** - Verifica conexión y configuración de Supabase Storage
- **monitor_uploads.py** - Monitorea el proceso de upload de imágenes

### Uso
```bash
cd scripts/tests
python test_env.py
python check_supabase_bucket.py
```

---

## migrations/

Scripts para ejecutar migraciones de base de datos:

- **run_migration.py** - Ejecuta migraciones con Alembic
- **run_migration_simple.py** - Migración simplificada
- **run_performance_migration.py** - Migración de optimizaciones de performance
- **fix_user_roles.py** - Corrige roles de usuarios existentes

### Uso
```bash
cd scripts/migrations
python run_migration.py
python fix_user_roles.py
```

---

## diagnostics/

Scripts para verificar estado del sistema:

- **diagnostic.py** - Diagnóstico general del sistema
- **diagnostic_env.py** - Diagnóstico de variables de entorno
- **verify_indexes_simple.py** - Verifica índices de base de datos
- **verify_performance_improvements.py** - Verifica optimizaciones aplicadas
- **verify_rate_limiting.py** - Verifica configuración de rate limiting
- **verify_file_validation.py** - Verifica validación de archivos

### Uso
```bash
cd scripts/diagnostics
python diagnostic.py
python verify_performance_improvements.py
```

---

## sql/

Scripts SQL para configuración inicial:

- **setup_complete_security.sql** - Configuración completa de seguridad (RLS, policies)
- **create_gps_update_function.sql** - Función para actualización de coordenadas GPS

### Uso
```bash
psql -U postgres -d sentrix -f scripts/sql/setup_complete_security.sql
psql -U postgres -d sentrix -f scripts/sql/create_gps_update_function.sql
```

---

## Notas

- Estos scripts son herramientas de desarrollo y no deben ejecutarse en producción sin revisión
- Algunos scripts requieren variables de entorno configuradas (ver `.env.example`)
- Ejecutar desde el directorio raíz del backend para asegurar imports correctos
