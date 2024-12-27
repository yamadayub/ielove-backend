from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import app.schemas as schemas
from app.services.product_service import product_service
from app.database import get_db
from app.auth.dependencies import get_current_user

router = APIRouter(tags=["specifications"])


@router.post("/products/{product_id}/specifications", response_model=schemas.ProductSpecificationSchema, summary="製品仕様を追加する")
async def create_product_specification(
    product_id: int,
    spec_data: schemas.ProductSpecificationSchema,
    db: Session = Depends(get_db),
    current_user: schemas.UserSchema = Depends(get_current_user)
):
    """製品に新しい仕様情報を1件追加する"""
    spec_data.product_id = product_id
    return await product_service.create_product_specification(db, product_id, spec_data)


@router.put("/products/{product_id}/specifications", response_model=List[schemas.ProductSpecificationSchema], summary="製品仕様を一括更新する")
async def update_product_specifications(
    product_id: int,
    specifications: List[schemas.ProductSpecificationSchema],
    db: Session = Depends(get_db),
    current_user: schemas.UserSchema = Depends(get_current_user)
):
    """製品の仕様情報を一括更新する（既存の仕様は全て削除され、新しい仕様に置き換えられる）"""
    return await product_service.update_product_specifications(db, product_id, specifications)


@router.get("/products/{product_id}/specifications", response_model=List[schemas.ProductSpecificationSchema], summary="製品仕様一覧を取得する")
async def get_product_specifications(
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.UserSchema = Depends(get_current_user)
):
    """指定された製品の仕様情報一覧を取得する"""
    return await product_service.get_product_specifications(db, product_id, skip, limit)


@router.delete("/specifications/{spec_id}", response_model=None, summary="製品仕様を削除する")
async def delete_product_specification(
    spec_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserSchema = Depends(get_current_user)
):
    """指定された仕様情報を1件削除する"""
    return await product_service.delete_product_specification(db, spec_id)


@router.get("/specifications/{spec_id}", response_model=schemas.ProductSpecificationSchema, summary="製品仕様を取得する")
async def get_product_specification(
    spec_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserSchema = Depends(get_current_user)
):
    """指定されたIDの仕様情報を取得する"""
    return await product_service.get_product_specification(db, spec_id)
