
from sqlalchemy.orm import Session
from app.models import ProductDimension
from app.schemas import ProductDimensionSchema

class ProductDimensionCRUD:
    @staticmethod
    def create(db: Session, dimension: ProductDimensionSchema) -> ProductDimension:
        db_dimension = ProductDimension(
            product_id=dimension.product_id,
            dimension_type=dimension.dimension_type,
            value=dimension.value,
            unit=dimension.unit
        )
        db.add(db_dimension)
        db.commit()
        db.refresh(db_dimension)
        return db_dimension

    @staticmethod
    def get(db: Session, dimension_id: int) -> ProductDimension:
        return db.query(ProductDimension).filter(ProductDimension.id == dimension_id).first()

    @staticmethod
    def update(db: Session, dimension_id: int, dimension: ProductDimensionSchema) -> ProductDimension:
        db_dimension = db.query(ProductDimension).filter(ProductDimension.id == dimension_id).first()
        if db_dimension:
            for key, value in dimension.dict(exclude_unset=True).items():
                setattr(db_dimension, key, value)
            db.commit()
            db.refresh(db_dimension)
        return db_dimension

    @staticmethod
    def delete(db: Session, dimension_id: int) -> bool:
        db_dimension = db.query(ProductDimension).filter(ProductDimension.id == dimension_id).first()
        if db_dimension:
            db.delete(db_dimension)
            db.commit()
            return True
        return False
