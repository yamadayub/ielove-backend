
from sqlalchemy.orm import Session
from app.models import Room
from app.schemas import RoomSchema
from .base import BaseCRUD

class RoomCRUD(BaseCRUD[Room, RoomSchema, RoomSchema]):
    def __init__(self):
        super().__init__(Room)

    def get_by_property(self, db: Session, property_id: int, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(self.model.property_id == property_id)\
            .offset(skip).limit(limit).all()

room = RoomCRUD()
