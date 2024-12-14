from sqlalchemy.orm import Session
from app.models import ProductCategory
from app.schemas import ProductCategorySchema
from .base import BaseCRUD

class ProductCategoryCRUD(BaseCRUD[ProductCategory, ProductCategorySchema, ProductCategorySchema]):
    def __init__(self):
        super().__init__(ProductCategory)

    def create(self, db: Session, *, obj_in: ProductCategorySchema) -> ProductCategory:
        db_obj = ProductCategory(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ProductCategory, obj_in: ProductCategorySchema) -> ProductCategory:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> ProductCategory:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def get_by_name(self, db: Session, name: str):
        return db.query(self.model).filter(self.model.name == name).first()

product_category = ProductCategoryCRUD()