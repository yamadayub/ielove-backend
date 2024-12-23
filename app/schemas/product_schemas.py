from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from .image_schemas import ImageSchema
from .product_specification_schemas import ProductSpecificationSchema
from .product_dimension_schemas import ProductDimensionSchema


class ProductSchema(BaseModel):
    id: Optional[int] = None
    room_id: int
    product_category_id: int
    manufacturer_id: Optional[int] = None
    name: str
    product_code: str
    description: Optional[str] = None
    catalog_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProductDetailsSchema(ProductSchema):
    specifications: List[ProductSpecificationSchema]
    dimensions: List[ProductDimensionSchema]
    images: List[ImageSchema]
