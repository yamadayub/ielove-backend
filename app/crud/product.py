
from sqlalchemy.orm import Session
from app.models import Product
from app.schemas import ProductSchema

class ProductCRUD:
    @staticmethod
    def create(db: Session, product: ProductSchema) -> Product:
        db_product = Product(
            property_id=product.property_id,
            room_id=product.room_id,
            product_category_id=product.product_category_id,
            manufacturer_id=product.manufacturer_id,
            name=product.name,
            product_code=product.product_code,
            description=product.description,
            catalog_url=product.catalog_url
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product

    @staticmethod
    def get(db: Session, product_id: int) -> Product:
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def update(db: Session, product_id: int, product: ProductSchema) -> Product:
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if db_product:
            for key, value in product.dict(exclude_unset=True).items():
                setattr(db_product, key, value)
            db.commit()
            db.refresh(db_product)
        return db_product

    @staticmethod
    def delete(db: Session, product_id: int) -> bool:
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if db_product:
            db.delete(db_product)
            db.commit()
            return True
        return False
