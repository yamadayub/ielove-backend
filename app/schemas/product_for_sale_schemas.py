from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal


class ProductForSaleSchema(BaseModel):
    id: Optional[int] = None
    seller_id: int
    name: str
    description: Optional[str] = None
    price: int
    sale_type: Literal["property", "room", "product", "consultation"]
    consultation_type: Optional[Literal["online", "offline"]] = None
    status: str = "draft"
    property_id: Optional[int] = None
    room_id: Optional[int] = None
    product_id: Optional[int] = None
    is_negotiable: bool = False
    consultation_minutes: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
