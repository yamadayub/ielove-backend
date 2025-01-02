from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.stripe_service import stripe_service
from app.services.seller_profile_service import register_seller
from app.crud.seller_profile import seller_profile
from app.schemas import seller_profile_schemas
from app.auth.dependencies import get_current_user
from app.schemas.user_schemas import UserSchema
from typing import Dict, Any
from app.config import get_settings
from app.services.stripe_service import WebhookType

router = APIRouter(tags=["sellers"])

settings = get_settings()


@router.post("/sellers/register", response_model=seller_profile_schemas.SellerProfileSchema)
async def create_seller_profile(
    seller_data: seller_profile_schemas.SellerProfileSchema,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """Sellerプロフィールを作成し、ユーザーのroleを更新する"""
    return register_seller(db, seller_data, current_user)


@router.post("/sellers/onboarding/start", response_model=seller_profile_schemas.StripeAccountLink)
async def start_onboarding(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """Stripeオンボーディングを開始する"""
    # Sellerプロフィールの取得
    seller = seller_profile.get_by_user_id(db, current_user.id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller profile not found")

    # Stripeアカウントが未作成の場合は作成
    if not seller.stripe_account_id:
        business_profile = {
            "name": seller.company_name or current_user.name,
            "support_email": current_user.email,
        }
        account = await stripe_service.create_connect_account(
            current_user.email,
            business_profile
        )
        seller = seller_profile.update(
            db,
            db_obj=seller,
            obj_in={
                "stripe_account_id": account["id"],
                "stripe_account_type": "standard",
                "stripe_account_status": "pending"
            }
        )

    # オンボーディングリンクの生成
    account_link = await stripe_service.create_account_link(
        seller.stripe_account_id
    )
    return seller_profile_schemas.StripeAccountLink(
        url=account_link["url"],
        expires_at=account_link["expires_at"]
    )


@router.get("/sellers/onboarding/status", response_model=seller_profile_schemas.SellerProfileSchema)
async def get_onboarding_status(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """オンボーディング状態を取得する"""
    seller = seller_profile.get_by_user_id(db, current_user.id)
    if not seller or not seller.stripe_account_id:
        raise HTTPException(status_code=404, detail="Stripe account not found")

    status = await stripe_service.get_account_status(seller.stripe_account_id)

    # ステータスの更新
    seller = seller_profile.update(
        db,
        db_obj=seller,
        obj_in={
            "stripe_onboarding_completed": status["details_submitted"],
            "stripe_charges_enabled": status["charges_enabled"],
            "stripe_payouts_enabled": status["payouts_enabled"],
            "stripe_account_status": "active" if status["details_submitted"] else "pending",
            "stripe_capabilities": status["capabilities"]
        }
    )

    return seller


@router.post("/sellers/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Stripe Connectからのwebhookを処理する"""
    # リクエストの詳細をログ出力
    print("\n=== Webhook Request Details ===")
    print(f"[DEBUG] Method: {request.method}")
    print(f"[DEBUG] URL: {request.url}")
    print(f"[DEBUG] Headers:")
    for name, value in request.headers.items():
        print(f"  {name}: {value}")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    print("\n=== Webhook Payload Details ===")
    print(f"[DEBUG] Payload Type: {type(payload)}")
    print(f"[DEBUG] Payload Length: {len(payload)}")
    print(f"[DEBUG] Payload Content (first 200 chars):")
    try:
        print(payload.decode('utf-8')[:200])
    except Exception as e:
        print(f"[ERROR] Failed to decode payload: {e}")

    try:
        event = stripe_service.verify_webhook_signature(
            payload,
            sig_header,
            WebhookType.CONNECT
        )
        await seller_profile_service.handle_stripe_webhook(db, event)
        return {"status": "success"}
    except ValueError as e:
        print(f"[ERROR] Webhook Processing Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sellers/reset-stripe", response_model=seller_profile_schemas.SellerProfileSchema)
async def reset_stripe_account(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """Stripe情報をリセットする"""
    seller = seller_profile.get_by_user_id(db, current_user.id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller profile not found")

    # Stripe情報をリセット
    seller = seller_profile.update(
        db,
        db_obj=seller,
        obj_in={
            "stripe_account_id": None,
            "stripe_account_type": None,
            "stripe_account_status": None,
            "stripe_onboarding_completed": False,
            "stripe_charges_enabled": False,
            "stripe_payouts_enabled": False,
            "stripe_capabilities": None
        }
    )

    return seller


@router.get("/sellers/stripe-dashboard", response_model=seller_profile_schemas.StripeDashboardLink)
async def get_stripe_dashboard_link(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """Stripeダッシュボードへのリンクを取得する"""
    try:
        seller = seller_profile.get_by_user_id(db, current_user.id)
        if not seller or not seller.stripe_account_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stripe account not found"
            )

        # テストモードかどうかでURLを変更
        base_url = "https://dashboard.stripe.com"
        if settings.STRIPE_SECRET_KEY.startswith("sk_test"):
            base_url = "https://dashboard.stripe.com/test"

        dashboard_url = f"{base_url}/connect/accounts/{seller.stripe_account_id}"
        return seller_profile_schemas.StripeDashboardLink(url=dashboard_url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
