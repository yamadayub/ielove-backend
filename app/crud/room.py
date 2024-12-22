
from sqlalchemy.orm import Session
from app.models import Room
from app.schemas import RoomSchema
from .base import BaseCRUD
from typing import Optional, List, Literal


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

    def get_multi_by_property(
        self,
        db: Session,
        *,
        property_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Room]:
        """
        指定された物件に紐付く部屋の一覧を取得する

        Args:
            db (Session): データベースセッション
            property_id (int): 物件ID
            skip (int): スキップする件数
            limit (int): 取得する最大件数

        Returns:
            List[Room]: 部屋のリスト
        """
        return (
            db.query(Room)
            .filter(Room.property_id == property_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get(self, db: Session, id: int) -> Optional[Room]:
        """
        指定されたIDの部屋を取得する

        Args:
            db (Session): データベースセッション
            id (int): 部屋ID

        Returns:
            Optional[Room]: 部屋オブジェクト。存在しない場合はNone
        """
        return db.query(Room).filter(Room.id == id).first()


room = RoomCRUD()
