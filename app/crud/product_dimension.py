from sqlalchemy.orm import Session
from app.models import ProductDimension
from app.schemas import ProductDimensionSchema
from .base import BaseCRUD

class ProductDimensionCRUD(BaseCRUD[ProductDimension, ProductDimensionSchema, ProductDimensionSchema]):
    def __init__(self):
        super().__init__(ProductDimension)

    def get_by_product(self, db: Session, product_id: int):
        return db.query(self.model).filter(self.model.product_id == product_id).all()

    def get_by_dimension_type(self, db: Session, product_id: int, dimension_type: str):
        return db.query(self.model)\
            .filter(self.model.product_id == product_id)\
            .filter(self.model.dimension_type == dimension_type)\
            .first()

product_dimension = ProductDimensionCRUD()