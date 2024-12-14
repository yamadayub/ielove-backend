from sqlalchemy.orm import Session
from app.models import SellerProfile
from app.schemas import SellerProfileSchema
from .base import BaseCRUD

class SellerProfileCRUD(BaseCRUD[SellerProfile, SellerProfileSchema, SellerProfileSchema]):
    def __init__(self):
        super().__init__(SellerProfile)

    def get_by_user(self, db: Session, user_id: str):
        return db.query(self.model).filter(self.model.user_id == user_id).first()

    def get_by_stripe_account(self, db: Session, stripe_account_id: str):
        return db.query(self.model)\
            .filter(self.model.stripe_account_id == stripe_account_id)\
            .first()

    def get_active_sellers(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(self.model)\
            .filter(self.model.stripe_onboarding_completed == True)\
            .filter(self.model.stripe_charges_enabled == True)\
            .offset(skip).limit(limit).all()

seller_profile = SellerProfileCRUD()