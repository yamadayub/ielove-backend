import stripe
from fastapi import HTTPException
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from enum import Enum

from app.config import get_settings
from app.models import Transaction, TransactionAuditLog, TransactionErrorLog, ListingItem
from app.enums import TransactionStatus, PaymentStatus, TransferStatus, ChangeType, ErrorType

settings = get_settings()

# Stripe APIキーの設定
stripe.api_key = settings.STRIPE_SECRET_KEY

# TransferStatusを示す定数を追加
STRIPE_TRANSFER_STATUS_PAID = "paid"
STRIPE_TRANSFER_STATUS_PENDING = "pending"
STRIPE_TRANSFER_STATUS_FAILED = "failed"


class WebhookType(Enum):
    PAYMENT = "payment"
    CONNECT = "connect"
    TRANSFER = "transfer"


class StripeService:
    """Stripe関連の処理を行うサービス"""

    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secrets = {
            WebhookType.PAYMENT: settings.STRIPE_TRANSACTION_WEBHOOK_SECRET,
            WebhookType.CONNECT: settings.STRIPE_CONNECT_WEBHOOK_SECRET,
            WebhookType.TRANSFER: settings.STRIPE_TRANSFER_WEBHOOK_SECRET
        }

    @staticmethod
    async def create_connect_account(email: str, business_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Stripe Connectアカウントを作成する"""
        try:
            account = stripe.Account.create(
                type="standard",
                email=email,
                business_profile=business_profile,
                capabilities={
                    "card_payments": {"requested": True},
                    "transfers": {"requested": True},
                },
            )
            return account
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def create_account_link(account_id: str) -> Dict[str, Any]:
        """オンボーディング用のアカウントリンクを生成する"""
        try:
            account_link = stripe.AccountLink.create(
                account=account_id,
                refresh_url=settings.STRIPE_CONNECT_REFRESH_URL,
                return_url=settings.STRIPE_CONNECT_RETURN_URL,
                type="account_onboarding",
            )
            return account_link
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def get_account_status(account_id: str) -> Dict[str, Any]:
        """アカウントの状態を取得する"""
        try:
            account = stripe.Account.retrieve(account_id)
            return {
                "charges_enabled": account.charges_enabled,
                "payouts_enabled": account.payouts_enabled,
                "details_submitted": account.details_submitted,
                "capabilities": account.capabilities,
            }
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def verify_webhook_signature(
        self,
        payload: bytes,
        sig_header: str,
        webhook_type: WebhookType
    ) -> Dict[str, Any]:
        """
        Webhookの署名を検証し、イベントを構築する

        Args:
            payload: Webhookのリクエストボディ
            sig_header: Stripe-Signature header
            webhook_type: WebhookのタイプPAYMENTまたはCONNECT
        """
        try:
            webhook_secret = self.webhook_secrets[webhook_type]
            print(f"[DEBUG] Webhook Type: {webhook_type.value}")
            print(f"[DEBUG] Webhook Secret: {webhook_secret}")
            print(f"[DEBUG] Signature Header: {sig_header}")

            # 署名ヘッダーの解析
            if sig_header:
                print("[DEBUG] Parsing signature components:")
                components = {
                    k: v for k, v in [
                        pair.split("=") for pair in sig_header.split(",")
                    ]
                }
                print(f"[DEBUG] Timestamp: {components.get('t')}")
                print(f"[DEBUG] v0 signature: {components.get('v0')}")
                print(f"[DEBUG] v1 signature: {components.get('v1')}")

            # ペイロードの確認
            print(f"[DEBUG] Payload length: {len(payload)}")
            print(f"[DEBUG] Payload type: {type(payload)}")
            print(f"[DEBUG] Payload preview: {payload[:100]}")

            # 署名検証
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            print("[DEBUG] Signature verification successful")
            return event

        except ValueError as e:
            print(f"[ERROR] ValueError in verify_webhook_signature: {str(e)}")
            print(f"[ERROR] Webhook Type: {webhook_type.value}")
            print(f"[ERROR] Secret Used: {webhook_secret}")
            raise ValueError(f"Invalid payload: {str(e)}")
        except stripe.error.SignatureVerificationError as e:
            print(f"[ERROR] SignatureVerificationError: {str(e)}")
            print(f"[ERROR] Webhook Type: {webhook_type.value}")
            print(f"[ERROR] Secret Used: {webhook_secret}")
            raise ValueError(f"Invalid signature: {str(e)}")
        except Exception as e:
            print(
                f"[ERROR] Unexpected error in verify_webhook_signature: {str(e)}")
            raise ValueError(f"Webhook verification failed: {str(e)}")

    @staticmethod
    async def create_account_login_link(account_id: str) -> Dict[str, Any]:
        """Stripeダッシュボードへのログインリンクを生成する"""
        try:
            login_link = stripe.Account.create_login_link(account_id)
            return login_link
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def handle_transfer_created(
        self,
        db: Session,
        transfer: Dict[str, Any]
    ) -> None:
        """
        transfer.createdイベントを処理する
        このイベントは売り手への送金が完了したことを示す
        """
        try:
            # 基本情報の取得
            transfer_id = transfer.get("id")
            is_reversed = transfer.get("reversed", False)
            source_transaction = transfer.get("source_transaction")

            print(f"[DEBUG] Transfer Created - Basic Info:")
            print(f"[DEBUG] transfer_id: {transfer_id}")
            print(f"[DEBUG] is_reversed: {is_reversed}")
            print(f"[DEBUG] source_transaction: {source_transaction}")
            print(f"[DEBUG] Full transfer object: {transfer}")

            # source_transactionからpayment_intent_idを取得
            if source_transaction.startswith('ch_'):
                print(
                    f"[DEBUG] Source transaction is a charge ID: {source_transaction}")
                try:
                    charge = stripe.Charge.retrieve(source_transaction)
                    print(f"[DEBUG] Retrieved charge object: {charge}")
                    payment_intent_id = charge.get('payment_intent')
                    print(
                        f"[DEBUG] Extracted payment_intent_id from charge: {payment_intent_id}")

                    if not payment_intent_id:
                        print(
                            f"[WARNING] No payment_intent found for charge {source_transaction}")
                        return
                except stripe.error.StripeError as e:
                    print(f"[ERROR] Error retrieving charge: {str(e)}")
                    return
            else:
                payment_intent_id = source_transaction
                print(
                    f"[DEBUG] Using source_transaction as payment_intent_id: {payment_intent_id}")

            # トランザクションの検索
            print(
                f"[DEBUG] Searching for transaction with payment_intent_id: {payment_intent_id}")
            transaction = db.query(Transaction).filter(
                Transaction.payment_intent_id == payment_intent_id
            ).first()

            if transaction:
                print(f"[DEBUG] Found existing transaction: {transaction.id}")
                # 既存のトランザクションを更新
                old_status = transaction.transfer_status.value if transaction.transfer_status else None
                print(f"[DEBUG] Current transfer_status: {old_status}")

                transaction.transfer_status = TransferStatus.SUCCEEDED if not is_reversed else TransferStatus.FAILED
                transaction.stripe_transfer_id = transfer_id
                transaction.updated_at = datetime.utcnow()

                print(
                    f"[DEBUG] Updated transfer_status to: {transaction.transfer_status.value}")

                # 監査ログを追加
                audit_log = TransactionAuditLog(
                    transaction_id=transaction.id,
                    change_type=ChangeType.TRANSFER_STATUS_UPDATED,
                    old_value=old_status,
                    new_value=transaction.transfer_status.value,
                    created_at=datetime.utcnow()
                )
                db.add(audit_log)
                print(
                    f"[DEBUG] Added audit log for status change: {old_status} -> {transaction.transfer_status.value}")
            else:
                print("[DEBUG] No existing transaction found, creating new one")
                # 新規トランザクションを作成
                try:
                    # Stripeから必要な情報を取得
                    charge = stripe.Charge.retrieve(source_transaction)
                    print(
                        f"[DEBUG] Retrieved charge for new transaction: {charge}")

                    checkout_session_id = charge.metadata.get(
                        "checkout_session_id")
                    print(
                        f"[DEBUG] Found checkout_session_id in charge metadata: {checkout_session_id}")

                    session = stripe.checkout.Session.retrieve(
                        checkout_session_id)
                    print(f"[DEBUG] Retrieved checkout session: {session}")

                    metadata = session.metadata
                    print(f"[DEBUG] Session metadata: {metadata}")

                    transaction = Transaction(
                        listing_id=int(metadata["listing_id"]),
                        buyer_id=int(metadata["buyer_id"]),
                        seller_id=int(metadata["seller_id"]),
                        payment_intent_id=payment_intent_id,
                        stripe_transfer_id=transfer_id,
                        total_amount=charge.amount,
                        platform_fee=int(metadata["platform_fee"]),
                        seller_amount=int(metadata["transfer_amount"]),
                        transaction_status=TransactionStatus.COMPLETED,
                        payment_status=PaymentStatus.SUCCEEDED,
                        transfer_status=TransferStatus.SUCCEEDED if not is_reversed else TransferStatus.FAILED,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(transaction)
                    print("[DEBUG] Created new transaction object")
                except stripe.error.StripeError as e:
                    print(
                        f"[ERROR] Error creating transaction from Stripe data: {str(e)}")
                    return

            print("[DEBUG] Committing transaction to database")
            db.commit()
            print("[DEBUG] Successfully committed transaction")

        except Exception as e:
            db.rollback()
            print(f"[ERROR] Error in handle_transfer_created: {str(e)}")
            print(f"[ERROR] Full error details: {repr(e)}")
            if transaction and transaction.id:
                error_log = TransactionErrorLog(
                    transaction_id=transaction.id,
                    error_type=ErrorType.WEBHOOK_PROCESSING_ERROR,
                    error_message=str(e),
                    created_at=datetime.utcnow()
                )
                db.add(error_log)
                db.commit()
                print(
                    f"[DEBUG] Added error log for transaction {transaction.id}")
            raise

    async def handle_checkout_completed(
        self,
        db: Session,
        session: Dict[str, Any]
    ) -> None:
        """
        checkout.session.completedイベントを処理する
        このイベントは支払いが完了したことを示す
        """
        try:
            # メタデータの取得
            metadata = session.get("metadata", {})
            listing_id = int(metadata["listing_id"])
            buyer_id = int(metadata["buyer_id"])
            seller_id = int(metadata["seller_id"])
            payment_intent_id = session.get("payment_intent")
            total_amount = session.get("amount_total")

            # トランザクションの作成
            transaction = Transaction(
                listing_id=listing_id,
                buyer_id=buyer_id,
                seller_id=seller_id,
                payment_intent_id=payment_intent_id,
                total_amount=total_amount,
                platform_fee=int(metadata["platform_fee"]),
                seller_amount=int(metadata["transfer_amount"]),
                transaction_status=TransactionStatus.COMPLETED,
                payment_status=PaymentStatus.SUCCEEDED,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(transaction)
            db.commit()

        except Exception as e:
            db.rollback()
            print(f"Error in handle_checkout_completed: {str(e)}")
            raise

    async def create_checkout_session(
        self,
        listing_item: Any,
        buyer_profile: Any,
        seller_profile: Any,
    ) -> Dict[str, Any]:
        """Stripeのチェックアウトセッションを作成する"""
        try:
            # 手数料計算（30%）
            total_amount = listing_item.price
            platform_fee = int(total_amount * 0.3)
            transfer_amount = total_amount - platform_fee

            session = stripe.checkout.Session.create(
                mode='payment',
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'jpy',
                        'product_data': {
                            'name': f'物件情報: {listing_item.property.name}',
                            'description': listing_item.description or '',
                        },
                        'unit_amount': listing_item.price,
                    },
                    'quantity': 1,
                }],
                payment_intent_data={
                    'application_fee_amount': platform_fee,  # プラットフォーム手数料
                    'transfer_data': {
                        'destination': seller_profile.stripe_account_id,  # 送金先のConnect アカウント
                    },
                },
                metadata={
                    'listing_id': str(listing_item.id),
                    'buyer_id': str(buyer_profile.id),
                    'seller_id': str(seller_profile.id),
                    'platform_fee': str(platform_fee),
                    'transfer_amount': str(transfer_amount)
                },
                customer=buyer_profile.stripe_customer_id,
                success_url=f"{settings.BASE_URL}/checkout/success",
                cancel_url=f"{settings.BASE_URL}/checkout/cancel",
            )
            return {
                'sessionId': session.id,
                'url': session.url,
            }
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=500,
                detail={
                    'error': 'Stripe Error',
                    'message': str(e)
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    'error': 'System Error',
                    'message': str(e)
                }
            )


stripe_service = StripeService()
