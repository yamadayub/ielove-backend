# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import get_settings

settings = get_settings()

# エンジンの作成
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # コネクションプールのヘルスチェック
    echo=settings.ENVIRONMENT == "development"  # 開発環境の場合、SQLログを出力
)

# セッションファクトリーの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# モデルのベースクラス
Base = declarative_base()

# 依存性注入用のセッション提供関数


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
