from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.schemas.image_schemas import ImageSchema
from app.schemas.product_schemas import ProductDetailsSchema


class RoomSchema(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    property_id: int

    class Config:
        from_attributes = True


class RoomDetailsSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    property_id: int
    created_at: datetime
    products: List[ProductDetailsSchema]
    images: List[ImageSchema]

    class Config:
        from_attributes = True
