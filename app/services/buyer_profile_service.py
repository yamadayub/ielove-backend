import stripe
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.models import User, BuyerProfile


class BuyerProfileService:
    @staticmethod
    async def get_or_create_buyer_profile(
        db: Session,
        user: User,
        customer_info: Dict[str, Any] = None
    ) -> BuyerProfile:
        # 既存のBuyerProfileを検索
        buyer_profile = db.query(BuyerProfile).filter(
            BuyerProfile.user_id == user.id
        ).first()

        if not buyer_profile:
            # Stripeカスタマー作成
            customer = stripe.Customer.create(
                email=customer_info.get('email', user.email),
                name=customer_info.get('name', user.name),
                metadata={
                    'user_id': str(user.id)
                }
            )

            # BuyerProfile作成
            buyer_profile = BuyerProfile(
                user_id=user.id,
                stripe_customer_id=customer.id,
                shipping_postal_code=None,  # customer_infoから抽出可能な場合は設定
                shipping_prefecture=None,
                shipping_city=None,
                shipping_address1=customer_info.get(
                    'address') if customer_info else None,
            )
            db.add(buyer_profile)
            db.flush()

        return buyer_profile


buyer_profile_service = BuyerProfileService()
