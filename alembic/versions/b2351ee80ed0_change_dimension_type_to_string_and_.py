"""change_dimension_type_to_string_and_make_fields_nullable

Revision ID: b2351ee80ed0
Revises: 2b906b85f67b
Create Date: 2024-01-11 07:14:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2351ee80ed0'
down_revision = '2b906b85f67b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # dimension_typeをEnumから文字列に変更し、nullableに設定
    op.execute(
        'ALTER TABLE product_dimensions ALTER COLUMN dimension_type DROP NOT NULL')
    op.execute(
        'ALTER TABLE product_dimensions ALTER COLUMN dimension_type TYPE varchar USING dimension_type::varchar')
    op.execute('DROP TYPE IF EXISTS dimensiontype')

    # valueとunitをnullableに変更
    op.alter_column('product_dimensions', 'value',
                    existing_type=sa.Float(),
                    nullable=True)
    op.alter_column('product_dimensions', 'unit',
                    existing_type=sa.String(),
                    nullable=True)


def downgrade() -> None:
    # valueとunitを非nullableに戻す
    op.alter_column('product_dimensions', 'value',
                    existing_type=sa.Float(),
                    nullable=False)
    op.alter_column('product_dimensions', 'unit',
                    existing_type=sa.String(),
                    nullable=False)

    # dimension_typeをEnumに戻し、非nullableに設定
    op.execute("""
        CREATE TYPE dimensiontype AS ENUM ('WIDTH', 'HEIGHT', 'DEPTH');
        ALTER TABLE product_dimensions ALTER COLUMN dimension_type TYPE dimensiontype USING dimension_type::dimensiontype;
        ALTER TABLE product_dimensions ALTER COLUMN dimension_type SET NOT NULL;
    """)
