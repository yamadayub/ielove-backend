from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.enums import ListingType, Visibility, ListingStatus


class ListingItem(BaseModel):
    id: Optional[int] = None
    seller_user_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    price: int = Field(gt=0)
    listing_type: ListingType
    property_id: Optional[int] = None
    room_id: Optional[int] = None
    product_id: Optional[int] = None
    is_negotiable: Optional[bool] = False
    service_type: Optional[str] = None
    service_duration: Optional[int] = None
    visibility: Visibility = Visibility.PUBLIC
    status: ListingStatus = ListingStatus.DRAFT
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True
