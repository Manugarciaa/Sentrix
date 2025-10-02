-- ============================================================================
-- SENTRIX DATABASE SCHEMA - SUPABASE
-- ============================================================================
-- Execute this script in Supabase SQL Editor to create all tables
-- https://app.supabase.com/project/_/sql
-- ============================================================================

-- Enable PostGIS extension for GPS functionality
CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================================================
-- CREATE ENUMS
-- ============================================================================

-- Risk level enum (Spanish - matches backend)
CREATE TYPE risk_level_enum AS ENUM ('MÍNIMO', 'BAJO', 'MEDIO', 'ALTO');

-- Detection risk enum (Spanish - matches backend)
CREATE TYPE detection_risk_enum AS ENUM ('MÍNIMO', 'BAJO', 'MEDIO', 'ALTO');

-- Breeding site types (exact class names from YOLO)
CREATE TYPE breeding_site_type_enum AS ENUM (
    'Basura',
    'Calles mal hechas',
    'Charcos/Cumulos de agua',
    'Huecos'
);

-- User roles
CREATE TYPE user_role_enum AS ENUM ('admin', 'expert', 'user');

-- Location source
CREATE TYPE location_source_enum AS ENUM ('EXIF_GPS', 'MANUAL', 'ESTIMATED');

-- Validation status
CREATE TYPE validation_status_enum AS ENUM ('pending', 'confirmed', 'rejected');

-- ============================================================================
-- CREATE TABLES
-- ============================================================================

-- User profiles table
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role user_role_enum DEFAULT 'user',
    display_name TEXT,
    organization TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Analyses table (main analysis records)
CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES user_profiles(id),

    -- Image information
    image_url TEXT NOT NULL,
    image_filename TEXT,
    image_size_bytes INTEGER,

    -- GPS and location data
    location GEOGRAPHY(POINT, 4326),
    has_gps_data BOOLEAN DEFAULT FALSE,
    gps_altitude_meters DECIMAL(8, 2),
    gps_date TEXT,
    gps_timestamp TEXT,
    location_source location_source_enum,
    google_maps_url TEXT,
    google_earth_url TEXT,

    -- Camera metadata
    camera_make TEXT,
    camera_model TEXT,
    camera_datetime TEXT,
    camera_software TEXT,

    -- Detection results
    total_detections INTEGER DEFAULT 0,
    high_risk_count INTEGER DEFAULT 0,
    medium_risk_count INTEGER DEFAULT 0,
    risk_level risk_level_enum,
    risk_score DECIMAL(4, 3),
    recommendations TEXT[],

    -- Processing metadata
    model_used TEXT,
    confidence_threshold DECIMAL(3, 2),
    processing_time_ms INTEGER,
    yolo_service_version TEXT,

    -- Timestamps
    image_taken_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Detections table (individual detections within an analysis)
CREATE TABLE detections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES analyses(id) ON DELETE CASCADE,

    -- Detection classification
    class_id INTEGER,
    class_name TEXT,
    confidence DECIMAL(5, 4),
    risk_level detection_risk_enum,
    breeding_site_type breeding_site_type_enum,

    -- Detection geometry
    polygon JSONB,
    mask_area DECIMAL(12, 2),
    area_square_pixels DECIMAL(12, 2),

    -- Detection location (if different from analysis)
    location GEOGRAPHY(POINT, 4326),
    has_location BOOLEAN DEFAULT FALSE,
    detection_latitude DECIMAL(10, 8),
    detection_longitude DECIMAL(11, 8),
    detection_altitude_meters DECIMAL(8, 2),
    google_maps_url TEXT,
    google_earth_url TEXT,

    -- Source metadata
    source_filename TEXT,
    camera_make TEXT,
    camera_model TEXT,
    image_datetime TEXT,

    -- Validation
    requires_verification BOOLEAN DEFAULT TRUE,
    validated_by UUID REFERENCES user_profiles(id),
    validation_status validation_status_enum DEFAULT 'pending',
    validation_notes TEXT,
    validated_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- CREATE INDEXES
-- ============================================================================

-- Analyses indexes
CREATE INDEX idx_analyses_user ON analyses(user_id);
CREATE INDEX idx_analyses_created_at ON analyses(created_at DESC);
CREATE INDEX idx_analyses_risk ON analyses(risk_level);
CREATE INDEX idx_analyses_gps_data ON analyses(has_gps_data);
CREATE INDEX idx_analyses_camera ON analyses(camera_make, camera_model);

-- Spatial indexes for analyses (PostGIS)
CREATE INDEX idx_analyses_location ON analyses USING GIST(location);
CREATE INDEX idx_analyses_location_spgist ON analyses USING SPGIST(location);

-- Detections indexes
CREATE INDEX idx_detections_analysis ON detections(analysis_id);
CREATE INDEX idx_detections_risk ON detections(risk_level);
CREATE INDEX idx_detections_has_location ON detections(has_location);
CREATE INDEX idx_detections_validation ON detections(validation_status);

-- Spatial indexes for detections (PostGIS)
CREATE INDEX idx_detections_location ON detections USING GIST(location);
CREATE INDEX idx_detections_location_spgist ON detections USING SPGIST(location);

-- ============================================================================
-- CREATE TRIGGERS
-- ============================================================================

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for analyses.updated_at
CREATE TRIGGER trg_set_timestamp
BEFORE UPDATE ON analyses
FOR EACH ROW EXECUTE PROCEDURE set_timestamp();

-- ============================================================================
-- CREATE STORAGE BUCKETS (Execute in Supabase Dashboard or via SQL)
-- ============================================================================

-- NOTE: Execute these in Supabase Dashboard → Storage
-- Or use Supabase JavaScript client to create buckets

-- Bucket for original images
-- INSERT INTO storage.buckets (id, name, public) VALUES ('sentrix-images', 'sentrix-images', true);

-- Bucket for processed images with markers
-- INSERT INTO storage.buckets (id, name, public) VALUES ('sentrix-processed', 'sentrix-processed', true);

-- ============================================================================
-- GRANT PERMISSIONS (if using service role)
-- ============================================================================

-- Grant permissions to authenticated users
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO authenticated;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check if PostGIS is enabled
SELECT PostGIS_version();

-- List all tables
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- List all enums
SELECT n.nspname as schema, t.typname as type
FROM pg_type t
LEFT JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
WHERE (t.typrelid = 0 OR (SELECT c.relkind = 'c' FROM pg_catalog.pg_class c WHERE c.oid = t.typrelid))
AND NOT EXISTS(SELECT 1 FROM pg_catalog.pg_type el WHERE el.oid = t.typelem AND el.typarray = t.oid)
AND n.nspname NOT IN ('pg_catalog', 'information_schema')
AND t.typname LIKE '%enum'
ORDER BY 1, 2;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

SELECT 'Sentrix database schema created successfully! ✓' AS status;
