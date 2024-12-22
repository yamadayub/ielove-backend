from sqlalchemy.orm import Session
from app.models import Image
from app.schemas import ImageSchema
from .base import BaseCRUD
from typing import List, Optional, Literal


class ImageCRUD(BaseCRUD[Image, ImageSchema, ImageSchema]):
    def __init__(self):
        super().__init__(Image)

    def create(self, db: Session, *, obj_in: ImageSchema) -> Image:
        db_obj = Image(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Image, obj_in: ImageSchema) -> Image:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> Image:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def get_images_by_entity(
        self,
        db: Session,
        entity_type: str,
        entity_id: int
    ) -> List[Image]:
        """
        指定されたエンティティに紐づく画像一覧を取得
        """
        query = db.query(Image)

        if entity_type == "property":
            query = query.filter(Image.property_id == entity_id)
        elif entity_type == "room":
            query = query.filter(Image.room_id == entity_id)
        elif entity_type == "product":
            query = query.filter(Image.product_id == entity_id)

        return query.all()

    def get_main_images(self, db: Session):
        return db.query(self.model).filter(self.model.image_type == "main").all()


image = ImageCRUD()
