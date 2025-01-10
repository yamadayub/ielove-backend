"""remove_cycle_option_and_add_logical_delete

Revision ID: 2b906b85f67b
Revises: 688204a0d631
Create Date: 2024-01-09 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b906b85f67b'
down_revision = '688204a0d631'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # cycleオプションを削除
    sequences = [
        'companies_id_seq',
        'product_categories_id_seq',
        'products_id_seq',
        'product_specifications_id_seq',
        'product_dimensions_id_seq',
        'rooms_id_seq',
        'properties_id_seq',
        'images_id_seq',
        'users_id_seq',
        'buyer_profiles_id_seq',
        'seller_profiles_id_seq',
        'saved_payment_methods_id_seq',
        'listing_items_id_seq',
        'transactions_id_seq',
        'transaction_audit_logs_id_seq',
        'transaction_error_logs_id_seq',
        'take_rates_id_seq'
    ]

    for seq in sequences:
        op.execute(f'ALTER SEQUENCE {seq} NO CYCLE;')

    # 論理削除フラグを追加
    op.add_column('properties',
                  sa.Column('is_deleted', sa.Boolean(),
                            nullable=False, server_default='false'))
    op.add_column('properties',
                  sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # cycleオプションを戻す
    sequences = [
        'companies_id_seq',
        'product_categories_id_seq',
        'products_id_seq',
        'product_specifications_id_seq',
        'product_dimensions_id_seq',
        'rooms_id_seq',
        'properties_id_seq',
        'images_id_seq',
        'users_id_seq',
        'buyer_profiles_id_seq',
        'seller_profiles_id_seq',
        'saved_payment_methods_id_seq',
        'listing_items_id_seq',
        'transactions_id_seq',
        'transaction_audit_logs_id_seq',
        'transaction_error_logs_id_seq',
        'take_rates_id_seq'
    ]

    for seq in sequences:
        op.execute(f'ALTER SEQUENCE {seq} CYCLE;')

    # 論理削除フラグを削除
    op.drop_column('properties', 'deleted_at')
    op.drop_column('properties', 'is_deleted')
