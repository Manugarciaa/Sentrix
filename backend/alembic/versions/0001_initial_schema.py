"""Initial schema with PostGIS support

Revision ID: 0001
Revises:
Create Date: 2024-09-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable PostGIS extension
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')

    # Create ENUMs
    risk_level_enum = postgresql.ENUM('MINIMAL', 'LOW', 'MEDIUM', 'HIGH', name='risk_level_enum')
    detection_risk_enum = postgresql.ENUM('BAJO', 'MEDIO', 'ALTO', name='detection_risk_enum')
    breeding_site_type_enum = postgresql.ENUM('Basura', 'Calles mal hechas', 'Charcos/Cumulo de agua', 'Huecos', name='breeding_site_type_enum')
    user_role_enum = postgresql.ENUM('admin', 'expert', 'user', name='user_role_enum')
    location_source_enum = postgresql.ENUM('EXIF_GPS', 'MANUAL', 'ESTIMATED', name='location_source_enum')
    validation_status_enum = postgresql.ENUM('pending', 'confirmed', 'rejected', name='validation_status_enum')

    risk_level_enum.create(op.get_bind(), checkfirst=True)
    detection_risk_enum.create(op.get_bind(), checkfirst=True)
    breeding_site_type_enum.create(op.get_bind(), checkfirst=True)
    user_role_enum.create(op.get_bind(), checkfirst=True)
    location_source_enum.create(op.get_bind(), checkfirst=True)
    validation_status_enum.create(op.get_bind(), checkfirst=True)

    # Create user_profiles table
    op.create_table('user_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', user_role_enum, server_default='user'),
        sa.Column('display_name', sa.Text(), nullable=True),
        sa.Column('organization', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create analyses table
    op.create_table('analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=False),
        sa.Column('image_filename', sa.Text(), nullable=True),
        sa.Column('image_size_bytes', sa.Integer(), nullable=True),
        sa.Column('location', geoalchemy2.types.Geography(geometry_type='POINT', srid=4326, from_text='ST_GeogFromText', name='geography'), nullable=True),
        sa.Column('has_gps_data', sa.Boolean(), server_default='false'),
        sa.Column('gps_altitude_meters', sa.DECIMAL(precision=8, scale=2), nullable=True),
        sa.Column('gps_date', sa.Text(), nullable=True),
        sa.Column('gps_timestamp', sa.Text(), nullable=True),
        sa.Column('location_source', location_source_enum, nullable=True),
        sa.Column('camera_make', sa.Text(), nullable=True),
        sa.Column('camera_model', sa.Text(), nullable=True),
        sa.Column('camera_datetime', sa.Text(), nullable=True),
        sa.Column('camera_software', sa.Text(), nullable=True),
        sa.Column('google_maps_url', sa.Text(), nullable=True),
        sa.Column('google_earth_url', sa.Text(), nullable=True),
        sa.Column('total_detections', sa.Integer(), server_default='0'),
        sa.Column('high_risk_count', sa.Integer(), server_default='0'),
        sa.Column('medium_risk_count', sa.Integer(), server_default='0'),
        sa.Column('risk_level', risk_level_enum, nullable=True),
        sa.Column('risk_score', sa.DECIMAL(precision=4, scale=3), nullable=True),
        sa.Column('recommendations', sa.ARRAY(sa.Text()), nullable=True),
        sa.Column('model_used', sa.Text(), nullable=True),
        sa.Column('confidence_threshold', sa.DECIMAL(precision=3, scale=2), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('yolo_service_version', sa.Text(), nullable=True),
        sa.Column('image_taken_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create detections table
    op.create_table('detections',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('analysis_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('class_id', sa.Integer(), nullable=True),
        sa.Column('class_name', sa.Text(), nullable=True),
        sa.Column('confidence', sa.DECIMAL(precision=5, scale=4), nullable=True),
        sa.Column('risk_level', detection_risk_enum, nullable=True),
        sa.Column('polygon', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('mask_area', sa.DECIMAL(precision=12, scale=2), nullable=True),
        sa.Column('location', geoalchemy2.types.Geography(geometry_type='POINT', srid=4326, from_text='ST_GeogFromText', name='geography'), nullable=True),
        sa.Column('has_location', sa.Boolean(), server_default='false'),
        sa.Column('detection_latitude', sa.DECIMAL(precision=10, scale=8), nullable=True),
        sa.Column('detection_longitude', sa.DECIMAL(precision=11, scale=8), nullable=True),
        sa.Column('detection_altitude_meters', sa.DECIMAL(precision=8, scale=2), nullable=True),
        sa.Column('google_maps_url', sa.Text(), nullable=True),
        sa.Column('google_earth_url', sa.Text(), nullable=True),
        sa.Column('breeding_site_type', breeding_site_type_enum, nullable=True),
        sa.Column('area_square_pixels', sa.DECIMAL(precision=12, scale=2), nullable=True),
        sa.Column('requires_verification', sa.Boolean(), server_default='true'),
        sa.Column('source_filename', sa.Text(), nullable=True),
        sa.Column('camera_make', sa.Text(), nullable=True),
        sa.Column('camera_model', sa.Text(), nullable=True),
        sa.Column('image_datetime', sa.Text(), nullable=True),
        sa.Column('validated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('validation_status', validation_status_enum, server_default='pending'),
        sa.Column('validation_notes', sa.Text(), nullable=True),
        sa.Column('validated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['validated_by'], ['user_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for analyses
    op.create_index('idx_analyses_user', 'analyses', ['user_id'], unique=False)
    op.create_index('idx_analyses_created_at', 'analyses', ['created_at'], unique=False)
    op.create_index('idx_analyses_risk', 'analyses', ['risk_level'], unique=False)
    op.create_index('idx_analyses_gps_data', 'analyses', ['has_gps_data'], unique=False)
    op.create_index('idx_analyses_camera', 'analyses', ['camera_make', 'camera_model'], unique=False)

    # Create spatial indexes for analyses
    op.execute('CREATE INDEX idx_analyses_location ON analyses USING GIST(location)')
    op.execute('CREATE INDEX idx_analyses_location_spgist ON analyses USING SPGIST(location)')

    # Create indexes for detections
    op.create_index('idx_detections_analysis', 'detections', ['analysis_id'], unique=False)
    op.create_index('idx_detections_risk', 'detections', ['risk_level'], unique=False)
    op.create_index('idx_detections_has_location', 'detections', ['has_location'], unique=False)
    op.create_index('idx_detections_validation', 'detections', ['validation_status'], unique=False)

    # Create spatial indexes for detections
    op.execute('CREATE INDEX idx_detections_location ON detections USING GIST(location)')
    op.execute('CREATE INDEX idx_detections_location_spgist ON detections USING SPGIST(location)')

    # Create updated_at trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION set_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
          NEW.updated_at = NOW();
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger for analyses.updated_at
    op.execute("""
        CREATE TRIGGER trg_set_timestamp
        BEFORE UPDATE ON analyses
        FOR EACH ROW EXECUTE PROCEDURE set_timestamp();
    """)


def downgrade() -> None:
    # Drop triggers and functions
    op.execute('DROP TRIGGER IF EXISTS trg_set_timestamp ON analyses')
    op.execute('DROP FUNCTION IF EXISTS set_timestamp()')

    # Drop indexes
    op.drop_index('idx_detections_location_spgist', table_name='detections')
    op.drop_index('idx_detections_location', table_name='detections')
    op.drop_index('idx_detections_validation', table_name='detections')
    op.drop_index('idx_detections_has_location', table_name='detections')
    op.drop_index('idx_detections_risk', table_name='detections')
    op.drop_index('idx_detections_analysis', table_name='detections')

    op.drop_index('idx_analyses_location_spgist', table_name='analyses')
    op.drop_index('idx_analyses_location', table_name='analyses')
    op.drop_index('idx_analyses_camera', table_name='analyses')
    op.drop_index('idx_analyses_gps_data', table_name='analyses')
    op.drop_index('idx_analyses_risk', table_name='analyses')
    op.drop_index('idx_analyses_created_at', table_name='analyses')
    op.drop_index('idx_analyses_user', table_name='analyses')

    # Drop tables
    op.drop_table('detections')
    op.drop_table('analyses')
    op.drop_table('user_profiles')

    # Drop ENUMs
    op.execute('DROP TYPE IF EXISTS validation_status_enum')
    op.execute('DROP TYPE IF EXISTS location_source_enum')
    op.execute('DROP TYPE IF EXISTS user_role_enum')
    op.execute('DROP TYPE IF EXISTS breeding_site_type_enum')
    op.execute('DROP TYPE IF EXISTS detection_risk_enum')
    op.execute('DROP TYPE IF EXISTS risk_level_enum')

    # Drop PostGIS extension (commented out for safety)
    # op.execute('DROP EXTENSION IF EXISTS postgis')