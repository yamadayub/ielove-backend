"""add status to images

Revision ID: a339975b5ad2
Revises: 870b887e9593
Create Date: 2024-01-26 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a339975b5ad2'
down_revision: Union[str, None] = '870b887e9593'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### 1. まずnullableなカラムとして追加
    op.add_column('images', sa.Column('status', sa.String(), nullable=True))

    # ### 2. 既存のレコードを更新
    op.execute("UPDATE images SET status = 'completed' WHERE status IS NULL")

    # ### 3. NOT NULL制約を追加
    op.alter_column('images', 'status',
                    existing_type=sa.String(),
                    nullable=False)

    # ### その他の変更
    op.alter_column('images', 'image_type',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.create_index('ix_images_id', 'images', ['id'], unique=False)


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_images_id', table_name='images')
    op.alter_column('images', 'image_type',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.drop_column('images', 'status')
    # ### end Alembic commands ###
