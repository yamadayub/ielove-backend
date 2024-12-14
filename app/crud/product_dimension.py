from sqlalchemy.orm import Session
from app.models import ProductDimension
from app.schemas import ProductDimensionSchema
from .base import BaseCRUD

class ProductDimensionCRUD(BaseCRUD[ProductDimension, ProductDimensionSchema, ProductDimensionSchema]):
    def __init__(self):
        super().__init__(ProductDimension)

    def create(self, db: Session, *, obj_in: ProductDimensionSchema) -> ProductDimension:
        db_obj = ProductDimension(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ProductDimension, obj_in: ProductDimensionSchema) -> ProductDimension:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> ProductDimension:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def get_by_product(self, db: Session, product_id: int):
        return db.query(self.model).filter(self.model.product_id == product_id).all()

    def get_by_dimension_type(self, db: Session, product_id: int, dimension_type: str):
        return db.query(self.model)\
            .filter(self.model.product_id == product_id)\
            .filter(self.model.dimension_type == dimension_type)\
            .first()

product_dimension = ProductDimensionCRUD()