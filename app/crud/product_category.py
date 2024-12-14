from sqlalchemy.orm import Session
from app.models import ProductCategory
from app.schemas import ProductCategorySchema
from .base import BaseCRUD

class ProductCategoryCRUD(BaseCRUD[ProductCategory, ProductCategorySchema, ProductCategorySchema]):
    def __init__(self):
        super().__init__(ProductCategory)

    def get_by_name(self, db: Session, name: str):
        return db.query(self.model).filter(self.model.name == name).first()

product_category = ProductCategoryCRUD()