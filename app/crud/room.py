from sqlalchemy.orm import Session
from app.models import Room
from app.schemas import RoomSchema
from .base import BaseCRUD
from typing import Optional, List, Literal


class RoomCRUD(BaseCRUD[Room, RoomSchema, RoomSchema]):
    def __init__(self):
        super().__init__(Room)

    def create(self, db: Session, *, obj_in: RoomSchema) -> Room:
        obj_dict = obj_in.model_dump()
        db_obj = Room(**obj_dict)
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

    def get_multi_by_property(
        self,
        db: Session,
        *,
        property_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Room]:
        """指定された物件IDに紐づく部屋一覧を取得"""
        return db.query(self.model)\
            .filter(self.model.property_id == property_id, self.model.is_deleted == False)\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get(self, db: Session, id: int) -> Optional[Room]:
        """指定されたIDの部屋を取得"""
        return db.query(self.model)\
            .filter(self.model.id == id, self.model.is_deleted == False)\
            .first()


room = RoomCRUD()
