
from sqlalchemy.orm import Session
from app.models import ProductSpecification
from app.schemas import ProductSpecificationSchema

class ProductSpecificationCRUD:
    @staticmethod
    def create(db: Session, spec: ProductSpecificationSchema) -> ProductSpecification:
        db_spec = ProductSpecification(
            product_id=spec.product_id,
            spec_type=spec.spec_type,
            spec_value=spec.spec_value,
            manufacturer_id=spec.manufacturer_id,
            model_number=spec.model_number
        )
        db.add(db_spec)
        db.commit()
        db.refresh(db_spec)
        return db_spec

    @staticmethod
    def get(db: Session, spec_id: int) -> ProductSpecification:
        return db.query(ProductSpecification).filter(ProductSpecification.id == spec_id).first()

    @staticmethod
    def update(db: Session, spec_id: int, spec: ProductSpecificationSchema) -> ProductSpecification:
        db_spec = db.query(ProductSpecification).filter(ProductSpecification.id == spec_id).first()
        if db_spec:
            for key, value in spec.dict(exclude_unset=True).items():
                setattr(db_spec, key, value)
            db.commit()
            db.refresh(db_spec)
        return db_spec

    @staticmethod
    def delete(db: Session, spec_id: int) -> bool:
        db_spec = db.query(ProductSpecification).filter(ProductSpecification.id == spec_id).first()
        if db_spec:
            db.delete(db_spec)
            db.commit()
            return True
        return False
