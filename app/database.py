# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from typing import Generator
from .config import get_settings
# import os

settings = get_settings()
# print("DATABASE_URL in database.py:", os.getenv("DATABASE_URL"))

# データベースURLの調整（Heroku対応）
database_url = settings.sqlalchemy_database_url
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://')

# エンジンの作成
engine = create_engine(
    database_url,
    pool_pre_ping=True,  # コネクションプールのヘルスチェック
    pool_size=5,  # コネクションプールのサイズ
    max_overflow=10,  # 最大オーバーフロー接続数
    # echo=settings.is_development,  # 開発環境の場合のみSQLログを出力
    echo=False
)

# セッションファクトリーの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# モデルのベースクラス
Base = declarative_base()


# 依存性注入用のセッション提供関数
def get_db() -> Generator:
    """
    データベースセッションを提供する依存性注入用のジェネレータ関数

    Yields:
        Session: データベースセッション

    Example:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
