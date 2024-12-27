from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import app.schemas as schemas
from app.services.product_service import product_service
from app.database import get_db
from app.auth.dependencies import get_current_user

router = APIRouter(tags=["dimensions"])


@router.post("/products/{product_id}/dimensions", response_model=schemas.ProductDimensionSchema, summary="製品寸法を追加する")
async def create_product_dimension(
    product_id: int,
    dimension_data: schemas.ProductDimensionSchema,
    db: Session = Depends(get_db),
    current_user: schemas.UserSchema = Depends(get_current_user)
):
    """製品に新しい寸法情報を1件追加する"""
    dimension_data.product_id = product_id
    return await product_service.create_product_dimension(db, product_id, dimension_data)


@router.put("/products/{product_id}/dimensions", response_model=List[schemas.ProductDimensionSchema], summary="製品寸法を一括更新する")
async def update_product_dimensions(
    product_id: int,
    dimensions: List[schemas.ProductDimensionSchema],
    db: Session = Depends(get_db),
    current_user: schemas.UserSchema = Depends(get_current_user)
):
    """製品の寸法情報を一括更新する（既存の寸法は全て削除され、新しい寸法に置き換えられる）"""
    return await product_service.update_product_dimensions(db, product_id, dimensions)


@router.get("/products/{product_id}/dimensions", response_model=List[schemas.ProductDimensionSchema], summary="製品寸法一覧を取得する")
async def get_product_dimensions(
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.UserSchema = Depends(get_current_user)
):
    """指定された製品の寸法情報一覧を取得する"""
    return await product_service.get_product_dimensions(db, product_id, skip, limit)


@router.delete("/dimensions/{dimension_id}", response_model=None, summary="製品寸法を削除する")
async def delete_product_dimension(
    dimension_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserSchema = Depends(get_current_user)
):
    """指定された寸法情報を1件削除する"""
    return await product_service.delete_product_dimension(db, dimension_id)


@router.get("/dimensions/{dimension_id}", response_model=schemas.ProductDimensionSchema, summary="製品寸法を取得する")
async def get_product_dimension(
    dimension_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserSchema = Depends(get_current_user)
):
    """指定されたIDの寸法情報を取得する"""
    return await product_service.get_product_dimension(db, dimension_id)
