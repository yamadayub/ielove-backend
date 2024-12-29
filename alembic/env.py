from app.database import Base
from app.config import get_settings
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from sqlalchemy import create_engine
import os
import sys

# このパスの追加はモジュールのインポートのために必要
current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, current_path)


# 環境設定を取得とURL調整
settings = get_settings()
database_url = settings.sqlalchemy_database_url

if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://')

# Alembic Configオブジェクトを取得
config = context.config

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
    # 最初に設定したURLを使用
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        echo=False
    )

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
