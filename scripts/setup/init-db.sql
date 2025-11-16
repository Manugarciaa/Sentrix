-- Sentrix Database Initialization Script
-- This script runs when PostgreSQL container first starts

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Create schema if needed
-- CREATE SCHEMA IF NOT EXISTS sentrix;

-- Grant privileges
-- GRANT ALL PRIVILEGES ON SCHEMA sentrix TO sentrix_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA sentrix TO sentrix_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA sentrix TO sentrix_user;

-- Success message
SELECT 'PostGIS extension enabled successfully' AS status;
