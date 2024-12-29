from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BuyerProfile(BaseModel):
    id: Optional[int] = None
    user_id: int
    stripe_customer_id: Optional[str] = None
    shipping_postal_code: Optional[str] = None
    shipping_prefecture: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_address1: Optional[str] = None
    shipping_address2: Optional[str] = None
    phone_number: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
