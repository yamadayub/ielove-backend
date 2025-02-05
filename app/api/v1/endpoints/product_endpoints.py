from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.schemas.product_schemas import (
    ProductSchema,
    ProductDetailsSchema,
    PropertyProductsResponse
)
from app.schemas.product_specification_schemas import ProductSpecificationSchema
from app.schemas.product_dimension_schemas import ProductDimensionSchema
from app.services.product_service import product_service
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.schemas.user_schemas import UserSchema
from app.models import Product, Room, ProductCategory, ProductSpecification
from app.crud.product import product as product_crud

router = APIRouter(
    prefix="/products",
    tags=["products"]
)


@router.post("", response_model=ProductSchema, summary="製品情報を作成する")
def create_product(
    room_id: int,
    product_data: ProductSchema,
    db: Session = Depends(get_db)
):
    """部屋に紐づく製品情報を作成する"""
    product_data.room_id = room_id
    return product_service.create_product(db, product_data)


@router.get("", response_model=List[ProductSchema], summary="製品一覧を取得する")
def get_products(
    room_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """特定の部屋に紐づく製品一覧を取得"""
    return product_service.get_products_by_room(db, room_id=room_id, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductSchema, summary="指定されたIDの製品を取得する")
def get_product(product_id: int, db: Session = Depends(get_db)):
    """指定されたIDの製品を取得"""
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/{product_id}/is-mine", response_model=bool, summary="指定された製品が自分の物件に属しているかを確認する")
def is_my_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """
    指定された製品が現在のユーザーの物件に属しているかを確認する

    Parameters:
    - product_id: 製品ID

    Returns:
    - bool: ユーザーの物件に属する製品である場合はTrue、そうでない場合はFalse
    """
    return product_service.is_my_product(db, product_id, current_user.id)


@router.patch("/{product_id}", response_model=ProductSchema, summary="製品情報を更新する")
async def update_product(
    product_id: int,
    product_data: ProductSchema,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """指定されたIDの製品情報を更新する"""
    return await product_service.update_product(db, product_id, product_data)


@router.delete("/{product_id}", response_model=None, summary="製品を削除する")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """指定されたIDの製品を削除する"""
    return await product_service.delete_product(db, product_id)


@router.get("/{product_id}/details", response_model=ProductDetailsSchema, summary="製品の詳細情報を取得する")
def get_product_details(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    製品の詳細情報を、関連する全ての情報（仕様、寸法、画像）と共に取得します。
    また、製品が属する部屋と物件の基本情報も含みます。

    Parameters:
    - product_id: 製品ID

    Returns:
    - 製品の詳細情報（階層構造）
        - 製品情報
        - 製品の画像一覧
        - 製品仕様一覧
        - 製品寸法一覧
        - 部屋の基本情報
        - 物件の基本情報
    """
    return product_service.get_product_details(db, product_id)


@router.get("/property/{property_id}", response_model=List[PropertyProductsResponse], summary="物件に紐づく全製品情報を取得する")
def get_products_by_property(
    property_id: int,
    db: Session = Depends(get_db)
):
    """
    指定された物件IDに紐づく全ての製品情報を取得します。
    各製品の部屋情報と製品カテゴリ情報も含みます。

    Parameters:
    - property_id: 物件ID

    Returns:
    - 製品情報のリスト（部屋情報、カテゴリ情報、製造者情報、仕様、寸法を含む）
    """
    products = db.query(Product).options(
        joinedload(Product.room),
        joinedload(Product.product_category),
        joinedload(Product.specifications),
        joinedload(Product.dimensions)
    ).join(
        Room, Product.room_id == Room.id
    ).filter(
        Room.property_id == property_id
    ).all()

    if not products:
        return []

    return [PropertyProductsResponse.from_orm(product) for product in products]


@router.put("/{product_id}/specifications", response_model=List[ProductSpecificationSchema])
def update_product_specifications(
    product_id: int,
    specifications: List[ProductSpecificationSchema],
    db: Session = Depends(get_db)
):
    # 製品の存在確認
    product = product_crud.get(db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 既存の仕様を更新または新規作成
    for spec in specifications:
        if spec.id:  # 既存の仕様の場合
            db_spec = db.query(ProductSpecification).get(spec.id)
            if db_spec and db_spec.product_id == product_id:
                # 既存の仕様を更新
                for key, value in spec.dict(exclude_unset=True).items():
                    setattr(db_spec, key, value)
        else:  # 新規の仕様の場合
            db_spec = ProductSpecification(
                product_id=product_id,
                spec_type=spec.spec_type,
                spec_value=spec.spec_value
            )
            db.add(db_spec)

    db.commit()

    # 更新された仕様一覧を返す
    return db.query(ProductSpecification).filter(
        ProductSpecification.product_id == product_id
    ).all()
