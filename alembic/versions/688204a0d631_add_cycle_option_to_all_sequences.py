"""add_cycle_option_to_all_sequences

Revision ID: 688204a0d631
Revises: ab6a086fabcd
Create Date: 2024-01-09 21:36:47.013744

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '688204a0d631'
down_revision = 'ab6a086fabcd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 各テーブルのシーケンスにcycleオプションを追加
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


def downgrade() -> None:
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
