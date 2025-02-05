"""remove company_name and other unnecessary fields from seller_profiles

Revision ID: 322cdd2f5627
Revises: 8451c95f8759
Create Date: 2025-01-07 00:42:29.026139

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '322cdd2f5627'
down_revision: Union[str, None] = '8451c95f8759'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # まず既存のデータをNULLに更新
    op.execute("""
        UPDATE seller_profiles 
        SET company_name = NULL,
            representative_name = NULL,
            postal_code = NULL,
            address = NULL,
            phone_number = NULL,
            business_registration_number = NULL,
            tax_registration_number = NULL
        WHERE company_name IS NOT NULL 
           OR representative_name IS NOT NULL
           OR postal_code IS NOT NULL
           OR address IS NOT NULL
           OR phone_number IS NOT NULL
           OR business_registration_number IS NOT NULL
           OR tax_registration_number IS NOT NULL
    """)
    # その後カラムを削除
    op.drop_column('seller_profiles', 'company_name')
    op.drop_column('seller_profiles', 'representative_name')
    op.drop_column('seller_profiles', 'postal_code')
    op.drop_column('seller_profiles', 'address')
    op.drop_column('seller_profiles', 'phone_number')
    op.drop_column('seller_profiles', 'business_registration_number')
    op.drop_column('seller_profiles', 'tax_registration_number')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('seller_profiles',
                  sa.Column('tax_registration_number', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('seller_profiles',
                  sa.Column('business_registration_number', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('seller_profiles',
                  sa.Column('phone_number', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('seller_profiles',
                  sa.Column('address', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('seller_profiles',
                  sa.Column('postal_code', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('seller_profiles',
                  sa.Column('representative_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('seller_profiles',
                  sa.Column('company_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
