#!/usr/bin/env python3
"""
Setup Supabase tables for Sentrix Backend
Configurar tablas de Supabase para Sentrix Backend
"""

import os
import sys
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_supabase_client():
    """Get Supabase client"""
    from supabase import create_client

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase credentials")

    return create_client(supabase_url, supabase_key)


def execute_sql(cursor, sql, description):
    """Execute SQL with error handling"""
    try:
        cursor.execute(sql)
        print(f"OK {description}")
        return True
    except Exception as e:
        error_msg = str(e).lower()
        if 'already exists' in error_msg:
            print(f"INFO {description} (already exists)")
            return True
        else:
            print(f"FAIL {description}: {e}")
            return False


def setup_database_tables():
    """Setup database tables directly with PostgreSQL"""
    print("=== Setting up Supabase Database Tables ===")

    try:
        import psycopg2
        from urllib.parse import urlparse

        database_url = os.getenv('DATABASE_URL')
        parsed = urlparse(database_url)

        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password
        )

        cursor = conn.cursor()

        # Create custom types (enums)
        enums_sql = [
            """
            CREATE TYPE user_role AS ENUM ('user', 'analyst', 'expert', 'admin');
            """,
            """
            CREATE TYPE risk_level AS ENUM ('MINIMAL', 'LOW', 'MEDIUM', 'HIGH');
            """,
            """
            CREATE TYPE detection_risk AS ENUM ('LOW', 'MEDIUM', 'HIGH');
            """,
            """
            CREATE TYPE breeding_site_type AS ENUM ('Basura', 'Calles_deterioradas', 'Charcos/Cumulo de agua', 'Hoyos/Depresiones');
            """,
            """
            CREATE TYPE location_source AS ENUM ('EXIF_GPS', 'USER_INPUT', 'ESTIMATED', 'NONE');
            """,
            """
            CREATE TYPE validation_status AS ENUM ('pending', 'approved', 'rejected', 'needs_review');
            """
        ]

        for sql in enums_sql:
            execute_sql(cursor, sql, f"Create enum")

        # Create user_profiles table
        user_profiles_sql = """
        CREATE TABLE IF NOT EXISTS user_profiles (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            role user_role DEFAULT 'user',
            display_name TEXT,
            organization TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        execute_sql(cursor, user_profiles_sql, "Create user_profiles table")

        # Create analyses table
        analyses_sql = """
        CREATE TABLE IF NOT EXISTS analyses (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES user_profiles(id),
            image_url TEXT NOT NULL,
            image_filename TEXT,
            image_size_bytes INTEGER,

            -- Geolocalización (simplified without PostGIS)
            latitude DECIMAL(10, 8),
            longitude DECIMAL(11, 8),
            has_gps_data BOOLEAN DEFAULT FALSE,
            gps_altitude_meters DECIMAL(8, 2),
            gps_date TEXT,
            gps_timestamp TEXT,
            location_source location_source,

            -- Metadata de cámara
            camera_make TEXT,
            camera_model TEXT,
            camera_datetime TEXT,
            camera_software TEXT,

            -- URLs de verificación
            google_maps_url TEXT,
            google_earth_url TEXT,

            -- Contadores de detecciones
            total_detections INTEGER DEFAULT 0,
            high_risk_count INTEGER DEFAULT 0,
            medium_risk_count INTEGER DEFAULT 0,
            risk_level risk_level,
            risk_score DECIMAL(4, 3),
            recommendations TEXT[],

            -- Configuración de procesamiento
            model_used TEXT,
            confidence_threshold DECIMAL(3, 2),
            processing_time_ms INTEGER,
            yolo_service_version TEXT,

            -- Timestamps
            image_taken_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        execute_sql(cursor, analyses_sql, "Create analyses table")

        # Create detections table
        detections_sql = """
        CREATE TABLE IF NOT EXISTS detections (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            analysis_id UUID REFERENCES analyses(id) ON DELETE CASCADE,

            -- Información básica de detección
            class_id INTEGER,
            class_name TEXT,
            confidence DECIMAL(5, 4),
            risk_level detection_risk,

            -- Geometría (stored as JSON)
            polygon JSONB,
            mask_area DECIMAL(12, 2),

            -- Geolocalización específica de esta detección
            detection_latitude DECIMAL(10, 8),
            detection_longitude DECIMAL(11, 8),
            detection_altitude_meters DECIMAL(8, 2),
            has_location BOOLEAN DEFAULT FALSE,

            -- URLs de verificación específicas
            google_maps_url TEXT,
            google_earth_url TEXT,

            -- Metadata para backend integration
            breeding_site_type breeding_site_type,
            area_square_pixels DECIMAL(12, 2),
            requires_verification BOOLEAN DEFAULT TRUE,

            -- Información de imagen fuente
            source_filename TEXT,
            camera_make TEXT,
            camera_model TEXT,
            image_datetime TEXT,

            -- Validación por expertos
            validated_by UUID REFERENCES user_profiles(id),
            validation_status validation_status DEFAULT 'pending',
            validation_notes TEXT,
            validated_at TIMESTAMPTZ,

            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        execute_sql(cursor, detections_sql, "Create detections table")

        # Create indexes for better performance
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_analyses_risk_level ON analyses(risk_level);",
            "CREATE INDEX IF NOT EXISTS idx_detections_analysis_id ON detections(analysis_id);",
            "CREATE INDEX IF NOT EXISTS idx_detections_validation_status ON detections(validation_status);",
            "CREATE INDEX IF NOT EXISTS idx_detections_risk_level ON detections(risk_level);"
        ]

        for sql in indexes_sql:
            execute_sql(cursor, sql, "Create index")

        # Commit changes
        conn.commit()
        cursor.close()
        conn.close()

        print("\nOK All database tables created successfully!")
        return True

    except Exception as e:
        print(f"FAIL Database setup failed: {e}")
        traceback.print_exc()
        return False


def test_table_creation():
    """Test that tables were created correctly"""
    print("\n=== Testing Table Creation ===")

    try:
        import psycopg2
        from urllib.parse import urlparse

        database_url = os.getenv('DATABASE_URL')
        parsed = urlparse(database_url)

        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password
        )

        cursor = conn.cursor()

        # Check if tables exist
        tables_to_check = ['user_profiles', 'analyses', 'detections']

        for table in tables_to_check:
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = %s;
            """, (table,))

            result = cursor.fetchone()
            if result:
                print(f"OK Table '{table}' exists")
            else:
                print(f"FAIL Table '{table}' not found")
                return False

        # Test basic operations
        cursor.execute("SELECT COUNT(*) FROM user_profiles;")
        user_count = cursor.fetchone()[0]
        print(f"OK user_profiles table accessible (count: {user_count})")

        cursor.execute("SELECT COUNT(*) FROM analyses;")
        analysis_count = cursor.fetchone()[0]
        print(f"OK analyses table accessible (count: {analysis_count})")

        cursor.execute("SELECT COUNT(*) FROM detections;")
        detection_count = cursor.fetchone()[0]
        print(f"OK detections table accessible (count: {detection_count})")

        cursor.close()
        conn.close()

        print("\nOK All tables are working correctly!")
        return True

    except Exception as e:
        print(f"FAIL Table test failed: {e}")
        return False


def create_sample_data():
    """Create some sample data for testing"""
    print("\n=== Creating Sample Data ===")

    try:
        supabase = get_supabase_client()

        # Create a sample user
        user_data = {
            "display_name": "Test User",
            "role": "user",
            "organization": "Sentrix Test"
        }

        user_response = supabase.table('user_profiles').insert(user_data).execute()

        if user_response.data:
            user_id = user_response.data[0]['id']
            print(f"OK Created sample user: {user_id}")

            # Create a sample analysis
            analysis_data = {
                "user_id": user_id,
                "image_url": "https://example.com/test_image.jpg",
                "image_filename": "test_image.jpg",
                "has_gps_data": True,
                "latitude": -26.831314,
                "longitude": -65.195539,
                "total_detections": 2,
                "risk_level": "MEDIUM",
                "confidence_threshold": 0.5,
                "model_used": "yolo11s-seg"
            }

            analysis_response = supabase.table('analyses').insert(analysis_data).execute()

            if analysis_response.data:
                analysis_id = analysis_response.data[0]['id']
                print(f"OK Created sample analysis: {analysis_id}")

                # Create sample detections
                detection_data = [
                    {
                        "analysis_id": analysis_id,
                        "class_id": 0,
                        "class_name": "Basura",
                        "confidence": 0.75,
                        "risk_level": "MEDIUM",
                        "breeding_site_type": "Basura",
                        "has_location": True,
                        "detection_latitude": -26.831314,
                        "detection_longitude": -65.195539,
                        "polygon": {"coordinates": [[100, 100], [200, 100], [200, 200], [100, 200]]},
                        "mask_area": 10000.0
                    },
                    {
                        "analysis_id": analysis_id,
                        "class_id": 2,
                        "class_name": "Charcos/Cumulo de agua",
                        "confidence": 0.85,
                        "risk_level": "HIGH",
                        "breeding_site_type": "Charcos/Cumulo de agua",
                        "has_location": True,
                        "detection_latitude": -26.831320,
                        "detection_longitude": -65.195545,
                        "polygon": {"coordinates": [[150, 150], [250, 150], [250, 250], [150, 250]]},
                        "mask_area": 10000.0
                    }
                ]

                detection_response = supabase.table('detections').insert(detection_data).execute()

                if detection_response.data:
                    print(f"OK Created {len(detection_response.data)} sample detections")
                else:
                    print("FAIL Could not create sample detections")
            else:
                print("FAIL Could not create sample analysis")
        else:
            print("FAIL Could not create sample user")

        return True

    except Exception as e:
        print(f"FAIL Sample data creation failed: {e}")
        return False


def main():
    """Main setup function"""
    print("Sentrix Supabase Database Setup")
    print("=" * 50)

    success = True

    # Setup tables
    if not setup_database_tables():
        success = False

    # Test tables
    if not test_table_creation():
        success = False

    # Create sample data
    if success:
        create_sample_data()

    print("\n" + "=" * 50)
    if success:
        print("OK Supabase database setup completed successfully!")
        print("\nNext steps:")
        print("1. Your database is ready for the Sentrix backend")
        print("2. You can now run the backend server")
        print("3. Check the Supabase dashboard to see your tables")
    else:
        print("FAIL Some setup steps failed. Check the errors above.")

    return success


if __name__ == "__main__":
    main()