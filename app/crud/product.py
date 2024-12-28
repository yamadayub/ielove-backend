from sqlalchemy.orm import Session, joinedload
from app.models import Product
from app.schemas import ProductSchema
from .base import CRUDBase
from typing import Optional


class ProductCRUD(CRUDBase[Product, ProductSchema, ProductSchema]):
    def __init__(self):
        super().__init__(Product)

    def create(self, db: Session, *, obj_in: ProductSchema) -> Product:
        db_obj = Product(
            room_id=obj_in.room_id,
            product_category_id=obj_in.product_category_id,
            manufacturer_id=obj_in.manufacturer_id,
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

    def get_by_manufacturer(self, db: Session, manufacturer_id: int, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(self.model.manufacturer_id == manufacturer_id)\
            .offset(skip).limit(limit).all()

    def get_products_by_room(self, db: Session, room_id: int, skip: int = 0, limit: int = 100):
        """
        指定された部屋IDに紐づく製品一覧を取得
        product_categoryとmanufacturerの情報も含める
        """
        products = db.query(Product)\
            .options(
                joinedload(Product.product_category),
                joinedload(Product.manufacturer)
        )\
            .filter(Product.room_id == room_id)\
            .offset(skip)\
            .limit(limit)\
            .all()

        # 明示的にproduct_category_nameとmanufacturer_nameを設定
        for product in products:
            if product.product_category:
                product.product_category_name = product.product_category.name
            if product.manufacturer:
                product.manufacturer_name = product.manufacturer.name

        return products

    def get_product_with_details(self, db: Session, product_id: int):
        """
        製品の詳細情報（仕様・寸法を含む）を取得
        """
        product = db.query(Product)\
            .options(
                joinedload(Product.specifications),
                joinedload(Product.dimensions),
                joinedload(Product.product_category),
                joinedload(Product.manufacturer)
        )\
            .filter(Product.id == product_id)\
            .first()

        # 明示的に関連名を設定
        if product:
            if product.product_category:
                product.product_category_name = product.product_category.name
            if product.manufacturer:
                product.manufacturer_name = product.manufacturer.name

        return product

    def get(self, db: Session, id: int) -> Optional[Product]:
        """
        指定されたIDの製品を取得（カテゴリ、メーカー、仕様、寸法情報を含む）
        """
        product = db.query(Product)\
            .options(
                joinedload(Product.product_category),
                joinedload(Product.manufacturer),
                joinedload(Product.specifications),
                joinedload(Product.dimensions)
        )\
            .filter(Product.id == id)\
            .first()

        # デバッグ用：取得したデータの確認
        if product:
            print(f"Product ID: {product.id}")
            print(f"Product Category: {product.product_category}")
            print(
                f"Product Category Name: {product.product_category.name if product.product_category else None}")
            print(f"Manufacturer: {product.manufacturer}")
            print(
                f"Manufacturer Name: {product.manufacturer.name if product.manufacturer else None}")
            print(f"Specifications Count: {len(product.specifications)}")
            print(f"Dimensions Count: {len(product.dimensions)}")

        # 明示的に関連名を設定
        if product:
            if product.product_category:
                product.product_category_name = product.product_category.name
            if product.manufacturer:
                product.manufacturer_name = product.manufacturer.name

        return product


product = ProductCRUD()
