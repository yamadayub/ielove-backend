from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import ProductCategory
from app.schemas.product_category_schemas import ProductCategorySchema

router = APIRouter(
    prefix="/product-categories",
    tags=["product-categories"]
)


@router.get("", response_model=List[ProductCategorySchema])
def get_product_categories(
    db: Session = Depends(get_db)
):
    """
    製品カテゴリ一覧を取得します。
    """
    return db.query(ProductCategory).order_by(ProductCategory.id).all()
