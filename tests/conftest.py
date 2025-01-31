import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.orm import Session
from datetime import datetime
from httpx import ASGITransport
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db, Base
from app.main import app
from app.config import get_settings
from app.models import User, BuyerProfile, SellerProfile, Property, ListingItem
from app.enums import ListingStatus, PropertyType, ListingType
from tests.test_settings import get_test_settings
from app.services.stripe_service import stripe_service, WebhookType

# テスト用の設定を取得
settings = get_test_settings()

# テスト用のデータベースエンジンを作成
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    isolation_level='SERIALIZABLE'
)

# テスト用の依存関係を上書き


def override_get_settings():
    return settings


app.dependency_overrides[get_settings] = override_get_settings

# stripe_serviceのwebhookシークレットをテスト用に置き換え
stripe_service.webhook_secrets = {
    WebhookType.PAYMENT: settings.STRIPE_TRANSACTION_WEBHOOK_SECRET,
    WebhookType.CONNECT: settings.STRIPE_CONNECT_WEBHOOK_SECRET,
    WebhookType.TRANSFER: settings.STRIPE_TRANSFER_WEBHOOK_SECRET
}


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """イベントループを作成"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def engine():
    """テスト用のデータベースエンジンを作成"""
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        isolation_level='SERIALIZABLE'
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def db(engine):
    """テスト用のデータベースセッションを作成"""
    connection = engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=connection,
        expire_on_commit=False
    )
    session = TestingSessionLocal()

    # テスト用のDBセッションを使用するように依存関係を上書き
    def override_get_db_for_test():
        try:
            yield session
        finally:
            pass  # セッションのクローズはテスト終了時に行う

    app.dependency_overrides[get_db] = override_get_db_for_test

    yield session

    # テスト終了時のクリーンアップ
    app.dependency_overrides[get_db] = override_get_db  # 元の依存関係に戻す
    session.close()
    transaction.rollback()
    connection.close()


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    """非同期HTTPクライアントを作成"""
    client = AsyncClient(transport=ASGITransport(
        app=app), base_url="http://test")
    yield client
    await client.aclose()


@pytest_asyncio.fixture
async def test_user(db: Session) -> User:
    """テスト用のユーザーを作成"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    user = User(
        clerk_user_id=f"test_clerk_user_id_{timestamp}",
        email=f"test_{timestamp}@example.com",
        name="Test User",
        user_type="individual",
        role="buyer",
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_buyer_profile(db: Session, test_user: User) -> BuyerProfile:
    """テスト用の購入者プロフィールを作成"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    buyer_profile = BuyerProfile(
        user_id=test_user.id,
        stripe_customer_id=f"cus_test_{timestamp}",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(buyer_profile)
    db.commit()
    db.refresh(buyer_profile)
    return buyer_profile


@pytest_asyncio.fixture
async def test_seller_profile(db: Session, test_user: User) -> SellerProfile:
    """テスト用の販売者プロフィールを作成"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    seller_profile = SellerProfile(
        user_id=test_user.id,
        stripe_account_id=f"acct_test_{timestamp}",
        stripe_account_type="standard",
        stripe_account_status="active",
        stripe_onboarding_completed=True,
        stripe_charges_enabled=True,
        stripe_payouts_enabled=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(seller_profile)
    db.commit()
    db.refresh(seller_profile)
    return seller_profile


@pytest_asyncio.fixture
async def test_property(db: Session, test_user: User) -> Property:
    """テスト用の物件を作成"""
    property = Property(
        user_id=test_user.id,
        name="Test Property",
        prefecture="Tokyo",
        property_type=PropertyType.HOUSE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(property)
    db.commit()
    db.refresh(property)
    return property


@pytest_asyncio.fixture
async def test_listing(db: Session, test_property: Property, test_seller_profile: SellerProfile) -> ListingItem:
    """テスト用のリスティングを作成"""
    listing = ListingItem(
        property_id=test_property.id,
        seller_id=test_seller_profile.id,
        title="Test Listing",
        description="Test Description",
        price=10000,
        listing_type=ListingType.PROPERTY_SPECS,
        status=ListingStatus.PUBLISHED,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing
