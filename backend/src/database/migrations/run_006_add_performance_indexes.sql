-- Runner script for migration 006
-- Execute this file to run the performance indexes migration

\echo '========================================'
\echo 'Running Migration: 006_add_performance_indexes.sql'
\echo 'Purpose: Add indexes to improve query performance'
\echo '========================================'

\i 006_add_performance_indexes.sql

\echo ''
\echo '========================================'
\echo 'Migration completed successfully!'
\echo '========================================'

-- Show created indexes
\echo ''
\echo 'Created indexes:'
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
AND (indexname LIKE 'idx_analyses_%' OR indexname LIKE 'idx_detections_%')
ORDER BY tablename, indexname;
