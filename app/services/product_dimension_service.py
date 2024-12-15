
from sqlalchemy.orm import Session
from app.crud.product_dimension import product_dimension as product_dimension_crud
from app.schemas import ProductDimensionSchema

class ProductDimensionService:
    def create_product_dimension(self, db: Session, dimension_data: ProductDimensionSchema) -> ProductDimensionSchema:
        """製品寸法情報を作成する"""
        return product_dimension_crud.create(db, obj_in=dimension_data)

    def get_product_dimensions(self, db: Session, product_id: int):
        """製品に紐づく寸法情報を取得する"""
        return product_dimension_crud.get_by_product(db, product_id)

product_dimension_service = ProductDimensionService()
