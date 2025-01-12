from sqlalchemy.orm import Session
from app.models import Image, Room, Product, ProductSpecification
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
