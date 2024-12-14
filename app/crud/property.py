
from sqlalchemy.orm import Session
from app.models import Property
from app.schemas import PropertySchema
from .base import BaseCRUD

class PropertyCRUD(BaseCRUD[Property, PropertySchema, PropertySchema]):
    def __init__(self):
        super().__init__(Property)

    def create(self, db: Session, *, obj_in: PropertySchema) -> Property:
        db_obj = Property(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Property, obj_in: PropertySchema) -> Property:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> Property:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def get_by_user(self, db: Session, user_id: str, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(self.model.user_id == user_id)\
            .offset(skip).limit(limit).all()

    def get_by_prefecture(self, db: Session, prefecture: str, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(self.model.prefecture == prefecture)\
            .offset(skip).limit(limit).all()

property = PropertyCRUD()
