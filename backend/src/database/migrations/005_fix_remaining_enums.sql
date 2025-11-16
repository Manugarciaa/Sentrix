-- Migration: Fix detection_risk_enum and validation_status_enum to match shared definitions
-- Created: 2025-10-19
-- Purpose: Align enum values with shared/data_models.py

-- ============================================
-- Fix detection_risk_enum
-- ============================================

-- Step 1: Drop views that depend on it
DROP VIEW IF EXISTS active_detections CASCADE;
DROP VIEW IF EXISTS expired_detections CASCADE;
DROP VIEW IF EXISTS expiring_soon_detections CASCADE;

-- Step 2: Change column to TEXT temporarily
ALTER TABLE detections
ALTER COLUMN risk_level TYPE TEXT;

-- Step 3: Drop old enum
DROP TYPE IF EXISTS detection_risk_enum CASCADE;

-- Step 4: Create new enum with correct values (matching shared/data_models.py DetectionRiskEnum)
CREATE TYPE detection_risk_enum AS ENUM (
    'ALTO',
    'MEDIO',
    'BAJO',
    'MINIMO'
);

-- Step 5: Convert column back to enum
ALTER TABLE detections
ALTER COLUMN risk_level TYPE detection_risk_enum
USING risk_level::detection_risk_enum;

-- ============================================
-- Fix validation_status_enum
-- ============================================

-- Step 6: Change column to TEXT temporarily
ALTER TABLE detections
ALTER COLUMN validation_status TYPE TEXT;

-- Step 7: Drop old enum
DROP TYPE IF EXISTS validation_status_enum CASCADE;

-- Step 8: Create new enum with correct values (matching shared/data_models.py ValidationStatusEnum)
CREATE TYPE validation_status_enum AS ENUM (
    'pending',
    'pending_validation',
    'validated_positive',
    'validated_negative',
    'requires_review'
);

-- Step 9: Convert column back to enum with default value
ALTER TABLE detections
ALTER COLUMN validation_status TYPE validation_status_enum
USING COALESCE(validation_status, 'pending')::validation_status_enum;

-- Step 10: Set default value
ALTER TABLE detections
ALTER COLUMN validation_status SET DEFAULT 'pending';

-- ============================================
-- Recreate views
-- ============================================

CREATE OR REPLACE VIEW active_detections AS
SELECT *
FROM detections
WHERE expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP;

CREATE OR REPLACE VIEW expired_detections AS
SELECT *
FROM detections
WHERE expires_at IS NOT NULL AND expires_at <= CURRENT_TIMESTAMP;

CREATE OR REPLACE VIEW expiring_soon_detections AS
SELECT *,
    EXTRACT(EPOCH FROM (expires_at - CURRENT_TIMESTAMP)) / 3600 AS hours_until_expiration
FROM detections
WHERE expires_at IS NOT NULL
  AND expires_at > CURRENT_TIMESTAMP
  AND expires_at <= CURRENT_TIMESTAMP + INTERVAL '1 day'
ORDER BY expires_at ASC;

-- Add comments
COMMENT ON TYPE detection_risk_enum IS 'Detection risk levels - matches shared/data_models.py DetectionRiskEnum';
COMMENT ON TYPE validation_status_enum IS 'Validation status - matches shared/data_models.py ValidationStatusEnum';

-- Migration complete
