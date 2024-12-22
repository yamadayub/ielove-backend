from sqlalchemy.orm import Session
from app.crud.product import product as product_crud
from app.schemas import ProductCreate
from typing import Optional
from fastapi import HTTPException
from app.models import Product, ProductSpecification, ProductDimension
from typing import List
from app.schemas import ProductSpecificationSchema, ProductDimensionSchema


class ProductService:
    def create_product(self, db: Session, product_data: ProductCreate) -> ProductCreate:
        """製品情報を作成する"""
        return product_crud.create(db, obj_in=product_data)

    def get_product(self, db: Session, product_id: int) -> Optional[ProductCreate]:
        """製品情報を取得する"""
        return product_crud.get(db, id=product_id)

    def get_products_by_room(self, db: Session, room_id: int, skip: int = 0, limit: int = 100):
        """
        指定された部屋IDに紐づく製品一覧を取得
        """
        return product_crud.get_products_by_room(db, room_id=room_id, skip=skip, limit=limit)

    def get_product_details(self, db: Session, product_id: int):
        """
        製品の細情報（仕様・寸法を含む）を取得
        """
        product = product_crud.get_product_with_details(db, product_id)
        if not product:
            return None
        return product

    async def update_product(self, db: Session, product_id: int, product_data: ProductCreate):
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
        # 製品の存在確��
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

    async def update_product_dimension(
        self,
        db: Session,
        dimension_id: int,
        dimension_data: ProductDimensionSchema
    ):
        db_dimension = db.query(ProductDimension).filter(
            ProductDimension.id == dimension_id
        ).first()

        if not db_dimension:
            raise HTTPException(status_code=404, detail="Dimension not found")

        for field, value in dimension_data.model_dump(exclude_unset=True).items():
            if field != "id" and field != "product_id":  # IDとproduct_idは更新しない
                setattr(db_dimension, field, value)

        try:
            db.commit()
            db.refresh(db_dimension)
            return db_dimension
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_product_dimension(self, db: Session, dimension_id: int):
        db_dimension = db.query(ProductDimension).filter(
            ProductDimension.id == dimension_id
        ).first()

        if not db_dimension:
            raise HTTPException(status_code=404, detail="Dimension not found")

        try:
            db.delete(db_dimension)
            db.commit()
            return {"message": "Dimension deleted successfully"}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def get_product_specifications(
        self,
        db: Session,
        product_id: int,
        skip: int = 0,
        limit: int = 100
    ):
        # 製品の存在確認
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        specifications = db.query(ProductSpecification).filter(
            ProductSpecification.product_id == product_id
        ).offset(skip).limit(limit).all()

        return specifications

    async def get_product_specification(self, db: Session, spec_id: int):
        db_spec = db.query(ProductSpecification).filter(
            ProductSpecification.id == spec_id
        ).first()

        if not db_spec:
            raise HTTPException(
                status_code=404, detail="Specification not found")

        return db_spec

    async def get_product_dimensions(
        self,
        db: Session,
        product_id: int,
        skip: int = 0,
        limit: int = 100
    ):
        # 製品の存在確認
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        dimensions = db.query(ProductDimension).filter(
            ProductDimension.product_id == product_id
        ).offset(skip).limit(limit).all()

        return dimensions

    async def get_product_dimension(self, db: Session, dimension_id: int):
        db_dimension = db.query(ProductDimension).filter(
            ProductDimension.id == dimension_id
        ).first()

        if not db_dimension:
            raise HTTPException(status_code=404, detail="Dimension not found")

        return db_dimension


product_service = ProductService()
