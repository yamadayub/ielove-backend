from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SaleSchema(BaseModel):
    id: Optional[int] = None
    seller_id: int
    product_for_sale_id: int
    purchase_id: int
    amount: int
    platform_fee: int
    seller_amount: int
    status: str = "pending"
    stripe_transfer_id: Optional[str] = None
    stripe_transfer_status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
