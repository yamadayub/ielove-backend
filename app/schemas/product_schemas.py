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
    manufacturer_id: Optional[int] = None
    manufacturer_name: Optional[str] = None
    name: str
    product_code: Optional[str] = None
    description: Optional[str] = None
    catalog_url: Optional[str] = None

    class Config:
        from_attributes = True


class ProductDetailsSchema(ProductSchema):
    specifications: List[ProductSpecificationSchema]
    dimensions: List[ProductDimensionSchema]
    images: List[ImageSchema]
