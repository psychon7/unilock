"""add theme config to domains

Revision ID: 5e707f46356c
Revises: 
Create Date: 2025-07-04 02:54:46.123456

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '5e707f46356c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add theme_config column with default value
    op.add_column('domains', sa.Column('theme_config', JSONB, nullable=True))
    
    # Set default theme config for existing rows
    default_theme = {
        "primaryColor": "#3b82f6",
        "secondaryColor": "#6b7280",
        "logoUrl": None,
        "loginTheme": None
    }
    op.execute(
        f"""
        UPDATE domains 
        SET theme_config = '{default_theme}'::jsonb 
        WHERE theme_config IS NULL
        """
    )


def downgrade() -> None:
    # Remove theme_config column
    op.drop_column('domains', 'theme_config')
