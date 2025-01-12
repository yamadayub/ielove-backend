"""add_product_specification_id_to_images

Revision ID: 928c36b47687
Revises: b2351ee80ed0
Create Date: 2024-01-11 07:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '928c36b47687'
down_revision = 'b2351ee80ed0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 外部キー制約を追加
    op.add_column('images',
                  sa.Column('product_specification_id',
                            sa.Integer(),
                            nullable=True))
    op.create_foreign_key(
        'fk_images_product_specification_id',
        'images',
        'product_specifications',
        ['product_specification_id'],
        ['id']
    )


def downgrade() -> None:
    # 外部キー制約を削除
    op.drop_constraint(
        'fk_images_product_specification_id',
        'images',
        type_='foreignkey'
    )
    op.drop_column('images', 'product_specification_id')
