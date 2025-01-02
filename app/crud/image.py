from sqlalchemy.orm import Session
from app.models import Image, Room, Product
from app.schemas import ImageSchema
from .base import BaseCRUD
from typing import List, Optional
from fastapi import HTTPException


class ImageCRUD(BaseCRUD[Image, ImageSchema, ImageSchema]):
    def __init__(self):
        super().__init__(Image)

    def delete(self, db: Session, *, id: int) -> bool:
        obj = db.query(self.model).get(id)
        if not obj:
            return False
        db.delete(obj)
        db.commit()
        return True

    def create(self, db: Session, *, obj_in: ImageSchema) -> Image:
        # 関連性のバリデーション
        if obj_in.product_id:
            # 製品が指定されている場合、部屋と物件も必須
            product = db.query(Product).get(obj_in.product_id)
            if not product:
                raise HTTPException(
                    status_code=404, detail="Product not found")
            obj_in.room_id = product.room_id
            room = db.query(Room).get(product.room_id)
            obj_in.property_id = room.property_id
        elif obj_in.room_id:
            # 部屋が指定されている場合、物件も必須
            room = db.query(Room).get(obj_in.room_id)
            if not room:
                raise HTTPException(status_code=404, detail="Room not found")
            obj_in.property_id = room.property_id

        db_obj = Image(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_images(
        self,
        db: Session,
        *,
        property_id: Optional[int] = None,
        room_id: Optional[int] = None,
        product_id: Optional[int] = None
    ) -> List[Image]:
        """
        指定された条件に基づいて画像を検索します。
        優先順位: property_id > room_id > product_id
        ステータスがcompletedの画像のみを返します。
        """
        try:
            query = db.query(Image).filter(Image.status == "completed")

            if property_id:
                return query.filter(Image.property_id == property_id).all()
            elif room_id:
                return query.filter(Image.room_id == room_id).all()
            elif product_id:
                return query.filter(Image.product_id == product_id).all()

            return query.all()  # 条件が指定されていない場合は、全てのcompletedな画像を返す
        except Exception as e:
            # エラーが発生した場合は空のリストを返す
            return []


image = ImageCRUD()
