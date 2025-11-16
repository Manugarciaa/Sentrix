-- Migration: Fix breeding_site_type_enum to match shared definitions
-- Created: 2025-10-19
-- Purpose: Change "Charcos/Cumulos de agua" to "Charcos/Cumulo de agua" (singular)

-- Step 1: Drop views that depend on the column
DROP VIEW IF EXISTS active_detections CASCADE;
DROP VIEW IF EXISTS expired_detections CASCADE;
DROP VIEW IF EXISTS expiring_soon_detections CASCADE;

-- Step 2: Change column to TEXT temporarily
ALTER TABLE detections
ALTER COLUMN breeding_site_type TYPE TEXT;

-- Step 3: Drop old enum
DROP TYPE IF EXISTS breeding_site_type_enum CASCADE;

-- Step 4: Create new enum with correct values (matching shared/sentrix_shared/data_models.py)
CREATE TYPE breeding_site_type_enum AS ENUM (
    'Basura',
    'Calles mal hechas',
    'Charcos/Cumulo de agua',  -- SINGULAR (was: Cumulos)
    'Huecos'
);

-- Step 5: Convert column back to enum
ALTER TABLE detections
ALTER COLUMN breeding_site_type TYPE breeding_site_type_enum
USING breeding_site_type::breeding_site_type_enum;

-- Step 6: Recreate views
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

-- Add comment
COMMENT ON TYPE breeding_site_type_enum IS 'Breeding site types for Aedes aegypti mosquitoes - matches shared/data_models.py BreedingSiteTypeEnum';
