from sqlalchemy.orm import Session
from app.crud.room import room as room_crud
from app.schemas import RoomSchema
from typing import Optional, List, Literal
from fastapi import HTTPException
from app.models import Room
from sqlalchemy.orm import joinedload
from app.crud.product import product as product_crud
from app.crud.image import image as image_crud
from app.models import Product


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

    def get_room_details(self, db: Session, room_id: int):
        """部屋の詳細情報を関連データと共に取得"""

        # 部屋情報を関連データと共に取得
        room = db.query(Room)\
            .options(
                joinedload(Room.products)
                .joinedload(Product.specifications),
                joinedload(Room.products)
                .joinedload(Product.dimensions),
                joinedload(Room.property)  # 物件情報も取得
        )\
            .filter(Room.id == room_id)\
            .first()

        if not room:
            raise HTTPException(status_code=404, detail="Room not found")

        # 部屋の画像を取得
        room_images = image_crud.get_images(db, room_id=room_id)

        # レスポンスの構築
        result = {
            "id": room.id,
            "name": room.name,
            "description": room.description,
            "property_id": room.property_id,
            "created_at": room.created_at,
            "images": room_images,
            "products": [],
            # 物件の基本情報
            "property_name": room.property.name,
            "property_type": room.property.property_type,
            "prefecture": room.property.prefecture
        }

        for product in room.products:
            # 製品の画像を取得
            product_images = image_crud.get_images(db, product_id=product.id)

            product_data = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "room_id": product.room_id,
                "product_category_id": product.product_category_id,
                "manufacturer_id": product.manufacturer_id,
                "product_code": product.product_code,
                "catalog_url": product.catalog_url,
                "created_at": product.created_at,
                "images": product_images,
                "specifications": product.specifications,
                "dimensions": product.dimensions
            }
            result["products"].append(product_data)

        return result


room_service = RoomService()
