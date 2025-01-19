from sqlalchemy.orm import Session, joinedload
from app.models import Product
from app.schemas import ProductSchema
from .base import CRUDBase
from typing import Optional, List


class ProductCRUD(CRUDBase[Product, ProductSchema, ProductSchema]):
    def __init__(self):
        super().__init__(Product)

    def create(self, db: Session, *, obj_in: ProductSchema) -> Product:
        db_obj = Product(
            room_id=obj_in.room_id,
            product_category_id=obj_in.product_category_id,
            manufacturer_name=obj_in.manufacturer_name,
            name=obj_in.name,
            product_code=obj_in.product_code,
            description=obj_in.description,
            catalog_url=obj_in.catalog_url
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Product, obj_in: ProductSchema) -> Product:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> Product:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def get_by_category(self, db: Session, category_id: int, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(self.model.product_category_id == category_id)\
            .offset(skip).limit(limit).all()

    def get_products_by_room(
        self,
        db: Session,
        *,
        room_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """指定された部屋IDに紐づく製品一覧を取得"""
        return db.query(self.model)\
            .filter(self.model.room_id == room_id, self.model.is_deleted == False)\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get_product_with_details(self, db: Session, product_id: int):
        """
        製品の詳細情報（仕様・寸法を含む）を取得
        """
        product = db.query(Product)\
            .options(
                joinedload(Product.specifications),
                joinedload(Product.dimensions),
                joinedload(Product.product_category)
        )\
            .filter(Product.id == product_id)\
            .first()

        # 明示的に関連名を設定
        if product and product.product_category:
            product.product_category_name = product.product_category.name

        return product

    def get(self, db: Session, id: int) -> Optional[Product]:
        """指定されたIDの製品を取得"""
        return db.query(self.model)\
            .filter(self.model.id == id, self.model.is_deleted == False)\
            .first()


product = ProductCRUD()
