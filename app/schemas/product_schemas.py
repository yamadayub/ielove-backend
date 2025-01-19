from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from .image_schemas import ImageSchema
from .product_specification_schemas import ProductSpecificationSchema
from .product_dimension_schemas import ProductDimensionSchema


class ProductSchema(BaseModel):
    id: Optional[int] = None
    room_id: int
    product_category_id: Optional[int] = None
    product_category_name: Optional[str] = None
    manufacturer_name: Optional[str] = None
    name: str
    product_code: Optional[str] = None
    description: Optional[str] = None
    catalog_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: Optional[str] = None
    is_deleted: Optional[bool] = None

    class Config:
        from_attributes = True


class ProductDetailsSchema(ProductSchema):
    specifications: List[ProductSpecificationSchema]
    dimensions: List[ProductDimensionSchema]
    images: List[ImageSchema]


class PropertyProductsResponse(BaseModel):
    """物件に紐づく製品情報のレスポンススキーマ"""
    id: int
    name: str
    description: Optional[str] = None
    product_code: Optional[str] = None
    catalog_url: Optional[str] = None
    room_id: int
    room_name: str
    product_category_id: Optional[int] = None
    product_category_name: Optional[str] = None
    manufacturer_name: Optional[str] = None
    specifications: List[ProductSpecificationSchema] = []
    dimensions: List[ProductDimensionSchema] = []
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, product):
        return cls(
            id=product.id,
            name=product.name,
            description=product.description,
            product_code=product.product_code,
            catalog_url=product.catalog_url,
            room_id=product.room_id,
            room_name=product.room.name if product.room else None,
            product_category_id=product.product_category_id,
            product_category_name=product.product_category.name if product.product_category else None,
            manufacturer_name=product.manufacturer_name,
            specifications=product.specifications,
            dimensions=product.dimensions,
            created_at=product.created_at
        )
