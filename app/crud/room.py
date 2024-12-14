
from sqlalchemy.orm import Session
from app.models import Room
from app.schemas import RoomSchema
from .base import BaseCRUD

class RoomCRUD(BaseCRUD[Room, RoomSchema, RoomSchema]):
    def __init__(self):
        super().__init__(Room)

    def create(self, db: Session, *, obj_in: RoomSchema) -> Room:
        db_obj = Room(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Room, obj_in: RoomSchema) -> Room:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> Room:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def get_by_property(self, db: Session, property_id: int, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(self.model.property_id == property_id)\
            .offset(skip).limit(limit).all()

room = RoomCRUD()
