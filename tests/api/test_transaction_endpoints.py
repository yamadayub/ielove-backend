import pytest
import pytest_asyncio
import json
import hmac
import hashlib
import time
from unittest.mock import patch, MagicMock
from httpx import AsyncClient
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Transaction, User, BuyerProfile, SellerProfile, ListingItem, Property
from app.enums import TransactionStatus, PaymentStatus, TransferStatus
from datetime import datetime
from tests.test_settings import (
    TEST_WEBHOOK_SECRET,
    TEST_CONNECT_WEBHOOK_SECRET,
    TEST_TRANSFER_WEBHOOK_SECRET
)

# テストデータ
MOCK_CHECKOUT_SESSION_COMPLETED = {
    "id": "evt_test_123",
    "type": "checkout.session.completed",
    "data": {
        "object": {
            "id": "cs_test_123",
            "payment_intent": "pi_test_123",
        }
    }
}

MOCK_PAYMENT_INTENT_SUCCEEDED = {
    "id": "evt_test_456",
    "type": "payment_intent.succeeded",
    "data": {
        "object": {
            "id": "pi_test_123",
            "latest_charge": "ch_test_123"
        }
    }
}

MOCK_TRANSFER_CREATED = {
    "id": "evt_test_789",
    "type": "transfer.created",
    "data": {
        "object": {
            "id": "tr_test_123",
            "source_transaction": "ch_test_123"
        }
    }
}


def generate_stripe_signature(payload: dict, secret: str) -> str:
    """Stripeのwebhook署名を生成する"""
    timestamp = int(time.time())
    payload_str = json.dumps(payload, separators=(',', ':'))  # コンパクトなJSON
    signed_payload = f"{timestamp}.{payload_str}"
    signature = hmac.new(
        secret.encode('utf-8'),
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"t={timestamp},v1={signature}"


@pytest_asyncio.fixture
async def test_checkout_transaction(db: Session, test_user: User, test_buyer_profile: BuyerProfile, test_seller_profile: SellerProfile, test_listing: ListingItem):
    """checkout.session.completedテスト用のトランザクション"""
    transaction = Transaction(
        listing_id=test_listing.id,
        buyer_user_id=test_buyer_profile.user_id,
        seller_user_id=test_seller_profile.user_id,
        session_id="cs_test_123",  # これが重要
        payment_intent_id=None,
        charge_id=None,
        total_amount=10000,
        platform_fee=1000,
        seller_amount=9000,
        transaction_status=TransactionStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
        transfer_status=TransferStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@pytest_asyncio.fixture
async def test_payment_transaction(db: Session, test_user: User, test_buyer_profile: BuyerProfile, test_seller_profile: SellerProfile, test_listing: ListingItem):
    """payment_intent.succeededテスト用のトランザクション"""
    transaction = Transaction(
        listing_id=test_listing.id,
        buyer_user_id=test_buyer_profile.user_id,
        seller_user_id=test_seller_profile.user_id,
        session_id="cs_other_123",
        payment_intent_id="pi_test_123",  # これが重要
        charge_id=None,
        total_amount=10000,
        platform_fee=1000,
        seller_amount=9000,
        transaction_status=TransactionStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
        transfer_status=TransferStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@pytest_asyncio.fixture
async def test_transfer_transaction(db: Session, test_user: User, test_buyer_profile: BuyerProfile, test_seller_profile: SellerProfile, test_listing: ListingItem):
    """transfer.createdテスト用のトランザクション"""
    transaction = Transaction(
        listing_id=test_listing.id,
        buyer_user_id=test_buyer_profile.user_id,
        seller_user_id=test_seller_profile.user_id,
        session_id="cs_other_456",
        payment_intent_id="pi_test_123",
        charge_id="ch_test_123",  # これが重要
        total_amount=10000,
        platform_fee=1000,
        seller_amount=9000,
        transaction_status=TransactionStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
        transfer_status=TransferStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@pytest.mark.asyncio
@patch('stripe.PaymentIntent.retrieve')
@patch('stripe.Charge.retrieve')
async def test_webhook_checkout_session_completed(
    mock_charge,
    mock_payment_intent,
    async_client: AsyncClient,
    db: Session,
    test_checkout_transaction: Transaction
):
    """checkout.session.completedイベントのテスト"""
    # モックの設定
    mock_payment_intent.return_value = MagicMock(
        id="pi_test_123",
        latest_charge="ch_test_123",
        status="succeeded"
    )
    mock_charge.return_value = MagicMock(
        id="ch_test_123",
        payment_intent="pi_test_123"
    )

    # webhookリクエストを送信
    signature = generate_stripe_signature(
        MOCK_CHECKOUT_SESSION_COMPLETED, TEST_WEBHOOK_SECRET)
    response = await async_client.post(
        "/api/transactions/webhook",
        json=MOCK_CHECKOUT_SESSION_COMPLETED,
        headers={"stripe-signature": signature}
    )

    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    # 同じセッションで状態を確認
    db.expire_all()  # キャッシュをクリア
    updated_transaction = db.query(Transaction).filter_by(
        id=test_checkout_transaction.id
    ).first()
    assert updated_transaction.transaction_status == TransactionStatus.COMPLETED
    assert updated_transaction.payment_intent_id == "pi_test_123"
    assert updated_transaction.charge_id == "ch_test_123"


@pytest.mark.asyncio
@patch('stripe.PaymentIntent.retrieve')
@patch('stripe.Charge.retrieve')
async def test_webhook_payment_intent_succeeded(
    mock_charge,
    mock_payment_intent,
    async_client: AsyncClient,
    db: Session,
    test_payment_transaction: Transaction
):
    """payment_intent.succeededイベントのテスト"""
    # モックの設定
    mock_payment_intent.return_value = MagicMock(
        id="pi_test_123",
        latest_charge="ch_test_123",
        status="succeeded"
    )
    mock_charge.return_value = MagicMock(
        id="ch_test_123",
        payment_intent="pi_test_123"
    )

    # webhookリクエストを送信
    signature = generate_stripe_signature(
        MOCK_PAYMENT_INTENT_SUCCEEDED, TEST_WEBHOOK_SECRET)
    response = await async_client.post(
        "/api/transactions/webhook",
        json=MOCK_PAYMENT_INTENT_SUCCEEDED,
        headers={"stripe-signature": signature}
    )

    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    # 同じセッションで状態を確認
    db.expire_all()  # キャッシュをクリア
    updated_transaction = db.query(Transaction).filter_by(
        id=test_payment_transaction.id
    ).first()
    assert updated_transaction.payment_status == PaymentStatus.SUCCEEDED
    assert updated_transaction.payment_intent_id == "pi_test_123"
    assert updated_transaction.charge_id == "ch_test_123"


@pytest.mark.asyncio
@patch('stripe.PaymentIntent.retrieve')
@patch('stripe.Charge.retrieve')
async def test_webhook_transfer_created(
    mock_charge,
    mock_payment_intent,
    async_client: AsyncClient,
    db: Session,
    test_transfer_transaction: Transaction
):
    """transfer.createdイベントのテスト"""
    # モックの設定
    mock_payment_intent.return_value = MagicMock(
        id="pi_test_123",
        latest_charge="ch_test_123",
        status="succeeded"
    )
    mock_charge.return_value = MagicMock(
        id="ch_test_123",
        payment_intent="pi_test_123"
    )

    # webhookリクエストを送信
    signature = generate_stripe_signature(
        MOCK_TRANSFER_CREATED, TEST_TRANSFER_WEBHOOK_SECRET)
    response = await async_client.post(
        "/api/transactions/webhook/connect",
        json=MOCK_TRANSFER_CREATED,
        headers={"stripe-signature": signature}
    )

    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    # 同じセッションで状態を確認
    db.expire_all()  # キャッシュをクリア
    updated_transaction = db.query(Transaction).filter_by(
        id=test_transfer_transaction.id
    ).first()
    assert updated_transaction.transfer_status == TransferStatus.SUCCEEDED
    assert updated_transaction.stripe_transfer_id == "tr_test_123"
    assert updated_transaction.charge_id == "ch_test_123"
