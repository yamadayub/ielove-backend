
from sqlalchemy.orm import Session
from app.models import Property
from app.schemas import PropertySchema
from .base import BaseCRUD

class PropertyCRUD(BaseCRUD[Property, PropertySchema, PropertySchema]):
    def __init__(self):
        super().__init__(Property)

    def get_by_user(self, db: Session, user_id: str, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(self.model.user_id == user_id)\
            .offset(skip).limit(limit).all()

    def get_by_prefecture(self, db: Session, prefecture: str, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(self.model.prefecture == prefecture)\
            .offset(skip).limit(limit).all()

property = PropertyCRUD()
