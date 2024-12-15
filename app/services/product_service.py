
from sqlalchemy.orm import Session
from app.crud.product import product as product_crud
from app.schemas import ProductCreate
from typing import Optional

class ProductService:
    def create_product(self, db: Session, product_data: ProductCreate) -> ProductCreate:
        """製品情報を作成する"""
        return product_crud.create(db, obj_in=product_data)

    def get_product(self, db: Session, product_id: int) -> Optional[ProductCreate]:
        """製品情報を取得する"""
        return product_crud.get(db, id=product_id)

product_service = ProductService()
