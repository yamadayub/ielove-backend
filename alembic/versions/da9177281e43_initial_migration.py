
"""initial migration

Revision ID: da9177281e43
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from app.models import PropertyType, ImageType, CompanyType, UserType, UserRole, SaleType, SaleStatus, ConsultationType

# revision identifiers, used by Alembic.
revision = 'da9177281e43'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('properties',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('property_type', sa.Enum(PropertyType, name='propertytype', create_type=False), nullable=False),
        sa.Column('prefecture', sa.String(), nullable=False),
        sa.Column('layout', sa.String(), nullable=True),
        sa.Column('construction_year', sa.Integer(), nullable=True),
        sa.Column('construction_month', sa.Integer(), nullable=True),
        sa.Column('site_area', sa.Float(), nullable=True),
        sa.Column('building_area', sa.Float(), nullable=True),
        sa.Column('floor_count', sa.Integer(), nullable=True),
        sa.Column('structure', sa.String(), nullable=True),
        sa.Column('design_company_id', sa.Integer(), nullable=True),
        sa.Column('construction_company_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('properties')
