from typing import Optional, List, Literal
from pydantic import BaseModel
from datetime import datetime

class ImageSchema(BaseModel):
    id: Optional[int] = None
    url: str
    description: Optional[str]
    image_type: Literal["main", "sub"]
    property_id: Optional[int] = None
    room_id: Optional[int] = None
    product_id: Optional[int] = None

class ProductSpecificationSchema(BaseModel):
    id: Optional[int] = None
    product_id: Optional[int] = None
    spec_type: str
    spec_value: str
    manufacturer_id: Optional[int] = None
    model_number: Optional[str] = None

class ProductDimensionSchema(BaseModel):
    id: Optional[int] = None
    product_id: Optional[int] = None
    dimension_type: str
    value: float
    unit: str

class ProductSchema(BaseModel):
    id: Optional[int] = None
    property_id: Optional[int] = None
    room_id: Optional[int] = None
    product_category_id: int
    manufacturer_id: int
    name: str
    model_number: str
    description: Optional[str] = None
    catalog_url: Optional[str] = None
    specifications: Optional[List[ProductSpecificationSchema]] = []
    dimensions: Optional[List[ProductDimensionSchema]] = []
    images: Optional[List[ImageSchema]] = []

class RoomSchema(BaseModel):
    id: Optional[int] = None
    property_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    products: Optional[List[ProductSchema]] = []
    images: Optional[List[ImageSchema]] = []

class PropertySchema(BaseModel):
    id: Optional[int] = None
    user_id: str
    name: str
    description: Optional[str] = None
    property_type: Literal["house", "apartment", "other"]
    prefecture: str
    layout: Optional[str] = None
    construction_year: Optional[int] = None
    construction_month: Optional[int] = None
    site_area: Optional[float] = None
    building_area: Optional[float] = None
    floor_count: Optional[int] = None
    structure: Optional[str] = None
    design_company_id: Optional[int] = None
    construction_company_id: Optional[int] = None
    rooms: Optional[List[RoomSchema]] = []
    images: Optional[List[ImageSchema]] = []

    class Config:
        from_attributes = True