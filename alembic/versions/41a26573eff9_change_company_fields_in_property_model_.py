"""change company fields in property model to string

Revision ID: 41a26573eff9
Revises: 928c36b47687
Create Date: 2025-01-16 13:13:57.499731

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '41a26573eff9'
down_revision: Union[str, None] = '928c36b47687'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop foreign key constraints
    op.drop_constraint('properties_design_company_id_fkey',
                       'properties', type_='foreignkey')
    op.drop_constraint('properties_construction_company_id_fkey',
                       'properties', type_='foreignkey')

    # Drop old columns
    op.drop_column('properties', 'design_company_id')
    op.drop_column('properties', 'construction_company_id')

    # Add new string columns
    op.add_column('properties', sa.Column(
        'design_company', sa.String(), nullable=True))
    op.add_column('properties', sa.Column(
        'construction_company', sa.String(), nullable=True))


def downgrade() -> None:
    # Drop new columns
    op.drop_column('properties', 'design_company')
    op.drop_column('properties', 'construction_company')

    # Add old columns back
    op.add_column('properties', sa.Column('design_company_id',
                  sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('properties', sa.Column('construction_company_id',
                  sa.INTEGER(), autoincrement=False, nullable=True))

    # Add foreign key constraints back
    op.create_foreign_key('properties_design_company_id_fkey',
                          'properties', 'companies', ['design_company_id'], ['id'])
    op.create_foreign_key('properties_construction_company_id_fkey',
                          'properties', 'companies', ['construction_company_id'], ['id'])
