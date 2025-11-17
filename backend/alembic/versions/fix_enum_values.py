"""Fix enum values and add missing location column

Revision ID: fix_enum_values
Revises:
Create Date: 2025-01-26 10:52:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = 'fix_enum_values'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Fix breeding_site_type enum to include our actual class names
    op.execute("ALTER TYPE breeding_site_type ADD VALUE IF NOT EXISTS 'Charcos/Cumulos de agua'")
    op.execute("ALTER TYPE breeding_site_type ADD VALUE IF NOT EXISTS 'Calles mal hechas'")
    op.execute("ALTER TYPE breeding_site_type ADD VALUE IF NOT EXISTS 'Huecos'")
    op.execute("ALTER TYPE breeding_site_type ADD VALUE IF NOT EXISTS 'Basura'")

    # Fix detection_risk enum to include our risk levels
    op.execute("ALTER TYPE detection_risk ADD VALUE IF NOT EXISTS 'ALTO'")
    op.execute("ALTER TYPE detection_risk ADD VALUE IF NOT EXISTS 'MEDIO'")
    op.execute("ALTER TYPE detection_risk ADD VALUE IF NOT EXISTS 'BAJO'")
    op.execute("ALTER TYPE detection_risk ADD VALUE IF NOT EXISTS 'MÍNIMO'")

    # Add location column to analyses table (PostGIS POINT)
    op.execute("ALTER TABLE analyses ADD COLUMN IF NOT EXISTS location geometry(POINT, 4326)")

    # Add risk_level column to analyses table if missing
    op.execute("ALTER TABLE analyses ADD COLUMN IF NOT EXISTS risk_level VARCHAR(10) DEFAULT 'BAJO'")


def downgrade() -> None:
    # Remove added columns
    op.drop_column('analyses', 'location')
    op.drop_column('analyses', 'risk_level')

    # Note: Cannot easily remove enum values in PostgreSQL without recreating the type
    pass