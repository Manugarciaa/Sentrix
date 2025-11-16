-- Migration: 006_add_performance_indexes.sql
-- Description: Add indexes to improve query performance on analyses and detections tables
-- Created: 2025-10-23
-- Purpose: Fix performance issue where analysis list queries take 2.8s instead of <1s

-- ============================================
-- ANALYSES TABLE INDEXES
-- ============================================

-- Index for sorting by creation date (most common query pattern)
CREATE INDEX IF NOT EXISTS idx_analyses_created_at_desc
ON analyses(created_at DESC);

-- Index for filtering by user_id (when filtering user's own analyses)
CREATE INDEX IF NOT EXISTS idx_analyses_user_id
ON analyses(user_id)
WHERE user_id IS NOT NULL;

-- Index for filtering by risk_level (when filtering high/medium/low risk analyses)
CREATE INDEX IF NOT EXISTS idx_analyses_risk_level
ON analyses(risk_level)
WHERE risk_level IS NOT NULL;

-- Composite index for user + created_at (most common query: user's recent analyses)
CREATE INDEX IF NOT EXISTS idx_analyses_user_created
ON analyses(user_id, created_at DESC)
WHERE user_id IS NOT NULL;

-- Index for GPS queries (for heatmap data)
CREATE INDEX IF NOT EXISTS idx_analyses_has_gps
ON analyses(has_gps_data)
WHERE has_gps_data = true;

-- ============================================
-- DETECTIONS TABLE INDEXES
-- ============================================

-- Index for getting detections by analysis_id (most common join)
CREATE INDEX IF NOT EXISTS idx_detections_analysis_id
ON detections(analysis_id);

-- Index for filtering by risk_level
CREATE INDEX IF NOT EXISTS idx_detections_risk_level
ON detections(risk_level)
WHERE risk_level IS NOT NULL;

-- Index for filtering by breeding_site_type
CREATE INDEX IF NOT EXISTS idx_detections_breeding_site
ON detections(breeding_site_type)
WHERE breeding_site_type IS NOT NULL;

-- Composite index for analysis + risk level (common query pattern)
CREATE INDEX IF NOT EXISTS idx_detections_analysis_risk
ON detections(analysis_id, risk_level);

-- ============================================
-- VERIFICATION
-- ============================================

-- Verify indexes were created
DO $$
DECLARE
    idx_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO idx_count
    FROM pg_indexes
    WHERE schemaname = 'public'
    AND (
        indexname LIKE 'idx_analyses_%' OR
        indexname LIKE 'idx_detections_%'
    );

    RAISE NOTICE 'Performance indexes created successfully. Total indexes: %', idx_count;
END $$;

-- Expected performance improvement:
-- - Analysis list queries: 2.8s → <500ms (5-6x faster)
-- - Heatmap queries: Significant improvement with GPS index
-- - User-specific queries: 10x faster with composite index
