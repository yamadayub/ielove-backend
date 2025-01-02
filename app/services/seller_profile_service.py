from sqlalchemy.orm import Session
from app.crud.seller_profile import seller_profile
from app.schemas import seller_profile_schemas
from fastapi import HTTPException, status
from app.models import User
from app.services.stripe_service import stripe_service
from typing import Dict, Any


def register_seller(
    db: Session,
    seller_data: seller_profile_schemas.SellerProfileSchema,
    current_user: User
) -> seller_profile_schemas.SellerProfileSchema:
    """
    Sellerプロフィールを作成し、ユーザーのroleを更新する
    """
    # 既存のSellerプロフィールをチェック
    existing_seller = seller_profile.get_by_user_id(db, current_user.id)
    if existing_seller:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seller profile already exists"
        )

    # 入力データの準備
    seller_data_dict = seller_data.model_dump(exclude={"id"})
    seller_data_dict["user_id"] = current_user.id

    try:
        # SellerProfileの作成
        seller = seller_profile.create(
            db, obj_in=seller_profile_schemas.SellerProfileSchema(**seller_data_dict))

        # ユーザーのroleを'both'に更新
        current_user = db.query(User).get(current_user.id)
        current_user.role = "both"
        db.add(current_user)

        # 変更をコミット
        db.commit()
        db.refresh(seller)
        return seller

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


async def start_onboarding(
    db: Session,
    current_user: User
) -> seller_profile_schemas.StripeAccountLink:
    """Stripeオンボーディングを開始する"""
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


async def get_onboarding_status(
    db: Session,
    current_user: User
) -> seller_profile_schemas.SellerProfileSchema:
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


async def handle_stripe_webhook(
    db: Session,
    event: Dict[str, Any]
) -> None:
    """Stripeのwebhookイベントを処理する"""
    if event["type"] == "account.updated":
        account = event["data"]["object"]
        seller = seller_profile.get_by_stripe_account_id(
            db, account["id"])

        if seller:
            seller_profile.update(
                db,
                db_obj=seller,
                obj_in={
                    "stripe_onboarding_completed": account["details_submitted"],
                    "stripe_charges_enabled": account["charges_enabled"],
                    "stripe_payouts_enabled": account["payouts_enabled"],
                    "stripe_account_status": "active" if account["details_submitted"] else "pending",
                    "stripe_capabilities": account["capabilities"]
                }
            )
