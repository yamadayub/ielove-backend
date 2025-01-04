from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional, List
import os


class Settings(BaseSettings):
    # 環境設定
    ENVIRONMENT: str = "development"

    # データベース設定
    DATABASE_URL: str

    # AWS設定
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_REGION: str = "ap-northeast-1"

    # CORS設定
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "https://ielove-frontend-staging-4f3b275ce8ee.herokuapp.com",
        "https://ie-love.com",
        "http://ie-love.com",
        "https://www.ie-love.com",
        "http://www.ie-love.com",
    ]

    # JWT設定
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Clerk設定
    CLERK_SECRET_KEY: Optional[str] = None
    CLERK_PUBLISHABLE_KEY: Optional[str] = None

    # Stripe設定
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_TRANSACTION_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_CONNECT_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_CONNECT_CLIENT_ID: Optional[str] = None
    STRIPE_CONNECT_RETURN_URL: str
    STRIPE_CONNECT_REFRESH_URL: str
    STRIPE_TRANSFER_WEBHOOK_SECRET: str

    # フロントエンドURL
    BASE_URL: str

    model_config = SettingsConfigDict(
        # 環境変数から設定ファイルを決定
        env_file=f".env.{os.getenv('ENVIRONMENT', 'development')}",
        env_file_encoding="utf-8",
        # 指定した.envファイルが存在しない場合は.envを使用
        env_file_fallback=True,
        # 大文字小文字を区別しない（環境変数は通常大文字）
        case_sensitive=False
    )

    @property
    def sqlalchemy_database_url(self) -> str:
        """
        環境に応じたデータベースURLを返す

        Returns:
            str: データベース接続URL
        """
        if self.ENVIRONMENT in ["staging", "production"]:
            # HerokuのPostgreSQLではSSL接続が必要
            return f"{self.DATABASE_URL}?sslmode=require"
        return self.DATABASE_URL

    @property
    def is_development(self) -> bool:
        """開発環境かどうかを返す"""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """本番環境かどうかを返す"""
        return self.ENVIRONMENT == "production"

    @property
    def is_staging(self) -> bool:
        """ステージング環境かどうかを返す"""
        return self.ENVIRONMENT == "staging"

    @property
    def aws_configured(self) -> bool:
        """AWS認証情報が設定されているかどうかを返す"""
        return all([
            self.AWS_ACCESS_KEY_ID,
            self.AWS_SECRET_ACCESS_KEY,
            self.AWS_S3_BUCKET
        ])

    @property
    def stripe_configured(self) -> bool:
        """Stripe認証情報が設定されているかどうかを返す"""
        return all([
            self.STRIPE_SECRET_KEY,
            self.STRIPE_PUBLISHABLE_KEY,
            self.STRIPE_TRANSACTION_WEBHOOK_SECRET,
            self.STRIPE_CONNECT_WEBHOOK_SECRET,
            self.STRIPE_CONNECT_CLIENT_ID,
            self.STRIPE_CONNECT_RETURN_URL,
            self.STRIPE_CONNECT_REFRESH_URL
        ])


# settingsインスタンスを作成
settings = Settings()


@lru_cache
def get_settings() -> Settings:
    """
    設定インスタンスを取得（キャッシュ付き）

    Returns:
        Settings: 設定インスタンス
    """
    return settings
