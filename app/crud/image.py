
from sqlalchemy.orm import Session
from app.models import Image
from app.schemas import ImageSchema
from .base import BaseCRUD

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

    def get_by_property(self, db: Session, property_id: int):
        return db.query(self.model).filter(self.model.property_id == property_id).all()

    def get_by_room(self, db: Session, room_id: int):
        return db.query(self.model).filter(self.model.room_id == room_id).all()

    def get_by_product(self, db: Session, product_id: int):
        return db.query(self.model).filter(self.model.product_id == product_id).all()

    def get_main_images(self, db: Session):
        return db.query(self.model).filter(self.model.image_type == "main").all()

image = ImageCRUD()
