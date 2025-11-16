-- Migration: Add temporal validity fields to detections table
-- Created: 2025-10-09
-- Purpose: Support temporal persistence model for breeding site detections

-- Add temporal validity columns to detections table
ALTER TABLE detections
ADD COLUMN IF NOT EXISTS validity_period_days INTEGER,
ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS is_weather_dependent BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS persistence_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS last_expiration_alert_sent TIMESTAMPTZ;

-- Add index on expires_at for efficient querying of expired detections
CREATE INDEX IF NOT EXISTS idx_detections_expires_at ON detections(expires_at);

-- Add index on persistence_type for filtering by persistence category
CREATE INDEX IF NOT EXISTS idx_detections_persistence_type ON detections(persistence_type);

-- Add comment to table
COMMENT ON COLUMN detections.validity_period_days IS 'Calculated validity period in days based on breeding site type, risk level, and weather conditions';
COMMENT ON COLUMN detections.expires_at IS 'Timestamp when this detection is considered expired and may need revalidation';
COMMENT ON COLUMN detections.is_weather_dependent IS 'Whether the validity of this detection depends on weather conditions (e.g., puddles dry faster in sun)';
COMMENT ON COLUMN detections.persistence_type IS 'Persistence classification: TRANSIENT, SHORT_TERM, MEDIUM_TERM, LONG_TERM, or PERMANENT';
COMMENT ON COLUMN detections.last_expiration_alert_sent IS 'Timestamp of last alert sent for upcoming expiration (to avoid spam)';

-- Backfill existing detections with default values based on breeding_site_type
-- Note: Using enum values without underscores to match the enum definition

-- Charcos/Cumulo de agua -> TRANSIENT (2 days default)
UPDATE detections
SET
    validity_period_days = 2,
    expires_at = created_at + INTERVAL '2 days',
    is_weather_dependent = TRUE,
    persistence_type = 'TRANSIENT'
WHERE breeding_site_type = 'Charcos/Cumulo de agua'
  AND validity_period_days IS NULL;

-- Basura -> SHORT_TERM (7 days default)
UPDATE detections
SET
    validity_period_days = 7,
    expires_at = created_at + INTERVAL '7 days',
    is_weather_dependent = TRUE,
    persistence_type = 'SHORT_TERM'
WHERE breeding_site_type = 'Basura'
  AND validity_period_days IS NULL;

-- Hoyos/Depresiones -> MEDIUM_TERM (30 days default)
UPDATE detections
SET
    validity_period_days = 30,
    expires_at = created_at + INTERVAL '30 days',
    is_weather_dependent = FALSE,
    persistence_type = 'MEDIUM_TERM'
WHERE breeding_site_type = 'Hoyos/Depresiones'
  AND validity_period_days IS NULL;

-- Calles_deterioradas -> LONG_TERM (180 days default)
UPDATE detections
SET
    validity_period_days = 180,
    expires_at = created_at + INTERVAL '180 days',
    is_weather_dependent = FALSE,
    persistence_type = 'LONG_TERM'
WHERE breeding_site_type = 'Calles_deterioradas'
  AND validity_period_days IS NULL;

-- Any remaining detections without classification -> MEDIUM_TERM as safe default
UPDATE detections
SET
    validity_period_days = 30,
    expires_at = created_at + INTERVAL '30 days',
    is_weather_dependent = FALSE,
    persistence_type = 'MEDIUM_TERM'
WHERE validity_period_days IS NULL;

-- Create a view for active detections (not expired)
CREATE OR REPLACE VIEW active_detections AS
SELECT *
FROM detections
WHERE expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP;

-- Create a view for expired detections
CREATE OR REPLACE VIEW expired_detections AS
SELECT *
FROM detections
WHERE expires_at IS NOT NULL AND expires_at <= CURRENT_TIMESTAMP;

-- Create a view for detections expiring soon (within 1 day)
CREATE OR REPLACE VIEW expiring_soon_detections AS
SELECT *,
    EXTRACT(EPOCH FROM (expires_at - CURRENT_TIMESTAMP)) / 3600 AS hours_until_expiration
FROM detections
WHERE expires_at IS NOT NULL
  AND expires_at > CURRENT_TIMESTAMP
  AND expires_at <= CURRENT_TIMESTAMP + INTERVAL '1 day'
ORDER BY expires_at ASC;

-- Create a function to check if a detection is expired
CREATE OR REPLACE FUNCTION is_detection_expired(detection_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    expiration_date TIMESTAMPTZ;
BEGIN
    SELECT expires_at INTO expiration_date
    FROM detections
    WHERE id = detection_id;

    IF expiration_date IS NULL THEN
        RETURN FALSE;  -- No expiration set = never expires
    END IF;

    RETURN expiration_date <= CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql STABLE;

-- Create a function to get remaining validity days
CREATE OR REPLACE FUNCTION get_remaining_validity_days(detection_id UUID)
RETURNS INTEGER AS $$
DECLARE
    expiration_date TIMESTAMPTZ;
    days_remaining INTEGER;
BEGIN
    SELECT expires_at INTO expiration_date
    FROM detections
    WHERE id = detection_id;

    IF expiration_date IS NULL THEN
        RETURN NULL;  -- No expiration set
    END IF;

    IF expiration_date <= CURRENT_TIMESTAMP THEN
        RETURN 0;  -- Already expired
    END IF;

    days_remaining := EXTRACT(DAY FROM (expiration_date - CURRENT_TIMESTAMP));
    RETURN days_remaining;
END;
$$ LANGUAGE plpgsql STABLE;

-- Migration complete
