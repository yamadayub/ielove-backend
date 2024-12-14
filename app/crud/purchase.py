from sqlalchemy.orm import Session
from app.models import Purchase
from app.schemas import PurchaseSchema
from .base import BaseCRUD

class PurchaseCRUD(BaseCRUD[Purchase, PurchaseSchema, PurchaseSchema]):
    def __init__(self):
        super().__init__(Purchase)

    def create(self, db: Session, *, obj_in: PurchaseSchema) -> Purchase:
        db_obj = Purchase(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Purchase, obj_in: PurchaseSchema) -> Purchase:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> Purchase:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

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