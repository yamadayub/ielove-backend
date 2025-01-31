from app.config import Settings
from pathlib import Path
from pydantic_settings import SettingsConfigDict
import os
from dotenv import load_dotenv

# .env.developmentを読み込む
env_path = Path(__file__).parent.parent / ".env.development"
load_dotenv(env_path)

# 環境変数からwebhookシークレットを取得
TEST_WEBHOOK_SECRET = os.getenv("STRIPE_TRANSACTION_WEBHOOK_SECRET")
TEST_CONNECT_WEBHOOK_SECRET = os.getenv("STRIPE_CONNECT_WEBHOOK_SECRET")
TEST_TRANSFER_WEBHOOK_SECRET = os.getenv("STRIPE_TRANSFER_WEBHOOK_SECRET")


class TestSettings(Settings):
    """テスト用の設定クラス"""
    model_config = SettingsConfigDict(env_file=None)


def get_test_settings() -> Settings:
    """テスト用の設定を取得"""
    # テスト用のSQLiteデータベースのパスを作成
    test_db_path = Path(__file__).parent / "test.db"

    return TestSettings(
        # データベース設定
        DATABASE_URL=f"sqlite:///{test_db_path}",

        # Stripe設定
        STRIPE_SECRET_KEY="sk_test_dummy",
        STRIPE_TRANSACTION_WEBHOOK_SECRET=TEST_WEBHOOK_SECRET,
        STRIPE_CONNECT_WEBHOOK_SECRET=TEST_CONNECT_WEBHOOK_SECRET,
        STRIPE_TRANSFER_WEBHOOK_SECRET=TEST_TRANSFER_WEBHOOK_SECRET,
        STRIPE_CONNECT_REFRESH_URL="http://localhost:3000/seller/refresh",
        STRIPE_CONNECT_RETURN_URL="http://localhost:3000/seller/return",

        # アプリケーション設定
        BASE_URL="http://localhost:3000",
        ENVIRONMENT="test"
    )
