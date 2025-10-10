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

-- Add partial index for active (non-expired) detections
CREATE INDEX IF NOT EXISTS idx_detections_active
ON detections(expires_at)
WHERE expires_at > NOW();

-- Add partial index for expiring soon (within 1 day)
CREATE INDEX IF NOT EXISTS idx_detections_expiring_soon
ON detections(expires_at)
WHERE expires_at BETWEEN NOW() AND NOW() + INTERVAL '1 day';

-- Add comment to table
COMMENT ON COLUMN detections.validity_period_days IS 'Calculated validity period in days based on breeding site type, risk level, and weather conditions';
COMMENT ON COLUMN detections.expires_at IS 'Timestamp when this detection is considered expired and may need revalidation';
COMMENT ON COLUMN detections.is_weather_dependent IS 'Whether the validity of this detection depends on weather conditions (e.g., puddles dry faster in sun)';
COMMENT ON COLUMN detections.persistence_type IS 'Persistence classification: TRANSIENT, SHORT_TERM, MEDIUM_TERM, LONG_TERM, or PERMANENT';
COMMENT ON COLUMN detections.last_expiration_alert_sent IS 'Timestamp of last alert sent for upcoming expiration (to avoid spam)';

-- Backfill existing detections with default values based on breeding site type
-- This is a safe operation that sets reasonable defaults for existing data

-- CHARCOS_CUMULO_AGUA -> TRANSIENT (2 days default)
UPDATE detections
SET
    validity_period_days = 2,
    expires_at = created_at + INTERVAL '2 days',
    is_weather_dependent = TRUE,
    persistence_type = 'TRANSIENT'
WHERE breeding_site_type = 'CHARCOS_CUMULO_AGUA'
  AND validity_period_days IS NULL;

-- BASURA -> SHORT_TERM (7 days default)
UPDATE detections
SET
    validity_period_days = 7,
    expires_at = created_at + INTERVAL '7 days',
    is_weather_dependent = TRUE,
    persistence_type = 'SHORT_TERM'
WHERE breeding_site_type = 'BASURA'
  AND validity_period_days IS NULL;

-- HUECOS -> MEDIUM_TERM (30 days default)
UPDATE detections
SET
    validity_period_days = 30,
    expires_at = created_at + INTERVAL '30 days',
    is_weather_dependent = FALSE,
    persistence_type = 'MEDIUM_TERM'
WHERE breeding_site_type = 'HUECOS'
  AND validity_period_days IS NULL;

-- CALLES_MAL_HECHAS -> LONG_TERM (180 days default)
UPDATE detections
SET
    validity_period_days = 180,
    expires_at = created_at + INTERVAL '180 days',
    is_weather_dependent = FALSE,
    persistence_type = 'LONG_TERM'
WHERE breeding_site_type = 'CALLES_MAL_HECHAS'
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
WHERE expires_at IS NULL OR expires_at > NOW();

-- Create a view for expired detections
CREATE OR REPLACE VIEW expired_detections AS
SELECT *
FROM detections
WHERE expires_at IS NOT NULL AND expires_at <= NOW();

-- Create a view for detections expiring soon (within 1 day)
CREATE OR REPLACE VIEW expiring_soon_detections AS
SELECT *,
    EXTRACT(EPOCH FROM (expires_at - NOW())) / 3600 AS hours_until_expiration
FROM detections
WHERE expires_at IS NOT NULL
  AND expires_at > NOW()
  AND expires_at <= NOW() + INTERVAL '1 day'
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

    RETURN expiration_date <= NOW();
END;
$$ LANGUAGE plpgsql;

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

    IF expiration_date <= NOW() THEN
        RETURN 0;  -- Already expired
    END IF;

    days_remaining := EXTRACT(DAY FROM (expiration_date - NOW()));
    RETURN days_remaining;
END;
$$ LANGUAGE plpgsql;

-- Migration complete
