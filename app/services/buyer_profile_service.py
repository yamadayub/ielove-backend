import stripe
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime

from app.models import User, BuyerProfile
from app.crud.buyer_profile import buyer_profile


class BuyerProfileService:
    async def get_or_create_buyer_profile(
        self,
        db: Session,
        user: User
    ) -> BuyerProfile:
        """BuyerProfileを取得または作成する"""
        buyer_profile = db.query(BuyerProfile).filter(
            BuyerProfile.user_id == user.id
        ).first()

        if not buyer_profile:
            # Stripeの顧客を作成
            customer = stripe.Customer.create(
                email=user.email,
                name=user.name,
                metadata={
                    'user_id': str(user.id)
                }
            )

            # BuyerProfileを作成
            buyer_profile = BuyerProfile(
                user_id=user.id,
                stripe_customer_id=customer.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(buyer_profile)
            db.commit()
            db.refresh(buyer_profile)

        return buyer_profile


buyer_profile_service = BuyerProfileService()
