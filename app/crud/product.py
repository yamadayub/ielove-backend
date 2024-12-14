
from sqlalchemy.orm import Session
from app.models import Product
from app.schemas import ProductSchema
from .base import BaseCRUD

class ProductCRUD(BaseCRUD[Product, ProductSchema, ProductSchema]):
    def __init__(self):
        super().__init__(Product)

    def create(self, db: Session, *, obj_in: ProductSchema) -> Product:
        db_obj = Product(
            property_id=obj_in.property_id,
            room_id=obj_in.room_id,
            product_category_id=obj_in.product_category_id,
            manufacturer_id=obj_in.manufacturer_id,
            name=obj_in.name,
            product_code=obj_in.product_code,
            description=obj_in.description,
            catalog_url=obj_in.catalog_url
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Product, obj_in: ProductSchema) -> Product:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> Product:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def get_by_category(self, db: Session, category_id: int, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(self.model.product_category_id == category_id)\
            .offset(skip).limit(limit).all()

    def get_by_manufacturer(self, db: Session, manufacturer_id: int, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(self.model.manufacturer_id == manufacturer_id)\
            .offset(skip).limit(limit).all()

    def get_by_room(self, db: Session, room_id: int, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(self.model.room_id == room_id)\
            .offset(skip).limit(limit).all()

product = ProductCRUD()
