from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, List


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

    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "https://ielove-frontend-staging-4f3b275ce8ee.herokuapp.com"
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

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
