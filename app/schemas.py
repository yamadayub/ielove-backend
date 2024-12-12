
from pydantic import BaseModel
from typing import List, Optional

class ImageSchema(BaseModel):
    id: Optional[int]
    url: str
    description: Optional[str]
    image_type: str
    property_id: Optional[int]
    room_id: Optional[int]
    product_id: Optional[int]

class ProductSpecificationSchema(BaseModel):
    id: Optional[int]
    product_id: Optional[int]
    spec_type: str
    spec_value: str
    manufacturer_id: Optional[int]
    model_number: Optional[str]

class ProductDimensionSchema(BaseModel):
    id: Optional[int]
    product_id: Optional[int]
    dimension_type: str
    value: float
    unit: str

class RoomSchema(BaseModel):
    id: Optional[int]
    property_id: Optional[int]
    name: str
    description: Optional[str]
    products: Optional[List["ProductSchema"]] = []
    images: Optional[List[ImageSchema]] = []

class ProductSchema(BaseModel):
    id: Optional[int]
    property_id: Optional[int]
    room_id: Optional[int]
    product_category_id: Optional[int]
    manufacturer_id: Optional[int]
    name: str
    model_number: str
    description: Optional[str]
    catalog_url: Optional[str]
    specifications: Optional[List[ProductSpecificationSchema]] = []
    dimensions: Optional[List[ProductDimensionSchema]] = []
    images: Optional[List[ImageSchema]] = []

class PropertySchema(BaseModel):
    id: Optional[int]
    user_id: Optional[str]
    name: str
    description: Optional[str]
    property_type: str
    prefecture: str
    layout: Optional[str]
    construction_year: Optional[int]
    construction_month: Optional[int]
    site_area: Optional[float]
    building_area: Optional[float]
    floor_count: Optional[int]
    structure: Optional[str]
    design_company_id: Optional[int]
    construction_company_id: Optional[int]
    rooms: Optional[List[RoomSchema]] = []
    images: Optional[List[ImageSchema]] = []

    class Config:
        from_attributes = True
