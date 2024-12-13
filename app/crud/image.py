
from sqlalchemy.orm import Session
from app.models import Image
from app.schemas import ImageSchema

class ImageCRUD:
    @staticmethod
    def create(db: Session, image: ImageSchema) -> Image:
        db_image = Image(
            url=image.url,
            description=image.description,
            image_type=image.image_type,
            property_id=image.property_id,
            room_id=image.room_id,
            product_id=image.product_id
        )
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        return db_image

    @staticmethod
    def get(db: Session, image_id: int) -> Image:
        return db.query(Image).filter(Image.id == image_id).first()

    @staticmethod
    def update(db: Session, image_id: int, image: ImageSchema) -> Image:
        db_image = db.query(Image).filter(Image.id == image_id).first()
        if db_image:
            for key, value in image.dict(exclude_unset=True).items():
                setattr(db_image, key, value)
            db.commit()
            db.refresh(db_image)
        return db_image

    @staticmethod
    def delete(db: Session, image_id: int) -> bool:
        db_image = db.query(Image).filter(Image.id == image_id).first()
        if db_image:
            db.delete(db_image)
            db.commit()
            return True
        return False
