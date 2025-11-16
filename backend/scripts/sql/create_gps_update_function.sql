-- ============================================
-- FUNCIÓN RPC PARA ACTUALIZAR UBICACIÓN GPS
-- ============================================
-- Esta función permite actualizar el campo 'location' (Geography)
-- desde el código Python a través de Supabase RPC

-- Drop function if exists
DROP FUNCTION IF EXISTS update_analysis_location(uuid, numeric, numeric);

-- Create function to update analysis location
CREATE OR REPLACE FUNCTION update_analysis_location(
    analysis_uuid UUID,
    lat NUMERIC,
    lng NUMERIC
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER  -- Ejecuta con permisos del owner (bypass RLS)
AS $$
BEGIN
    -- Update the location field using PostGIS
    -- Note: ST_MakePoint takes (longitude, latitude) order
    UPDATE analyses
    SET location = ST_SetSRID(ST_MakePoint(lng, lat), 4326)
    WHERE id = analysis_uuid;

    -- Log the update
    RAISE NOTICE 'Updated location for analysis % to (%, %)', analysis_uuid, lat, lng;
END;
$$;

-- Grant execute permission to authenticated users and service role
GRANT EXECUTE ON FUNCTION update_analysis_location(uuid, numeric, numeric) TO authenticated;
GRANT EXECUTE ON FUNCTION update_analysis_location(uuid, numeric, numeric) TO service_role;

-- Test the function (optional)
-- SELECT update_analysis_location('some-uuid-here'::uuid, -26.8319, -65.1945);

COMMENT ON FUNCTION update_analysis_location IS 'Updates the PostGIS location field for an analysis given latitude and longitude';
