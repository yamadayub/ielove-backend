from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from datetime import datetime
from typing import Dict, Any

from app.auth.dependencies import get_db, get_current_user
from app.models import User, Property, ListingItem, Transaction, BuyerProfile
from app.enums import TransactionStatus, ListingStatus
from app.schemas.transaction_schemas import (
    TransactionCheckResponse,
    PurchasedTransactionsResponse,
    PurchasedTransaction,
    PropertyInfo,
    ListingInfo
)
from app.schemas.checkout_schemas import CheckoutSessionCreate, CheckoutSessionResponse
from app.services.stripe_service import stripe_service, WebhookType
from app.services.buyer_profile_service import buyer_profile_service

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/purchased", response_model=PurchasedTransactionsResponse)
async def get_purchased_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> PurchasedTransactionsResponse:
    """ログインユーザーの購入済み物件一覧を取得"""

    # BuyerProfileの取得
    buyer_profile = db.query(BuyerProfile).filter(
        BuyerProfile.user_id == current_user.id
    ).first()

    if not buyer_profile:
        return PurchasedTransactionsResponse(transactions=[])

    # 購入済み取引の取得
    transactions = db.query(Transaction).join(
        ListingItem, Transaction.listing_id == ListingItem.id
    ).join(
        Property, ListingItem.property_id == Property.id
    ).filter(
        and_(
            Transaction.buyer_id == buyer_profile.id,
            Transaction.transaction_status == TransactionStatus.COMPLETED
        )
    ).options(
        joinedload(Transaction.listing).joinedload(ListingItem.property)
    ).order_by(
        Transaction.created_at.desc()
    ).all()

    # レスポンスの作成
    return PurchasedTransactionsResponse(
        transactions=[
            PurchasedTransaction(
                id=transaction.id,
                purchaseDate=transaction.created_at,
                totalAmount=transaction.total_amount,
                listing=ListingInfo(
                    id=transaction.listing.id,
                    title=transaction.listing.title,
                    price=transaction.listing.price
                ),
                property=PropertyInfo(
                    id=transaction.listing.property.id,
                    name=transaction.listing.property.name,
                    prefecture=transaction.listing.property.prefecture
                )
            )
            for transaction in transactions
        ]
    )


@router.get("/check", response_model=TransactionCheckResponse)
async def check_transaction_status(
    property_id: int = Query(..., description="確認対象の物件ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TransactionCheckResponse:
    """
    指定された物件に対する取引状態を確認します。
    """
    # 物件の存在確認
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")

    # BuyerProfileの取得
    buyer_profile = db.query(BuyerProfile).filter(
        BuyerProfile.user_id == current_user.id
    ).first()

    if not buyer_profile:
        # BuyerProfileが存在しない場合は未購入として扱う
        return TransactionCheckResponse(isPurchased=False)

    # 取引記録の確認
    # N+1問題を避けるためJOINを使用
    transaction = db.query(Transaction).join(
        ListingItem, Transaction.listing_id == ListingItem.id
    ).filter(
        and_(
            ListingItem.property_id == property_id,
            Transaction.buyer_id == buyer_profile.id,
            Transaction.transaction_status == TransactionStatus.COMPLETED
        )
    ).order_by(
        Transaction.created_at.desc()
    ).first()

    if not transaction:
        return TransactionCheckResponse(isPurchased=False)

    # 取引記録が存在する場合
    return TransactionCheckResponse(
        isPurchased=True,
        purchaseInfo={
            "transactionId": transaction.id,
            "purchaseDate": transaction.created_at.isoformat(),
            "amount": transaction.total_amount
        }
    )


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> CheckoutSessionResponse:
    """Stripeのチェックアウトセッションを作成する"""

    # ListingItemの取得と検証
    listing_item = db.query(ListingItem).options(
        joinedload(ListingItem.property),
        joinedload(ListingItem.seller)
    ).filter(
        ListingItem.id == request.listingId
    ).first()

    if not listing_item:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Not Found",
                "message": "Listing not found"
            }
        )

    if listing_item.status != ListingStatus.PUBLISHED:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Bad Request",
                "message": "Listing is not available"
            }
        )

    # BuyerProfileの取得または作成
    buyer_profile = await buyer_profile_service.get_or_create_buyer_profile(
        db=db,
        user=current_user,
        customer_info=request.customerInfo
    )

    # 購入済みかどうかの確認
    existing_transaction = db.query(Transaction).filter(
        and_(
            Transaction.listing_id == listing_item.id,
            Transaction.buyer_id == buyer_profile.id,
            Transaction.transaction_status == TransactionStatus.COMPLETED
        )
    ).first()

    if existing_transaction:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Bad Request",
                "message": "Already purchased"
            }
        )

    # Stripeセッションの作成
    session = await stripe_service.create_checkout_session(
        listing_item=listing_item,
        buyer_profile=buyer_profile,
        seller_profile=listing_item.seller
    )

    return CheckoutSessionResponse(
        sessionId=session["sessionId"],
        url=session["url"]
    )


@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Stripeからのwebhookを処理する"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe_service.verify_webhook_signature(
            payload,
            sig_header,
            WebhookType.PAYMENT
        )

        # イベントタイプに基づいて処理
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            await stripe_service.handle_checkout_completed(db, session)
            return {"status": "success"}
        else:
            # 他のイベントタイプは正常に受け取ったことだけを通知
            print(f"Received unhandled event type: {event['type']}")
            return {"status": "received"}

    except ValueError as e:
        print(f"Webhook error: {str(e)}")
        # Stripeに再試行させないよう200を返す
        return {"status": "error", "message": str(e)}
