from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.product_schemas import (
    ProductSchema,
    ProductDetailsSchema
)
from app.schemas.product_specification_schemas import ProductSpecificationSchema
from app.schemas.product_dimension_schemas import ProductDimensionSchema
from app.services.product_service import product_service
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.schemas.user_schemas import UserSchema

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
