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

    async def handle_checkout_completed(
        self,
        db: Session,
        session: Dict[str, Any]
    ) -> None:
        """
        checkout.session.completedイベントを処理する

        Args:
            db: データベースセッション
            session: Stripeのセッションデータ
        """
        transaction_id = None
        try:
            print(f"Received checkout session data: {session}")

            # 基本的なセッション検証
            if session.get("mode") != "payment":
                raise ValueError("Invalid checkout session mode")

            # メタデータの取得と検証
            metadata = session.get("metadata", {})
            print(f"Received metadata: {metadata}")
            required_metadata = ["listing_id", "buyer_id", "seller_id"]
            if not all(key in metadata for key in required_metadata):
                raise ValueError(
                    f"Required metadata is missing: {required_metadata}")

            listing_id = int(metadata["listing_id"])
            buyer_id = int(metadata["buyer_id"])
            seller_id = int(metadata["seller_id"])
            print(
                f"Parsed IDs - listing: {listing_id}, buyer: {buyer_id}, seller: {seller_id}")

            # ListingItemの取得と検証
            listing_item = db.query(ListingItem).filter(
                ListingItem.id == listing_id
            ).first()
            if not listing_item:
                raise ValueError(f"Listing not found: {listing_id}")
            print(f"Found listing item: {listing_item.id}")

            # 同一ユーザーによる購入済みかどうかの確認
            existing_purchase = db.query(Transaction).filter(
                Transaction.listing_id == listing_id,
                Transaction.buyer_id == buyer_id,
                Transaction.transaction_status == TransactionStatus.COMPLETED
            ).first()
            if existing_purchase:
                raise ValueError(
                    f"You have already purchased listing {listing_id}")

            # payment_intent_idの取得と検証
            payment_intent_id = session.get("payment_intent")
            if not payment_intent_id:
                raise ValueError("Payment intent ID is missing")
            print(f"Payment intent ID: {payment_intent_id}")

            # 既存のトランザクションをチェック（べき等性の確保）
            existing_transaction = db.query(Transaction).filter(
                Transaction.payment_intent_id == payment_intent_id
            ).first()
            if existing_transaction:
                print(f"Transaction already exists: {existing_transaction.id}")
                return  # 既に処理済みの場合は何もしない

            # 金額の取得（複数の方法に対応）
            total_amount = (
                session.get("amount_total") or
                listing_item.price  # リスティングの価格をフォールバックとして使用
            )
            print(f"Total amount: {total_amount}")

            # 支払い状態の検証
            payment_status = session.get("payment_status")
            if payment_status != "paid":
                raise ValueError(f"Invalid payment status: {payment_status}")

            # 金額の計算
            platform_fee = int(total_amount * 0.05)  # 5%のプラットフォーム手数料
            seller_amount = total_amount - platform_fee
            print(
                f"Calculated amounts - platform fee: {platform_fee}, seller amount: {seller_amount}")

            # トランザクションの作成
            transaction = Transaction(
                listing_id=listing_id,
                buyer_id=buyer_id,
                seller_id=seller_id,
                payment_intent_id=payment_intent_id,
                total_amount=total_amount,
                platform_fee=platform_fee,
                seller_amount=seller_amount,
                transaction_status=TransactionStatus.COMPLETED,
                payment_status=PaymentStatus.SUCCEEDED,  # PAIDではなくSUCCEEDEDを使用
                transfer_status=TransferStatus.PENDING,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(transaction)
            db.flush()  # IDを生成するためにflush
            transaction_id = transaction.id
            print(f"Created transaction with ID: {transaction.id}")

            # 監査ログの作成
            audit_log = TransactionAuditLog(
                transaction_id=transaction.id,
                field_name="status",
                old_value=None,
                new_value=TransactionStatus.COMPLETED.value,
                changed_by_user_id=None,  # システムによる変更
                change_type=ChangeType.SYSTEM,
                change_reason="Transaction created from Stripe checkout",
                change_metadata={
                    "payment_intent_id": payment_intent_id,
                    "checkout_session_id": session.get("id")  # 参照用に保存
                }
            )
            db.add(audit_log)
            print("Added audit log")

            # 変更をコミット
            db.commit()
            print("Successfully committed transaction and audit log")

        except ValueError as e:
            print(f"Validation error: {str(e)}")
            db.rollback()  # トランザクションをロールバック
            # バリデーションエラーの記録
            error_log = TransactionErrorLog(
                transaction_id=transaction_id,  # トランザクションIDがある場合は設定
                error_type=ErrorType.VALIDATION_ERROR,
                error_code="CHECKOUT_VALIDATION_ERROR",
                error_message=str(e),
                error_details={
                    "session_id": session.get("id"),
                    "metadata": session.get("metadata")
                }
            )
            db.add(error_log)
            db.commit()
            raise HTTPException(status_code=400, detail=str(e))

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            db.rollback()  # トランザクションをロールバック
            # 予期せぬエラーの記録
            error_log = TransactionErrorLog(
                transaction_id=transaction_id,  # トランザクションIDがある場合は設定
                error_type=ErrorType.SYSTEM_ERROR,
                error_code="CHECKOUT_SYSTEM_ERROR",
                error_message=str(e),
                error_details={
                    "session_id": session.get("id"),
                    "metadata": session.get("metadata")
                }
            )
            db.add(error_log)
            db.commit()
            raise HTTPException(
                status_code=500, detail="Internal server error")

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
