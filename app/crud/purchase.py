from sqlalchemy.orm import Session
from app.models import Purchase
from app.schemas import PurchaseSchema
from .base import BaseCRUD

class PurchaseCRUD(BaseCRUD[Purchase, PurchaseSchema, PurchaseSchema]):
    def __init__(self):
        super().__init__(Purchase)

    def get_by_buyer(self, db: Session, buyer_id: str, skip: int = 0, limit: int = 100):
        return db.query(self.model)\
            .filter(self.model.buyer_id == buyer_id)\
            .offset(skip).limit(limit).all()

    def get_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100):
        return db.query(self.model)\
            .filter(self.model.status == status)\
            .offset(skip).limit(limit).all()

    def get_by_payment_intent(self, db: Session, payment_intent_id: str):
        return db.query(self.model)\
            .filter(self.model.stripe_payment_intent_id == payment_intent_id)\
            .first()

purchase = PurchaseCRUD()