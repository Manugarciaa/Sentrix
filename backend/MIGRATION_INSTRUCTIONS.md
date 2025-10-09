# Instrucciones para Ejecutar la Migración de Validez Temporal
# Migration Instructions for Temporal Validity

## Opción 1: Supabase SQL Editor (Recomendado / Recommended)

1. **Acceder al Supabase Dashboard**
   - Ve a: https://app.supabase.com/project/_/sql
   - Inicia sesión en tu proyecto

2. **Abrir el SQL Editor**
   - Click en "SQL Editor" en el menú lateral
   - Click en "New Query"

3. **Copiar y Ejecutar la Migración**
   - Abre el archivo: `backend/src/database/migrations/002_add_detection_validity.sql`
   - Copia todo el contenido
   - Pégalo en el SQL Editor
   - Click en "Run" (o presiona Ctrl+Enter)

4. **Verificar Ejecución**
   Deberías ver mensajes de éxito para:
   - ✅ ALTER TABLE (5 columnas agregadas)
   - ✅ CREATE INDEX (4 índices creados)
   - ✅ COMMENT ON COLUMN (5 comentarios)
   - ✅ UPDATE (backfill de datos existentes - 4 statements)
   - ✅ CREATE VIEW (3 vistas creadas)
   - ✅ CREATE FUNCTION (2 funciones creadas)

## Opción 2: psql Command Line

Si tienes acceso directo a PostgreSQL vía `psql`:

```bash
# Conéctate a tu base de datos
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"

# Ejecuta la migración
\i backend/src/database/migrations/002_add_detection_validity.sql

# Verifica que se crearon las columnas
\d detections
```

## Opción 3: Script Python con psycopg2

Si tienes `psycopg2` instalado:

```bash
cd backend
pip install psycopg2-binary

# Configura DATABASE_URL en .env:
# DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

python apply_migration_psycopg2.py
```

## Verificación Post-Migración

Después de ejecutar la migración, verifica que todo esté correcto:

### 1. Verificar Columnas Agregadas

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'detections'
  AND column_name IN (
    'validity_period_days',
    'expires_at',
    'is_weather_dependent',
    'persistence_type',
    'last_expiration_alert_sent'
  );
```

Deberías ver 5 filas.

### 2. Verificar Índices Creados

```sql
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'detections'
  AND indexname LIKE '%validity%' OR indexname LIKE '%persistence%' OR indexname LIKE '%expir%';
```

Deberías ver al menos 4 índices:
- `idx_detections_expires_at`
- `idx_detections_persistence_type`
- `idx_detections_active`
- `idx_detections_expiring_soon`

### 3. Verificar Vistas Creadas

```sql
SELECT table_name, view_definition
FROM information_schema.views
WHERE table_name IN (
  'active_detections',
  'expired_detections',
  'expiring_soon_detections'
);
```

Deberías ver 3 vistas.

### 4. Verificar Funciones Creadas

```sql
SELECT routine_name, routine_type
FROM information_schema.routines
WHERE routine_name IN (
  'is_detection_expired',
  'get_remaining_validity_days'
);
```

Deberías ver 2 funciones.

### 5. Verificar Backfill de Datos

```sql
-- Contar detecciones con validez asignada
SELECT
  COUNT(*) as total_detections,
  COUNT(validity_period_days) as with_validity,
  COUNT(expires_at) as with_expiration,
  COUNT(DISTINCT persistence_type) as persistence_types
FROM detections;
```

Si tienes detecciones existentes, todas deberían tener valores en estos campos.

### 6. Probar Vistas

```sql
-- Ver detecciones activas
SELECT COUNT(*) FROM active_detections;

-- Ver detecciones expiradas
SELECT COUNT(*) FROM expired_detections;

-- Ver detecciones por expirar pronto
SELECT * FROM expiring_soon_detections LIMIT 5;
```

### 7. Probar Funciones

```sql
-- Probar función de expiración
SELECT
  id,
  expires_at,
  is_detection_expired(id) as is_expired,
  get_remaining_validity_days(id) as days_remaining
FROM detections
LIMIT 10;
```

## Rollback (Si es Necesario)

Si necesitas revertir la migración:

```sql
-- Eliminar vistas
DROP VIEW IF EXISTS expiring_soon_detections;
DROP VIEW IF EXISTS expired_detections;
DROP VIEW IF EXISTS active_detections;

-- Eliminar funciones
DROP FUNCTION IF EXISTS get_remaining_validity_days(UUID);
DROP FUNCTION IF EXISTS is_detection_expired(UUID);

-- Eliminar índices
DROP INDEX IF EXISTS idx_detections_expiring_soon;
DROP INDEX IF EXISTS idx_detections_active;
DROP INDEX IF EXISTS idx_detections_persistence_type;
DROP INDEX IF EXISTS idx_detections_expires_at;

-- Eliminar columnas
ALTER TABLE detections
  DROP COLUMN IF EXISTS last_expiration_alert_sent,
  DROP COLUMN IF EXISTS persistence_type,
  DROP COLUMN IF EXISTS is_weather_dependent,
  DROP COLUMN IF EXISTS expires_at,
  DROP COLUMN IF EXISTS validity_period_days;
```

## Problemas Comunes

### Error: "relation detections does not exist"
- Verifica que estás conectado a la base de datos correcta
- Verifica que la tabla `detections` existe: `SELECT * FROM detections LIMIT 1;`

### Error: "column already exists"
- La migración ya fue ejecutada anteriormente
- Verifica con: `\d detections` o consulta `information_schema.columns`

### Error: "permission denied"
- Asegúrate de estar conectado con el usuario `postgres` o un usuario con permisos adecuados
- En Supabase Dashboard, el SQL Editor tiene permisos completos

## Próximos Pasos

Una vez completada la migración:

1. ✅ Reinicia el backend para que los nuevos campos estén disponibles
2. ✅ Prueba los nuevos endpoints de `/api/v1/detections/*`
3. ✅ Verifica que las detecciones nuevas calculan automáticamente su validez
4. ✅ Considera implementar un cron job para enviar alertas de expiración

---

**Nota**: Esta migración es **aditiva** y **no destructiva**. No elimina ni modifica datos existentes,
solo agrega nuevas columnas e índices. Es seguro ejecutarla en producción.
