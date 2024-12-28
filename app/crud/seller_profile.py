from sqlalchemy.orm import Session
from app.models import SellerProfile
from app.schemas import seller_profile_schemas
from app.crud.base import CRUDBase
from typing import Optional, List


class CRUDSellerProfile(CRUDBase[SellerProfile, seller_profile_schemas.SellerProfileSchema, seller_profile_schemas.SellerProfileSchema]):
    def get_by_user_id(self, db: Session, user_id: int) -> Optional[SellerProfile]:
        """ユーザーIDからSellerプロフィールを取得する"""
        return db.query(self.model).filter(self.model.user_id == user_id).first()

    def get_by_stripe_account_id(self, db: Session, stripe_account_id: str) -> Optional[SellerProfile]:
        """Stripe Account IDからSellerプロフィールを取得する"""
        return db.query(self.model).filter(self.model.stripe_account_id == stripe_account_id).first()

    def get_active_sellers(self, db: Session) -> List[SellerProfile]:
        """アクティブなSeller一覧を取得する"""
        return db.query(self.model).filter(
            self.model.stripe_onboarding_completed == True,
            self.model.stripe_charges_enabled == True
        ).all()


seller_profile = CRUDSellerProfile(SellerProfile)
