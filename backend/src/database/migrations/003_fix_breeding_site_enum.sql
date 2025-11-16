-- Migration: Fix breeding_site_type_enum to match shared definitions
-- Created: 2025-10-19
-- Purpose: Change "Charcos/Cumulos de agua" to "Charcos/Cumulo de agua" (singular)

-- Step 1: Change column to TEXT temporarily
ALTER TABLE detections
ALTER COLUMN breeding_site_type TYPE TEXT;

-- Step 2: Drop old enum
DROP TYPE IF EXISTS breeding_site_type_enum CASCADE;

-- Step 3: Create new enum with correct values (matching shared/sentrix_shared/data_models.py)
CREATE TYPE breeding_site_type_enum AS ENUM (
    'Basura',
    'Calles mal hechas',
    'Charcos/Cumulo de agua',  -- SINGULAR (was: Cumulos)
    'Huecos'
);

-- Step 4: Convert column back to enum
ALTER TABLE detections
ALTER COLUMN breeding_site_type TYPE breeding_site_type_enum
USING breeding_site_type::breeding_site_type_enum;

-- Verify
COMMENT ON TYPE breeding_site_type_enum IS 'Breeding site types for Aedes aegypti mosquitoes - matches shared/data_models.py';
