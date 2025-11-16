-- Migration: Add UserSettings table
-- Date: 2025-01-08
-- Description: Create user_settings table for storing user preferences as JSONB

-- Create user_settings table
CREATE TABLE IF NOT EXISTS user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    settings JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Foreign key constraint
    CONSTRAINT fk_user_settings_user
        FOREIGN KEY (user_id)
        REFERENCES user_profiles(id)
        ON DELETE CASCADE
);

-- Create index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_settings_user_id ON user_settings(user_id);

-- Create index on settings JSONB for faster queries
CREATE INDEX IF NOT EXISTS idx_user_settings_settings ON user_settings USING gin(settings);

-- Add trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_user_settings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_user_settings_updated_at
    BEFORE UPDATE ON user_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_user_settings_updated_at();

-- Add default settings for existing users (optional)
INSERT INTO user_settings (user_id, settings)
SELECT
    id,
    '{
        "language": "es",
        "timezone": "America/Argentina/Buenos_Aires",
        "date_format": "DD/MM/YYYY",
        "email_notifications": true,
        "email_new_analysis": true,
        "email_validation_complete": false,
        "email_reports": true,
        "in_app_notifications": true,
        "default_confidence_threshold": 0.7,
        "default_include_gps": true,
        "auto_validate_high_confidence": false,
        "profile_visibility": "private",
        "share_analytics": false
    }'::jsonb
FROM user_profiles
WHERE NOT EXISTS (
    SELECT 1 FROM user_settings WHERE user_settings.user_id = user_profiles.id
);

-- Rollback script (save for reference)
-- DROP TRIGGER IF EXISTS trigger_user_settings_updated_at ON user_settings;
-- DROP FUNCTION IF EXISTS update_user_settings_updated_at();
-- DROP TABLE IF EXISTS user_settings CASCADE;
