from sqlalchemy.orm import Session
from app.crud.product import product as product_crud
from app.schemas import ProductSchema
from typing import Optional
from fastapi import HTTPException
from app.models import Product, Room, Property, ProductSpecification, ProductDimension
from typing import List
from app.schemas import ProductSpecificationSchema, ProductDimensionSchema
from sqlalchemy.orm import joinedload
from app.crud.image import image as image_crud


class ProductService:
    def create_product(self, db: Session, product_data: ProductSchema) -> ProductSchema:
        """製品情報を作成する"""
        return product_crud.create(db, obj_in=product_data)

    def get_product(self, db: Session, product_id: int) -> Optional[ProductSchema]:
        """製品情報を取得する"""
        return product_crud.get(db, id=product_id)

    def get_products_by_room(self, db: Session, room_id: int, skip: int = 0, limit: int = 100):
        """
        指定された部屋IDに紐づく製品一覧を取得
        """
        return product_crud.get_products_by_room(db, room_id=room_id, skip=skip, limit=limit)

    def get_product_details(self, db: Session, product_id: int):
        """製品の詳細情報を関連データと共に取得"""

        # 製品情報を関連データと共に取得
        product = db.query(Product)\
            .options(
                joinedload(Product.specifications),
                joinedload(Product.dimensions),
                joinedload(Product.room).joinedload(Room.property),
                joinedload(Product.product_category)
        )\
            .filter(Product.id == product_id)\
            .first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # 製品の画像を取得
        product_images = image_crud.get_images(db, product_id=product_id)

        # レスポンスの構築
        result = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "room_id": product.room_id,
            "product_category_id": product.product_category_id,
            "product_category_name": product.product_category.name if product.product_category else None,
            "manufacturer_name": product.manufacturer_name,
            "product_code": product.product_code,
            "catalog_url": product.catalog_url,
            "created_at": product.created_at,
            "specifications": product.specifications,
            "dimensions": product.dimensions,
            "images": product_images,
            # 部屋と物件の基本情報
            "room_name": product.room.name,
            "property_id": product.room.property_id,
            "property_name": product.room.property.name,
            "property_type": product.room.property.property_type,
            "prefecture": product.room.property.prefecture
        }

        return result

    async def update_product(self, db: Session, product_id: int, product_data: ProductSchema):
        db_product = db.query(Product).filter(Product.id == product_id).first()

        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        for field, value in product_data.model_dump(exclude_unset=True).items():
            setattr(db_product, field, value)

        try:
            db.commit()
            db.refresh(db_product)
            return db_product
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_product(self, db: Session, product_id: int):
        db_product = db.query(Product).filter(Product.id == product_id).first()

        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        try:
            db.delete(db_product)
            db.commit()
            return {"message": "Product deleted successfully"}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def update_product_specifications(
        self,
        db: Session,
        product_id: int,
        specifications: List[ProductSpecificationSchema]
    ):
        # 製品の存在確認
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        try:
            # 既存の仕様を全て削除
            db.query(ProductSpecification).filter(
                ProductSpecification.product_id == product_id
            ).delete()

            # 新しい仕様を追加
            new_specs = []
            for spec in specifications:
                db_spec = ProductSpecification(
                    product_id=product_id,
                    spec_type=spec.spec_type,
                    spec_value=spec.spec_value,
                    manufacturer_id=spec.manufacturer_id,
                    model_number=spec.model_number
                )
                db.add(db_spec)
                new_specs.append(db_spec)

            db.commit()
            return new_specs
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def update_product_dimensions(
        self,
        db: Session,
        product_id: int,
        dimensions: List[ProductDimensionSchema]
    ):
        # 製品の存在確認
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        try:
            # 既存の寸法を全て削除
            db.query(ProductDimension).filter(
                ProductDimension.product_id == product_id
            ).delete()

            # 新しい寸法を追加
            new_dimensions = []
            for dim in dimensions:
                db_dimension = ProductDimension(
                    product_id=product_id,
                    dimension_type=dim.dimension_type,
                    value=dim.value,
                    unit=dim.unit
                )
                db.add(db_dimension)
                new_dimensions.append(db_dimension)

            db.commit()
            return new_dimensions
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def create_product_specification(
        self,
        db: Session,
        product_id: int,
        spec_data: ProductSpecificationSchema
    ):
        # 製品の存在確認
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        try:
            db_spec = ProductSpecification(
                product_id=product_id,
                spec_type=spec_data.spec_type,
                spec_value=spec_data.spec_value,
                manufacturer_id=spec_data.manufacturer_id,
                model_number=spec_data.model_number
            )
            db.add(db_spec)
            db.commit()
            db.refresh(db_spec)
            return db_spec
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def update_product_specification(
        self,
        db: Session,
        spec_id: int,
        spec_data: ProductSpecificationSchema
    ):
        db_spec = db.query(ProductSpecification).filter(
            ProductSpecification.id == spec_id
        ).first()

        if not db_spec:
            raise HTTPException(
                status_code=404, detail="Specification not found")

        for field, value in spec_data.model_dump(exclude_unset=True).items():
            if field != "id" and field != "product_id":  # IDとproduct_idは更新しない
                setattr(db_spec, field, value)

        try:
            db.commit()
            db.refresh(db_spec)
            return db_spec
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_product_specification(self, db: Session, spec_id: int):
        db_spec = db.query(ProductSpecification).filter(
            ProductSpecification.id == spec_id
        ).first()

        if not db_spec:
            raise HTTPException(
                status_code=404, detail="Specification not found")

        try:
            db.delete(db_spec)
            db.commit()
            return {"message": "Specification deleted successfully"}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def create_product_dimension(
        self,
        db: Session,
        product_id: int,
        dimension_data: ProductDimensionSchema
    ):
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        try:
            db_dimension = ProductDimension(
                product_id=product_id,
                dimension_type=dimension_data.dimension_type,
                value=dimension_data.value,
                unit=dimension_data.unit
            )
            db.add(db_dimension)
            db.commit()
            db.refresh(db_dimension)
            return db_dimension
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_product_dimension(self, db: Session, dimension_id: int):
        """指定された寸法情報を削除する"""
        db_dimension = db.query(ProductDimension).filter(
            ProductDimension.id == dimension_id
        ).first()

        if not db_dimension:
            raise HTTPException(
                status_code=404, detail="Dimension not found")

        try:
            db.delete(db_dimension)
            db.commit()
            return {"message": "Dimension deleted successfully"}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    def is_my_product(self, db: Session, product_id: int, user_id: int) -> bool:
        """
        指定された製品が現在のユーザーの物件に属しているかを確認する

        Args:
            db (Session): データベースセッション
            product_id (int): 製品ID
            user_id (int): ユーザーID

        Returns:
            bool: ユーザーの物件に属する製品である場合はTrue、そうでない場合はFalse
        """
        product = db.query(Product).join(Room).join(Property).filter(
            Product.id == product_id,
            Property.user_id == user_id,
            Property.is_deleted == False
        ).first()
        return product is not None


product_service = ProductService()
