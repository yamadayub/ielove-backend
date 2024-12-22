from sqlalchemy.orm import Session
from app.crud.room import room as room_crud
from app.schemas import RoomSchema
from typing import Optional, List, Literal
from fastapi import HTTPException
from app.models import Room


class RoomService:
    def create_room(self, db: Session, room_data: RoomSchema) -> RoomSchema:
        """部屋情報を作成する"""
        return room_crud.create(db, obj_in=room_data)

    def get_rooms(
        self,
        db: Session,
        property_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[RoomSchema]:
        """
        指定された物件の部屋一覧を取得する

        Args:
            db (Session): データベースセッション
            property_id (int): 物件ID
            skip (int): スキップする件数
            limit (int): 取得する最大件数

        Returns:
            List[RoomSchema]: 部屋のリスト
        """
        return room_crud.get_multi_by_property(
            db,
            property_id=property_id,
            skip=skip,
            limit=limit
        )

    def get_room(self, db: Session, room_id: int) -> Optional[RoomSchema]:
        """
        指定されたIDの部屋を取得する

        Args:
            db (Session): データベースセッション
            room_id (int): 部屋ID

        Returns:
            Optional[RoomSchema]: 部屋オブジェクト。存在しない場合はNone
        """
        return room_crud.get(db, id=room_id)

    async def update_room(self, db: Session, room_id: int, room_data: RoomSchema):
        db_room = db.query(Room).filter(Room.id == room_id).first()

        if not db_room:
            raise HTTPException(status_code=404, detail="Room not found")

        for field, value in room_data.model_dump(exclude_unset=True).items():
            setattr(db_room, field, value)

        try:
            db.commit()
            db.refresh(db_room)
            return db_room
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_room(self, db: Session, room_id: int):
        db_room = db.query(Room).filter(Room.id == room_id).first()

        if not db_room:
            raise HTTPException(status_code=404, detail="Room not found")

        try:
            db.delete(db_room)
            db.commit()
            return {"message": "Room deleted successfully"}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))


room_service = RoomService()
