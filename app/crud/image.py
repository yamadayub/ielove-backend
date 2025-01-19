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
        product_id: Optional[int] = None,
        product_specification_id: Optional[int] = None,
        drawing_id: Optional[int] = None
    ) -> List[Image]:
        """
        指定された条件に基づいて画像を検索します。
        drawing_idが指定された場合は、他のパラメータに関係なく図面の画像のみを返します。
        property_idが指定された場合は、そのプロパティに紐づく全ての画像（drawingの画像含む）を返します。
        それ以外の場合は以下の優先順位で処理します：
        room_id > product_id > product_specification_id
        ステータスがcompletedの画像のみを返します。
        """
        try:
            query = db.query(Image).filter(Image.status == "completed")

            if drawing_id is not None:
                return query.filter(Image.drawing_id == drawing_id).all()
            elif property_id:
                return query.filter(Image.property_id == property_id).all()
            elif room_id:
                return query.filter(Image.room_id == room_id).all()
            elif product_id:
                return query.filter(Image.product_id == product_id).all()
            elif product_specification_id:
                return query.filter(Image.product_specification_id == product_specification_id).all()

            # 条件が指定されていない場合は、drawing以外の全てのcompletedな画像を返す
            return query.filter(Image.drawing_id.is_(None)).all()
        except Exception as e:
            # エラーが発生した場合は空のリストを返す
            return []


image = ImageCRUD()
