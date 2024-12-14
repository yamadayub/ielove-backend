from sqlalchemy.orm import Session
from app.models import ProductSpecification
from app.schemas import ProductSpecificationSchema
from .base import BaseCRUD

class ProductSpecificationCRUD(BaseCRUD[ProductSpecification, ProductSpecificationSchema, ProductSpecificationSchema]):
    def __init__(self):
        super().__init__(ProductSpecification)

    def create(self, db: Session, *, obj_in: ProductSpecificationSchema) -> ProductSpecification:
        db_obj = ProductSpecification(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ProductSpecification, obj_in: ProductSpecificationSchema) -> ProductSpecification:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> ProductSpecification:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def get_by_product(self, db: Session, product_id: int):
        return db.query(self.model).filter(self.model.product_id == product_id).all()

    def get_by_spec_type(self, db: Session, product_id: int, spec_type: str):
        return db.query(self.model)\
            .filter(self.model.product_id == product_id)\
            .filter(self.model.spec_type == spec_type)\
            .all()

product_specification = ProductSpecificationCRUD()