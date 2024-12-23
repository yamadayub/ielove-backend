from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PurchaseSchema(BaseModel):
    id: Optional[int] = None
    buyer_id: int
    product_for_sale_id: int
    amount: int
    status: str = "pending"
    stripe_payment_intent_id: Optional[str] = None
    stripe_payment_status: Optional[str] = None
    stripe_transfer_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
