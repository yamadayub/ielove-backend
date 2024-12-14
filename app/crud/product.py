
from sqlalchemy.orm import Session
from app.models import Product
from app.schemas import ProductSchema
from .base import BaseCRUD

class ProductCRUD(BaseCRUD[Product, ProductSchema, ProductSchema]):
    def __init__(self):
        super().__init__(Product)

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
