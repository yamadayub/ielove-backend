import stripe
from fastapi import HTTPException
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from enum import Enum
from sqlalchemy import or_

from app.config import get_settings
from app.models import Transaction, TransactionAuditLog, TransactionErrorLog, ListingItem, User, BuyerProfile
from app.enums import TransactionStatus, PaymentStatus, TransferStatus, ChangeType, ErrorType
from app.services.take_rate_service import take_rate_service

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


class StripeService:
    """Stripe関連の処理を行うサービス"""

    def __init__(self):
        settings = get_settings()
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.frontend_url = settings.BASE_URL
        self.webhook_secrets = {
            WebhookType.PAYMENT: settings.STRIPE_TRANSACTION_WEBHOOK_SECRET,
            WebhookType.CONNECT: settings.STRIPE_CONNECT_WEBHOOK_SECRET
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
            print("[DEBUG] Processing checkout.session.completed event")
            transaction_id = session.get("metadata", {}).get("transaction_id")
            payment_intent_id = session.get("payment_intent")
            charge_id = None

            if not transaction_id:
                print("[WARNING] No transaction_id found in session metadata")
                return

            # payment_intentからcharge_idを取得
            if payment_intent_id:
                payment_intent = stripe.PaymentIntent.retrieve(
                    payment_intent_id)
                charge_id = payment_intent.latest_charge
                print(f"[DEBUG] Payment Intent ID: {payment_intent_id}")
                print(f"[DEBUG] Charge ID: {charge_id}")

            # transaction_idでトランザクションを検索
            print(
                f"[DEBUG] Searching for transaction with ID: {transaction_id}")
            transaction = db.query(Transaction).filter(
                Transaction.id == int(transaction_id)
            ).first()

            if transaction:
                print(f"[DEBUG] Found transaction: {transaction.id}")
                # 既存のトランザクションを更新
                transaction.payment_intent_id = payment_intent_id
                transaction.charge_id = charge_id
                transaction.transaction_status = TransactionStatus.COMPLETED
                transaction.updated_at = datetime.utcnow()
                print(
                    "[DEBUG] Updated transaction with payment_intent_id and charge_id")

                # 監査ログを追加
                audit_log = TransactionAuditLog(
                    transaction_id=transaction.id,
                    field_name="transaction_status",
                    change_type=ChangeType.WEBHOOK,
                    old_value=transaction.transaction_status.value if transaction.transaction_status else None,
                    new_value=TransactionStatus.COMPLETED.value
                )
                db.add(audit_log)
                print("[DEBUG] Added audit log for transaction status update")

                print("[DEBUG] Committing transaction")
                db.commit()
                print("[DEBUG] Successfully committed transaction")
            else:
                print(
                    f"[WARNING] No transaction found for ID: {transaction_id}")

        except Exception as e:
            db.rollback()
            print(f"[ERROR] Error in handle_checkout_completed: {str(e)}")
            print(f"[ERROR] Full error details: {repr(e)}")
            raise

    async def create_checkout_session(
        self,
        listing_item: ListingItem,
        buyer_profile: BuyerProfile,
        seller: User,
        transaction_id: int,
        platform_fee: int,
        transfer_amount: int
    ) -> Dict[str, str]:
        """Stripeのチェックアウトセッションを作成する"""

        print("[DEBUG] Creating Stripe checkout session")

        if not seller.seller_profile or not seller.seller_profile.stripe_account_id:
            raise ValueError("Seller does not have a Stripe account")

        try:
            # セッションのパラメータを構築
            session_params = {
                "mode": "payment",
                "payment_method_types": ["card"],
                "line_items": [{
                    "price_data": {
                        "currency": "jpy",
                        "product_data": {
                            "name": listing_item.title,
                            "description": listing_item.description
                        },
                        "unit_amount": listing_item.price
                    },
                    "quantity": 1
                }],
                "payment_intent_data": {
                    "transfer_data": {
                        "destination": seller.seller_profile.stripe_account_id,
                        "amount": transfer_amount
                    },
                    "metadata": {
                        "transaction_id": str(transaction_id),
                        "buyer_user_id": str(buyer_profile.user_id),
                        "seller_user_id": str(listing_item.seller_user_id)
                    }
                },
                "success_url": f"{self.frontend_url}/checkout/success",
                "cancel_url": f"{self.frontend_url}/checkout/cancel",
                "metadata": {
                    "transaction_id": str(transaction_id),
                    "buyer_user_id": str(buyer_profile.user_id),
                    "seller_user_id": str(listing_item.seller_user_id)
                }
            }

            # customer_idが存在する場合のみ追加
            if buyer_profile.stripe_customer_id:
                session_params["customer"] = buyer_profile.stripe_customer_id

            # セッションの作成
            session = stripe.checkout.Session.create(**session_params)

            print(f"[DEBUG] Created session: {session.id}")
            print(f"[DEBUG] Payment Intent ID: {session.payment_intent}")

            # payment_intent_idをトランザクションに保存
            if session.payment_intent:
                payment_intent = stripe.PaymentIntent.retrieve(
                    session.payment_intent)
                transaction = db.query(Transaction).filter(
                    Transaction.id == transaction_id
                ).first()
                if transaction:
                    transaction.payment_intent_id = session.payment_intent
                    transaction.updated_at = datetime.utcnow()
                    db.commit()
                    print(
                        f"[DEBUG] Updated transaction with payment_intent_id: {session.payment_intent}")

            return {
                "sessionId": session.id,
                "url": session.url
            }
        except stripe.error.StripeError as e:
            print(f"[ERROR] Stripe error in create_checkout_session: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    'error': 'Stripe Error',
                    'message': str(e)
                }
            )
        except Exception as e:
            print(f"[ERROR] System error in create_checkout_session: {str(e)}")
            print(f"[ERROR] Full error details: {repr(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    'error': 'System Error',
                    'message': str(e)
                }
            )

    async def handle_payment_intent_succeeded(
        self,
        db: Session,
        payment_intent: Dict[str, Any]
    ) -> None:
        """
        payment_intent.succeededイベントを処理する
        このイベントは支払いが完了したことを示す
        """
        try:
            print("[DEBUG] Processing payment_intent.succeeded event")
            transaction_id = payment_intent.get(
                "metadata", {}).get("transaction_id")
            charge_id = payment_intent.get("latest_charge")

            if not transaction_id:
                print("[WARNING] No transaction_id found in payment_intent metadata")
                return

            print(f"[DEBUG] Transaction ID: {transaction_id}")
            print(f"[DEBUG] Latest Charge ID: {charge_id}")

            # transaction_idでトランザクションを検索
            print(
                f"[DEBUG] Searching for transaction with ID: {transaction_id}")
            transaction = db.query(Transaction).filter(
                Transaction.id == int(transaction_id)
            ).first()

            if transaction:
                print(f"[DEBUG] Found transaction: {transaction.id}")
                # 既存のトランザクションを更新
                transaction.charge_id = charge_id
                transaction.payment_status = PaymentStatus.SUCCEEDED
                # 支払い成功時点でtransfer_statusもSUCCEEDEDに更新
                transaction.transfer_status = TransferStatus.SUCCEEDED
                transaction.updated_at = datetime.utcnow()
                print(
                    "[DEBUG] Updated payment_status and transfer_status to SUCCEEDED and set charge_id")

                # 監査ログを追加（payment_status）
                payment_audit_log = TransactionAuditLog(
                    transaction_id=transaction.id,
                    field_name="payment_status",
                    change_type=ChangeType.WEBHOOK,
                    old_value=transaction.payment_status.value if transaction.payment_status else None,
                    new_value=PaymentStatus.SUCCEEDED.value
                )
                db.add(payment_audit_log)

                # 監査ログを追加（transfer_status）
                transfer_audit_log = TransactionAuditLog(
                    transaction_id=transaction.id,
                    field_name="transfer_status",
                    change_type=ChangeType.WEBHOOK,
                    old_value=transaction.transfer_status.value if transaction.transfer_status else None,
                    new_value=TransferStatus.SUCCEEDED.value
                )
                db.add(transfer_audit_log)
                print("[DEBUG] Added audit logs for status updates")

                print("[DEBUG] Committing transaction")
                db.commit()
                print("[DEBUG] Successfully committed transaction")
            else:
                print(
                    f"[WARNING] No transaction found for ID: {transaction_id}")

        except Exception as e:
            db.rollback()
            print(
                f"[ERROR] Error in handle_payment_intent_succeeded: {str(e)}")
            print(f"[ERROR] Full error details: {repr(e)}")
            raise


stripe_service = StripeService()
