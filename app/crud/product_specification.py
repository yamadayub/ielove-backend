from sqlalchemy.orm import Session
from app.models import ProductSpecification
from app.schemas import ProductSpecificationSchema
from .base import BaseCRUD

class ProductSpecificationCRUD(BaseCRUD[ProductSpecification, ProductSpecificationSchema, ProductSpecificationSchema]):
    def __init__(self):
        super().__init__(ProductSpecification)

    def get_by_product(self, db: Session, product_id: int):
        return db.query(self.model).filter(self.model.product_id == product_id).all()

    def get_by_spec_type(self, db: Session, product_id: int, spec_type: str):
        return db.query(self.model)\
            .filter(self.model.product_id == product_id)\
            .filter(self.model.spec_type == spec_type)\
            .all()

product_specification = ProductSpecificationCRUD()