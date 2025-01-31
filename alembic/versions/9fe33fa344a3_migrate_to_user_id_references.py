"""migrate_to_user_id_references

Revision ID: 9fe33fa344a3
Revises: f531b974fbd7
Create Date: 2025-02-01 06:38:21.627980

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9fe33fa344a3'
down_revision: Union[str, None] = 'f531b974fbd7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ListingItemsテーブルの修正
    # 1. 新しいカラムの追加
    op.add_column('listing_items', sa.Column(
        'seller_user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_listing_items_seller_user_id',
                          'listing_items', 'users', ['seller_user_id'], ['id'])

    # 2. データの移行
    op.execute("""
        UPDATE listing_items li
        SET seller_user_id = sp.user_id
        FROM seller_profiles sp
        WHERE li.seller_id = sp.id
    """)

    # 3. 新しいカラムをNOT NULL制約に変更
    op.alter_column('listing_items', 'seller_user_id', nullable=False)

    # 4. 古いカラムとインデックスの削除
    op.drop_constraint('listing_items_seller_id_fkey',
                       'listing_items', type_='foreignkey')
    op.drop_column('listing_items', 'seller_id')

    # 5. 新しいインデックスの作成
    op.create_index('ix_listing_items_seller_user_created',
                    'listing_items', ['seller_user_id', 'created_at'])

    # Transactionsテーブルの修正
    # 1. 新しいカラムの追加
    op.add_column('transactions', sa.Column(
        'buyer_user_id', sa.Integer(), nullable=True))
    op.add_column('transactions', sa.Column(
        'seller_user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_transactions_buyer_user_id',
                          'transactions', 'users', ['buyer_user_id'], ['id'])
    op.create_foreign_key('fk_transactions_seller_user_id',
                          'transactions', 'users', ['seller_user_id'], ['id'])

    # 2. データの移行
    # buyer_user_idの移行
    op.execute("""
        UPDATE transactions t
        SET buyer_user_id = bp.user_id
        FROM buyer_profiles bp
        WHERE t.buyer_id = bp.id
    """)

    # seller_user_idの移行
    op.execute("""
        UPDATE transactions t
        SET seller_user_id = sp.user_id
        FROM seller_profiles sp
        WHERE t.seller_id = sp.id
    """)

    # 3. 新しいカラムをNOT NULL制約に変更
    op.alter_column('transactions', 'buyer_user_id', nullable=False)
    op.alter_column('transactions', 'seller_user_id', nullable=False)

    # 4. 古いカラムとインデックスの削除
    op.drop_constraint('transactions_buyer_id_fkey',
                       'transactions', type_='foreignkey')
    op.drop_constraint('transactions_seller_id_fkey',
                       'transactions', type_='foreignkey')
    op.drop_index('ix_transactions_buyer_created', table_name='transactions')
    op.drop_index('ix_transactions_seller_created', table_name='transactions')
    op.drop_column('transactions', 'buyer_id')
    op.drop_column('transactions', 'seller_id')

    # 5. 新しいインデックスの作成
    op.create_index('ix_transactions_buyer_user_created',
                    'transactions', ['buyer_user_id', 'created_at'])
    op.create_index('ix_transactions_seller_user_created',
                    'transactions', ['seller_user_id', 'created_at'])

    # SavedPaymentMethodsのインデックス修正は不要なので削除


def downgrade() -> None:
    # ListingItemsテーブルの修正を元に戻す
    # 1. 古いカラムの追加
    op.add_column('listing_items', sa.Column(
        'seller_id', sa.Integer(), nullable=True))
    op.create_foreign_key('listing_items_seller_id_fkey',
                          'listing_items', 'seller_profiles', ['seller_id'], ['id'])

    # 2. データの移行
    op.execute("""
        UPDATE listing_items li
        SET seller_id = sp.id
        FROM seller_profiles sp
        WHERE li.seller_user_id = sp.user_id
    """)

    # 3. 古いカラムをNOT NULL制約に変更
    op.alter_column('listing_items', 'seller_id', nullable=False)

    # 4. 新しいカラムとインデックスの削除
    op.drop_constraint('fk_listing_items_seller_user_id',
                       'listing_items', type_='foreignkey')
    op.drop_index('ix_listing_items_seller_user_created',
                  table_name='listing_items')
    op.drop_column('listing_items', 'seller_user_id')

    # 5. 古いインデックスの作成
    op.create_index('ix_listing_items_seller_created',
                    'listing_items', ['seller_id', 'created_at'])

    # Transactionsテーブルの修正を元に戻す
    # 1. 古いカラムの追加
    op.add_column('transactions', sa.Column(
        'buyer_id', sa.Integer(), nullable=True))
    op.add_column('transactions', sa.Column(
        'seller_id', sa.Integer(), nullable=True))
    op.create_foreign_key('transactions_buyer_id_fkey',
                          'transactions', 'buyer_profiles', ['buyer_id'], ['id'])
    op.create_foreign_key('transactions_seller_id_fkey',
                          'transactions', 'seller_profiles', ['seller_id'], ['id'])

    # 2. データの移行
    # buyer_idの移行
    op.execute("""
        UPDATE transactions t
        SET buyer_id = bp.id
        FROM buyer_profiles bp
        WHERE t.buyer_user_id = bp.user_id
    """)

    # seller_idの移行
    op.execute("""
        UPDATE transactions t
        SET seller_id = sp.id
        FROM seller_profiles sp
        WHERE t.seller_user_id = sp.user_id
    """)

    # 3. 古いカラムをNOT NULL制約に変更
    op.alter_column('transactions', 'buyer_id', nullable=False)
    op.alter_column('transactions', 'seller_id', nullable=False)

    # 4. 新しいカラムとインデックスの削除
    op.drop_constraint('fk_transactions_buyer_user_id',
                       'transactions', type_='foreignkey')
    op.drop_constraint('fk_transactions_seller_user_id',
                       'transactions', type_='foreignkey')
    op.drop_index('ix_transactions_buyer_user_created',
                  table_name='transactions')
    op.drop_index('ix_transactions_seller_user_created',
                  table_name='transactions')
    op.drop_column('transactions', 'buyer_user_id')
    op.drop_column('transactions', 'seller_user_id')

    # 5. 古いインデックスの作成
    op.create_index('ix_transactions_buyer_created',
                    'transactions', ['buyer_id', 'created_at'])
    op.create_index('ix_transactions_seller_created',
                    'transactions', ['seller_id', 'created_at'])

    # SavedPaymentMethodsのインデックス修正は不要なので削除
