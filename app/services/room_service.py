
from sqlalchemy.orm import Session
from app.crud.room import room as room_crud
from app.schemas import RoomSchema
from typing import Optional

class RoomService:
    def create_room(self, db: Session, room_data: RoomSchema) -> RoomSchema:
        """部屋情報を作成する"""
        return room_crud.create(db, obj_in=room_data)

    def get_room(self, db: Session, room_id: int) -> Optional[RoomSchema]:
        """部屋情報を取得する"""
        return room_crud.get(db, id=room_id)

room_service = RoomService()
