from sqlalchemy.orm import Session
from app.models import SellerProfile
from app.schemas import SellerProfileSchema
from .base import BaseCRUD

class SellerProfileCRUD(BaseCRUD[SellerProfile, SellerProfileSchema, SellerProfileSchema]):
    def __init__(self):
        super().__init__(SellerProfile)

    def create(self, db: Session, *, obj_in: SellerProfileSchema) -> SellerProfile:
        db_obj = SellerProfile(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: SellerProfile, obj_in: SellerProfileSchema) -> SellerProfile:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> SellerProfile:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

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