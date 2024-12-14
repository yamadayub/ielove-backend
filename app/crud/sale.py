from sqlalchemy.orm import Session
from app.models import Sale
from app.schemas import SaleSchema
from .base import BaseCRUD

class SaleCRUD(BaseCRUD[Sale, SaleSchema, SaleSchema]):
    def __init__(self):
        super().__init__(Sale)

    def create(self, db: Session, *, obj_in: SaleSchema) -> Sale:
        db_obj = Sale(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Sale, obj_in: SaleSchema) -> Sale:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> Sale:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def get_by_seller(self, db: Session, seller_id: int, skip: int = 0, limit: int = 100):
        return db.query(self.model)\
            .filter(self.model.seller_id == seller_id)\
            .offset(skip).limit(limit).all()

    def get_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100):
        return db.query(self.model)\
            .filter(self.model.status == status)\
            .offset(skip).limit(limit).all()

    def get_by_transfer(self, db: Session, transfer_id: str):
        return db.query(self.model)\
            .filter(self.model.stripe_transfer_id == transfer_id)\
            .first()

sale = SaleCRUD()