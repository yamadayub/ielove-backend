"""change id in users table and add clerk_user_id

Revision ID: 870b887e9593
Revises: 66e3b267e6bb
Create Date: 2024-12-21 10:33:39.193428

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '870b887e9593'
down_revision: Union[str, None] = '66e3b267e6bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. まず外部キー制約を削除
    op.drop_constraint('properties_user_id_fkey',
                       'properties', type_='foreignkey')
    op.drop_constraint('purchases_buyer_id_fkey',
                       'purchases', type_='foreignkey')
    op.drop_constraint('seller_profiles_user_id_fkey',
                       'seller_profiles', type_='foreignkey')

    # 2. カラムの型を変更（明示的な型変換を使用）
    op.execute(
        'ALTER TABLE properties ALTER COLUMN user_id TYPE INTEGER USING user_id::integer')
    op.execute(
        'ALTER TABLE purchases ALTER COLUMN buyer_id TYPE INTEGER USING buyer_id::integer')
    op.execute(
        'ALTER TABLE seller_profiles ALTER COLUMN user_id TYPE INTEGER USING user_id::integer')

    # 3. usersテーブルの変更
    op.add_column('users', sa.Column(
        'clerk_user_id', sa.String(), nullable=True))
    op.execute('UPDATE users SET clerk_user_id = id')

    # シーケンスの作成と紐付け
    op.execute('CREATE SEQUENCE IF NOT EXISTS users_id_seq')
    op.execute(
        "SELECT setval('users_id_seq', (SELECT MAX(id::integer) FROM users))")
    op.execute('ALTER TABLE users ALTER COLUMN id TYPE INTEGER USING id::integer')
    op.execute(
        "ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval('users_id_seq')")
    op.execute("ALTER SEQUENCE users_id_seq OWNED BY users.id")

    op.alter_column('users', 'clerk_user_id', nullable=False)
    op.create_unique_constraint(
        'uq_users_clerk_user_id', 'users', ['clerk_user_id'])

    # 4. 外部キー制約を再作成
    op.create_foreign_key('properties_user_id_fkey',
                          'properties', 'users', ['user_id'], ['id'])
    op.create_foreign_key('purchases_buyer_id_fkey',
                          'purchases', 'users', ['buyer_id'], ['id'])
    op.create_foreign_key('seller_profiles_user_id_fkey',
                          'seller_profiles', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    # 1. 外部キー制約を削除
    op.drop_constraint('properties_user_id_fkey',
                       'properties', type_='foreignkey')
    op.drop_constraint('purchases_buyer_id_fkey',
                       'purchases', type_='foreignkey')
    op.drop_constraint('seller_profiles_user_id_fkey',
                       'seller_profiles', type_='foreignkey')

    # 2. カラムの型を元に戻す
    op.execute(
        'ALTER TABLE properties ALTER COLUMN user_id TYPE VARCHAR USING user_id::text')
    op.execute(
        'ALTER TABLE purchases ALTER COLUMN buyer_id TYPE VARCHAR USING buyer_id::text')
    op.execute(
        'ALTER TABLE seller_profiles ALTER COLUMN user_id TYPE VARCHAR USING user_id::text')

    # 3. usersテーブルを元に戻す
    op.drop_constraint('uq_users_clerk_user_id', 'users', type_='unique')
    op.execute('ALTER TABLE users ALTER COLUMN id DROP DEFAULT')
    op.execute('ALTER TABLE users ALTER COLUMN id TYPE VARCHAR USING id::text')
    op.execute('UPDATE users SET id = clerk_user_id')
    op.drop_column('users', 'clerk_user_id')

    # シーケンスの削除
    op.execute('DROP SEQUENCE IF EXISTS users_id_seq')

    # 4. 外部キー制約を再作成
    op.create_foreign_key('properties_user_id_fkey',
                          'properties', 'users', ['user_id'], ['id'])
    op.create_foreign_key('purchases_buyer_id_fkey',
                          'purchases', 'users', ['buyer_id'], ['id'])
    op.create_foreign_key('seller_profiles_user_id_fkey',
                          'seller_profiles', 'users', ['user_id'], ['id'])
