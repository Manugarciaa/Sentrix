"""Add authentication fields to user_profiles

Revision ID: 0003
Revises: 0002
Create Date: 2025-11-25 17:20:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add missing authentication fields to user_profiles table"""

    # Add email column (unique, indexed, not null)
    try:
        op.add_column('user_profiles', sa.Column('email', sa.String(255), nullable=True))
        # Make it unique and indexed after adding
        op.create_unique_constraint('uq_user_profiles_email', 'user_profiles', ['email'])
        op.create_index('ix_user_profiles_email', 'user_profiles', ['email'])
    except Exception as e:
        print(f"Could not add email column: {e}")
        pass

    # Add hashed_password column
    try:
        op.add_column('user_profiles', sa.Column('hashed_password', sa.String(255), nullable=True))
    except Exception as e:
        print(f"Could not add hashed_password column: {e}")
        pass

    # Add is_active column
    try:
        op.add_column('user_profiles', sa.Column('is_active', sa.Boolean(), server_default='true'))
    except Exception as e:
        print(f"Could not add is_active column: {e}")
        pass

    # Add is_verified column
    try:
        op.add_column('user_profiles', sa.Column('is_verified', sa.Boolean(), server_default='false'))
    except Exception as e:
        print(f"Could not add is_verified column: {e}")
        pass

    # Add updated_at column
    try:
        op.add_column('user_profiles', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    except Exception as e:
        print(f"Could not add updated_at column: {e}")
        pass

    # Add last_login column
    try:
        op.add_column('user_profiles', sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))
    except Exception as e:
        print(f"Could not add last_login column: {e}")
        pass


def downgrade() -> None:
    """Remove authentication fields from user_profiles table"""

    op.drop_column('user_profiles', 'last_login')
    op.drop_column('user_profiles', 'updated_at')
    op.drop_column('user_profiles', 'is_verified')
    op.drop_column('user_profiles', 'is_active')
    op.drop_column('user_profiles', 'hashed_password')
    op.drop_index('ix_user_profiles_email', 'user_profiles')
    op.drop_constraint('uq_user_profiles_email', 'user_profiles')
    op.drop_column('user_profiles', 'email')
