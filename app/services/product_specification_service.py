
from sqlalchemy.orm import Session
from app.crud.product_specification import product_specification as product_specification_crud
from app.schemas import ProductSpecificationSchema

class ProductSpecificationService:
    def create_product_specification(self, db: Session, spec_data: ProductSpecificationSchema) -> ProductSpecificationSchema:
        """製品仕様情報を作成する"""
        return product_specification_crud.create(db, obj_in=spec_data)

    def get_product_specifications(self, db: Session, product_id: int):
        """製品に紐づく仕様情報を取得する"""
        return product_specification_crud.get_by_product(db, product_id)

product_specification_service = ProductSpecificationService()
