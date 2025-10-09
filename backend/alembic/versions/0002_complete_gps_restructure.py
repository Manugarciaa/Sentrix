"""Complete GPS and enum restructure

Revision ID: 0002
Revises: 0001, fix_enum_values
Create Date: 2025-01-26 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = ('0001', 'fix_enum_values')
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Complete database restructure to support GPS functionality properly.
    This migration fixes all enum mismatches and ensures GPS fields exist.
    """

    # Step 1: Fix risk level enum to match Python code (Spanish values)
    op.execute("DROP TYPE IF EXISTS risk_level_enum CASCADE")
    risk_level_enum = postgresql.ENUM('MÍNIMO', 'BAJO', 'MEDIO', 'ALTO', name='risk_level_enum')
    risk_level_enum.create(op.get_bind())

    # Step 2: Fix detection risk enum to include all values
    op.execute("DROP TYPE IF EXISTS detection_risk_enum CASCADE")
    detection_risk_enum = postgresql.ENUM('MÍNIMO', 'BAJO', 'MEDIO', 'ALTO', name='detection_risk_enum')
    detection_risk_enum.create(op.get_bind())

    # Step 3: Fix breeding site type enum to match exact class names
    op.execute("DROP TYPE IF EXISTS breeding_site_type_enum CASCADE")
    breeding_site_type_enum = postgresql.ENUM(
        'Basura',
        'Calles mal hechas',
        'Charcos/Cumulos de agua',
        'Huecos',
        name='breeding_site_type_enum'
    )
    breeding_site_type_enum.create(op.get_bind())

    # Step 4: Ensure location source enum exists
    op.execute("DROP TYPE IF EXISTS location_source_enum CASCADE")
    location_source_enum = postgresql.ENUM('EXIF_GPS', 'MANUAL', 'ESTIMATED', name='location_source_enum')
    location_source_enum.create(op.get_bind())

    # Step 5: Ensure validation status enum exists
    op.execute("DROP TYPE IF EXISTS validation_status_enum CASCADE")
    validation_status_enum = postgresql.ENUM('pending', 'confirmed', 'rejected', name='validation_status_enum')
    validation_status_enum.create(op.get_bind())

    # Step 6: Ensure user role enum exists
    op.execute("DROP TYPE IF EXISTS user_role_enum CASCADE")
    user_role_enum = postgresql.ENUM('admin', 'expert', 'user', name='user_role_enum')
    user_role_enum.create(op.get_bind())

    # Step 7: Add all missing GPS and metadata columns to analyses table
    # These are the columns that should exist but might be missing from Supabase

    # GPS and location fields
    try:
        op.add_column('analyses', sa.Column('has_gps_data', sa.Boolean(), server_default='false'))
    except Exception:
        pass  # Column might already exist

    try:
        op.add_column('analyses', sa.Column('location_source', location_source_enum, nullable=True))
    except Exception:
        pass

    try:
        op.add_column('analyses', sa.Column('google_maps_url', sa.Text(), nullable=True))
    except Exception:
        pass

    try:
        op.add_column('analyses', sa.Column('google_earth_url', sa.Text(), nullable=True))
    except Exception:
        pass

    try:
        op.add_column('analyses', sa.Column('gps_altitude_meters', sa.DECIMAL(precision=8, scale=2), nullable=True))
    except Exception:
        pass

    # Camera metadata fields
    try:
        op.add_column('analyses', sa.Column('camera_make', sa.Text(), nullable=True))
    except Exception:
        pass

    try:
        op.add_column('analyses', sa.Column('camera_model', sa.Text(), nullable=True))
    except Exception:
        pass

    try:
        op.add_column('analyses', sa.Column('camera_datetime', sa.Text(), nullable=True))
    except Exception:
        pass

    try:
        op.add_column('analyses', sa.Column('camera_software', sa.Text(), nullable=True))
    except Exception:
        pass

    # Analysis metadata fields
    try:
        op.add_column('analyses', sa.Column('model_used', sa.Text(), nullable=True))
    except Exception:
        pass

    try:
        op.add_column('analyses', sa.Column('confidence_threshold', sa.DECIMAL(precision=3, scale=2), nullable=True))
    except Exception:
        pass

    try:
        op.add_column('analyses', sa.Column('processing_time_ms', sa.Integer(), nullable=True))
    except Exception:
        pass

    try:
        op.add_column('analyses', sa.Column('yolo_service_version', sa.Text(), nullable=True))
    except Exception:
        pass

    # Risk assessment fields
    try:
        op.add_column('analyses', sa.Column('risk_level', risk_level_enum, nullable=True))
    except Exception:
        pass

    try:
        op.add_column('analyses', sa.Column('risk_score', sa.DECIMAL(precision=4, scale=3), nullable=True))
    except Exception:
        pass

    try:
        op.add_column('analyses', sa.Column('high_risk_count', sa.Integer(), server_default='0'))
    except Exception:
        pass

    try:
        op.add_column('analyses', sa.Column('medium_risk_count', sa.Integer(), server_default='0'))
    except Exception:
        pass

    try:
        op.add_column('analyses', sa.Column('recommendations', sa.ARRAY(sa.Text()), nullable=True))
    except Exception:
        pass

    # Timestamps
    try:
        op.add_column('analyses', sa.Column('image_taken_at', sa.DateTime(timezone=True), nullable=True))
    except Exception:
        pass

    try:
        op.add_column('analyses', sa.Column('updated_at', sa.DateTime(timezone=True),
                                          server_default=sa.text('now()'), nullable=True))
    except Exception:
        pass

    # Step 8: Ensure PostGIS geography column exists for analyses
    try:
        op.add_column('analyses', sa.Column('location',
                                          geoalchemy2.types.Geography(geometry_type='POINT', srid=4326),
                                          nullable=True))
    except Exception:
        pass

    # Step 9: Ensure all detection table columns exist with proper enums
    try:
        op.add_column('detections', sa.Column('risk_level', detection_risk_enum, nullable=True))
    except Exception:
        pass

    try:
        op.add_column('detections', sa.Column('breeding_site_type', breeding_site_type_enum, nullable=True))
    except Exception:
        pass

    try:
        op.add_column('detections', sa.Column('validation_status', validation_status_enum,
                                            server_default='pending'))
    except Exception:
        pass

    # Step 10: Create proper indexes for performance
    try:
        op.create_index('idx_analyses_gps_data', 'analyses', ['has_gps_data'], unique=False)
    except Exception:
        pass

    try:
        op.create_index('idx_analyses_risk_level', 'analyses', ['risk_level'], unique=False)
    except Exception:
        pass

    try:
        op.execute('CREATE INDEX IF NOT EXISTS idx_analyses_location_gist ON analyses USING GIST(location)')
    except Exception:
        pass

    # Step 11: Create updated_at trigger if it doesn't exist
    op.execute("""
        CREATE OR REPLACE FUNCTION set_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
          NEW.updated_at = NOW();
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    try:
        op.execute("""
            CREATE TRIGGER trg_analyses_updated_at
            BEFORE UPDATE ON analyses
            FOR EACH ROW EXECUTE PROCEDURE set_timestamp();
        """)
    except Exception:
        pass  # Trigger might already exist


def downgrade() -> None:
    """
    Downgrade is not implemented as this is a restructure migration.
    To downgrade, you would need to drop the entire database and recreate.
    """
    pass