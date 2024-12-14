from logging.config import fileConfig
import sys
import os
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from app.database import Base
from app.models import *  # This imports all models
from app.config import get_settings

# このパスの追加はモジュールのインポートのために必要
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Alembic Configオブジェクトを取得
config = context.config

# 環境設定を取得とURL調整
settings = get_settings()
database_url = settings.sqlalchemy_database_url
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://')

# sqlalchemy.urlを環境変数から取得したURLで上書き
config.set_main_option("sqlalchemy.url", database_url)

# Pythonのロギング設定
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# メタデータオブジェクトの設定
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """
    'offline' モードでマイグレーションを実行
    SQLを生成するだけで実際には実行しない
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """
    'online' モードでマイグレーションを実行
    実際にデータベースに接続してマイグレーションを実行
    """
    # URL文字列を'postgresql://'形式に変換
    configuration = config.get_section(config.config_ini_section, {})
    if 'sqlalchemy.url' in configuration:
        if configuration['sqlalchemy.url'].startswith('postgres://'):
            configuration['sqlalchemy.url'] = configuration['sqlalchemy.url'].replace('postgres://', 'postgresql://')

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # カラムの型の変更を検知
            compare_server_default=True,  # デフォルト値の変更を検知
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()