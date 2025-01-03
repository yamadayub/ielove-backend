from sqlalchemy.orm import Session
from typing import Optional

from app.models import BuyerProfile
from app.crud.base import CRUDBase
from app.schemas import buyer_profile_schemas


class CRUDBuyerProfile(CRUDBase[BuyerProfile, buyer_profile_schemas.BuyerProfile, buyer_profile_schemas.BuyerProfile]):
    def get_by_user_id(self, db: Session, user_id: int) -> Optional[BuyerProfile]:
        """ユーザーIDからBuyerProfileを取得する"""
        return db.query(self.model).filter(self.model.user_id == user_id).first()

    def create_with_stripe(
        self,
        db: Session,
        *,
        user_id: int,
        stripe_customer_id: str,
        shipping_postal_code: Optional[str] = None,
        shipping_prefecture: Optional[str] = None,
        shipping_city: Optional[str] = None,
        shipping_address1: Optional[str] = None,
    ) -> BuyerProfile:
        """Stripe情報付きでBuyerProfileを作成する"""
        buyer_profile = BuyerProfile(
            user_id=user_id,
            stripe_customer_id=stripe_customer_id,
            shipping_postal_code=shipping_postal_code,
            shipping_prefecture=shipping_prefecture,
            shipping_city=shipping_city,
            shipping_address1=shipping_address1,
        )
        db.add(buyer_profile)
        db.commit()
        db.refresh(buyer_profile)
        return buyer_profile


buyer_profile = CRUDBuyerProfile(BuyerProfile)
