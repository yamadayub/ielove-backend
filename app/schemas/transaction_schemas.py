from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from app.enums import TransactionStatus, PaymentStatus, TransferStatus
from app.schemas.user_schemas import UserSchema
from app.schemas.listing_item_schemas import ListingItem


class TransactionSchema(BaseModel):
    id: Optional[int] = None
    buyer_id: int
    seller_id: int
    listing_id: int
    payment_intent_id: str
    total_amount: int
    platform_fee: int
    seller_amount: int
    transaction_status: TransactionStatus = TransactionStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.PENDING
    transfer_status: TransferStatus = TransferStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Relationships (APIレスポンス用)
    buyer: Optional[UserSchema] = None
    seller: Optional[UserSchema] = None
    listing: Optional[ListingItem] = None

    class Config:
        from_attributes = True
