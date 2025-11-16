-- ============================================
-- SENTRIX - CONFIGURACIÓN COMPLETA DE SEGURIDAD
-- ============================================
-- Este script:
-- 1. Limpia toda la base de datos
-- 2. Configura RLS (Row Level Security) correctamente
-- 3. Establece políticas de seguridad
-- ============================================

-- ============================================
-- PASO 1: LIMPIEZA COMPLETA
-- ============================================

-- Eliminar en orden correcto por foreign keys
DELETE FROM detections;
DELETE FROM analyses;
DELETE FROM audit_log;
DELETE FROM user_settings;
DELETE FROM user_profiles;

-- NOTA: spatial_ref_sys y geography_columns NO se tocan (son tablas del sistema PostGIS)

-- Verificar que esté vacío
DO $$
BEGIN
    RAISE NOTICE 'Registros eliminados - Verificación:';
    RAISE NOTICE 'Analyses: %', (SELECT COUNT(*) FROM analyses);
    RAISE NOTICE 'Detections: %', (SELECT COUNT(*) FROM detections);
    RAISE NOTICE 'User profiles: %', (SELECT COUNT(*) FROM user_profiles);
    RAISE NOTICE 'User settings: %', (SELECT COUNT(*) FROM user_settings);
    RAISE NOTICE 'Audit log: %', (SELECT COUNT(*) FROM audit_log);
END $$;

-- ============================================
-- PASO 2: CONFIGURAR RLS (ROW LEVEL SECURITY)
-- ============================================

-- Habilitar RLS en todas las tablas
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE detections ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Eliminar políticas existentes si las hay
DROP POLICY IF EXISTS "analyses_select_policy" ON analyses;
DROP POLICY IF EXISTS "analyses_insert_policy" ON analyses;
DROP POLICY IF EXISTS "analyses_update_policy" ON analyses;
DROP POLICY IF EXISTS "analyses_delete_policy" ON analyses;

DROP POLICY IF EXISTS "detections_select_policy" ON detections;
DROP POLICY IF EXISTS "detections_insert_policy" ON detections;
DROP POLICY IF EXISTS "detections_update_policy" ON detections;
DROP POLICY IF EXISTS "detections_delete_policy" ON detections;

DROP POLICY IF EXISTS "user_profiles_select_policy" ON user_profiles;
DROP POLICY IF EXISTS "user_profiles_insert_policy" ON user_profiles;
DROP POLICY IF EXISTS "user_profiles_update_policy" ON user_profiles;

DROP POLICY IF EXISTS "user_settings_select_policy" ON user_settings;
DROP POLICY IF EXISTS "user_settings_insert_policy" ON user_settings;
DROP POLICY IF EXISTS "user_settings_update_policy" ON user_settings;

DROP POLICY IF EXISTS "audit_log_select_policy" ON audit_log;
DROP POLICY IF EXISTS "audit_log_insert_policy" ON audit_log;

-- ============================================
-- PASO 3: POLÍTICAS PARA TABLA ANALYSES
-- ============================================

-- SELECT: Usuarios pueden ver sus propios análisis + Admins ven todo
CREATE POLICY "analyses_select_policy" ON analyses
    FOR SELECT
    USING (
        auth.uid() = user_id OR  -- Usuario es dueño
        auth.jwt() ->> 'role' IN ('ADMIN', 'EXPERT') OR  -- Usuario es admin/expert
        auth.role() = 'service_role'  -- Backend con service_role
    );

-- INSERT: Usuarios autenticados pueden crear análisis
CREATE POLICY "analyses_insert_policy" ON analyses
    FOR INSERT
    WITH CHECK (
        auth.uid() = user_id OR  -- Usuario es dueño
        auth.role() = 'service_role'  -- Backend puede crear
    );

-- UPDATE: Solo dueño, admins, o service_role pueden actualizar
CREATE POLICY "analyses_update_policy" ON analyses
    FOR UPDATE
    USING (
        auth.uid() = user_id OR
        auth.jwt() ->> 'role' IN ('ADMIN', 'EXPERT') OR
        auth.role() = 'service_role'
    );

-- DELETE: Solo dueño, admins, o service_role pueden eliminar
CREATE POLICY "analyses_delete_policy" ON analyses
    FOR DELETE
    USING (
        auth.uid() = user_id OR
        auth.jwt() ->> 'role' = 'ADMIN' OR
        auth.role() = 'service_role'
    );

-- ============================================
-- PASO 4: POLÍTICAS PARA TABLA DETECTIONS
-- ============================================

-- SELECT: Ver detecciones de análisis propios + Admins/Experts ven todo
CREATE POLICY "detections_select_policy" ON detections
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM analyses
            WHERE analyses.id = detections.analysis_id
            AND (
                analyses.user_id = auth.uid() OR
                auth.jwt() ->> 'role' IN ('ADMIN', 'EXPERT')
            )
        ) OR
        auth.role() = 'service_role'
    );

-- INSERT: Solo backend puede crear detecciones
CREATE POLICY "detections_insert_policy" ON detections
    FOR INSERT
    WITH CHECK (
        auth.role() = 'service_role' OR
        EXISTS (
            SELECT 1 FROM analyses
            WHERE analyses.id = detections.analysis_id
            AND analyses.user_id = auth.uid()
        )
    );

-- UPDATE: Dueño del análisis, Admins, Experts, o service_role
CREATE POLICY "detections_update_policy" ON detections
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM analyses
            WHERE analyses.id = detections.analysis_id
            AND (
                analyses.user_id = auth.uid() OR
                auth.jwt() ->> 'role' IN ('ADMIN', 'EXPERT')
            )
        ) OR
        auth.role() = 'service_role'
    );

-- DELETE: Solo Admins o service_role
CREATE POLICY "detections_delete_policy" ON detections
    FOR DELETE
    USING (
        auth.jwt() ->> 'role' = 'ADMIN' OR
        auth.role() = 'service_role'
    );

-- ============================================
-- PASO 5: POLÍTICAS PARA TABLA USER_PROFILES
-- ============================================

-- SELECT: Usuarios ven su propio perfil + Admins ven todos
CREATE POLICY "user_profiles_select_policy" ON user_profiles
    FOR SELECT
    USING (
        auth.uid() = id OR
        auth.jwt() ->> 'role' = 'ADMIN' OR
        auth.role() = 'service_role'
    );

-- INSERT: Solo service_role puede crear perfiles (durante registro)
CREATE POLICY "user_profiles_insert_policy" ON user_profiles
    FOR INSERT
    WITH CHECK (
        auth.role() = 'service_role'
    );

-- UPDATE: Usuario puede actualizar su propio perfil + Admins pueden actualizar cualquiera
CREATE POLICY "user_profiles_update_policy" ON user_profiles
    FOR UPDATE
    USING (
        auth.uid() = id OR
        auth.jwt() ->> 'role' = 'ADMIN' OR
        auth.role() = 'service_role'
    );

-- ============================================
-- PASO 6: POLÍTICAS PARA TABLA USER_SETTINGS
-- ============================================

-- SELECT: Usuarios ven solo su propia configuración + Admins ven todas
CREATE POLICY "user_settings_select_policy" ON user_settings
    FOR SELECT
    USING (
        auth.uid() = user_id OR
        auth.jwt() ->> 'role' = 'ADMIN' OR
        auth.role() = 'service_role'
    );

-- INSERT: Solo service_role puede crear configuraciones (durante registro)
CREATE POLICY "user_settings_insert_policy" ON user_settings
    FOR INSERT
    WITH CHECK (
        auth.role() = 'service_role'
    );

-- UPDATE: Usuario puede actualizar su propia configuración + Admins pueden actualizar cualquiera
CREATE POLICY "user_settings_update_policy" ON user_settings
    FOR UPDATE
    USING (
        auth.uid() = user_id OR
        auth.jwt() ->> 'role' = 'ADMIN' OR
        auth.role() = 'service_role'
    );

-- ============================================
-- PASO 7: POLÍTICAS PARA TABLA AUDIT_LOG
-- ============================================

-- SELECT: Usuarios ven solo sus propios logs + Admins ven todos
CREATE POLICY "audit_log_select_policy" ON audit_log
    FOR SELECT
    USING (
        auth.uid() = user_id OR
        auth.jwt() ->> 'role' = 'ADMIN' OR
        auth.role() = 'service_role'
    );

-- INSERT: Solo service_role puede escribir en audit_log
CREATE POLICY "audit_log_insert_policy" ON audit_log
    FOR INSERT
    WITH CHECK (
        auth.role() = 'service_role'
    );

-- NO permitir UPDATE ni DELETE en audit_log (es un log de auditoría)

-- ============================================
-- PASO 8: CONFIGURAR STORAGE BUCKETS
-- ============================================

-- Nota: Estos comandos son para ejecutar en la consola de Supabase Storage
-- O usar la API de Storage para configurar políticas

-- Política para sentrix-images: Lectura pública, escritura solo service_role
-- Ejecutar en SQL Editor:

-- Primero, asegurarse de que los buckets existan y sean públicos
-- Esto se hace desde el Dashboard de Storage, no desde SQL

-- Eliminar políticas existentes de Storage
DROP POLICY IF EXISTS "Public read access for images" ON storage.objects;
DROP POLICY IF EXISTS "Public read access for processed" ON storage.objects;
DROP POLICY IF EXISTS "Service role can upload images" ON storage.objects;
DROP POLICY IF EXISTS "Service role can upload processed" ON storage.objects;
DROP POLICY IF EXISTS "Service role can delete images" ON storage.objects;

-- Política de Storage para SELECT (lectura pública)
CREATE POLICY "Public read access for images"
ON storage.objects FOR SELECT
USING (bucket_id = 'sentrix-images');

CREATE POLICY "Public read access for processed"
ON storage.objects FOR SELECT
USING (bucket_id = 'sentrix-processed');

-- Política de Storage para INSERT (solo service_role)
CREATE POLICY "Service role can upload images"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'sentrix-images' AND
    auth.role() = 'service_role'
);

CREATE POLICY "Service role can upload processed"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'sentrix-processed' AND
    auth.role() = 'service_role'
);

-- Política de Storage para DELETE (solo service_role)
CREATE POLICY "Service role can delete images"
ON storage.objects FOR DELETE
USING (
    bucket_id IN ('sentrix-images', 'sentrix-processed') AND
    auth.role() = 'service_role'
);

-- ============================================
-- PASO 7: PERMISOS ADICIONALES
-- ============================================

-- Asegurar que la función de Geography funcione correctamente
-- (Si usas PostGIS para coordenadas GPS)

-- Grant necesarios para que el service_role pueda operar
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO service_role;

-- Grant para usuarios autenticados (lectura limitada por RLS)
GRANT SELECT, INSERT, UPDATE ON analyses TO authenticated;
GRANT SELECT, UPDATE ON detections TO authenticated;
GRANT SELECT, UPDATE ON user_profiles TO authenticated;
GRANT SELECT, UPDATE ON user_settings TO authenticated;
GRANT SELECT ON audit_log TO authenticated;

-- ============================================
-- PASO 8: ÍNDICES PARA PERFORMANCE
-- ============================================

-- Índices para mejorar queries comunes
CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_risk_level ON analyses(risk_level);
CREATE INDEX IF NOT EXISTS idx_analyses_has_gps ON analyses(has_gps_data);

CREATE INDEX IF NOT EXISTS idx_detections_analysis_id ON detections(analysis_id);
CREATE INDEX IF NOT EXISTS idx_detections_risk_level ON detections(risk_level);

-- Índice espacial para búsquedas por ubicación (si usas PostGIS)
CREATE INDEX IF NOT EXISTS idx_analyses_location ON analyses USING GIST(location);

-- ============================================
-- PASO 9: VERIFICACIÓN FINAL
-- ============================================

-- Verificar que RLS esté habilitado
SELECT
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('analyses', 'detections', 'user_profiles', 'user_settings', 'audit_log')
ORDER BY tablename;

-- Verificar políticas creadas
SELECT
    schemaname,
    tablename,
    policyname,
    cmd as command,
    roles
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- Contar registros finales
SELECT
    'analyses' as tabla,
    COUNT(*) as registros,
    'Should be 0' as expected
FROM analyses
UNION ALL
SELECT
    'detections' as tabla,
    COUNT(*) as registros,
    'Should be 0' as expected
FROM detections
UNION ALL
SELECT
    'user_profiles' as tabla,
    COUNT(*) as registros,
    'Should be 0' as expected
FROM user_profiles
UNION ALL
SELECT
    'user_settings' as tabla,
    COUNT(*) as registros,
    'Should be 0' as expected
FROM user_settings
UNION ALL
SELECT
    'audit_log' as tabla,
    COUNT(*) as registros,
    'Should be 0' as expected
FROM audit_log;

-- ============================================
-- NOTAS IMPORTANTES
-- ============================================

/*
1. BUCKETS DE STORAGE:
   - Asegúrate de que 'sentrix-images' y 'sentrix-processed' estén marcados como PÚBLICOS
   - Hazlo desde: Storage > sentrix-images > Settings > Public bucket = ON

2. SERVICE ROLE KEY:
   - El backend DEBE usar SUPABASE_SERVICE_ROLE_KEY para bypasear RLS
   - NUNCA uses service_role_key en el frontend (solo anon_key)

3. AUTH.USERS:
   - Los usuarios se crean en auth.users (tabla de Supabase Auth)
   - La tabla 'user_profiles' es solo para datos adicionales del perfil

4. TESTING:
   - Para probar RLS, conéctate con diferentes usuarios
   - Verifica que cada usuario solo vea sus propios análisis
   - Verifica que admins vean todo

5. ROLES:
   - USER: Rol por defecto, acceso limitado a sus datos
   - EXPERT: Puede validar detecciones, ve todos los análisis
   - ADMIN: Acceso completo, puede eliminar

6. LIMPIEZA DE STORAGE:
   - Este SQL no limpia archivos de Storage
   - Hazlo manualmente: Storage > Select all > Delete
*/

-- FIN DEL SCRIPT
