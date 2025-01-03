import stripe
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.models import User, BuyerProfile
from app.crud.buyer_profile import buyer_profile


class BuyerProfileService:
    async def get_or_create_buyer_profile(
        self,
        db: Session,
        user: User,
        customer_info: Dict[str, Any] = None
    ) -> BuyerProfile:
        """BuyerProfileを取得、存在しない場合は作成する"""
        # 既存のBuyerProfileを検索
        buyer_profile_db = buyer_profile.get_by_user_id(db, user.id)

        if not buyer_profile_db:
            # Stripeカスタマー作成（current_userの情報のみを使用）
            stripe_customer = stripe.Customer.create(
                email=user.email,
                name=user.name,
                metadata={
                    'user_id': str(user.id)
                }
            )

            # BuyerProfile作成
            buyer_profile_db = buyer_profile.create_with_stripe(
                db=db,
                user_id=user.id,
                stripe_customer_id=stripe_customer.id,
                shipping_address1=None,
            )

        return buyer_profile_db


buyer_profile_service = BuyerProfileService()
