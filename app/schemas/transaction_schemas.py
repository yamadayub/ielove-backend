from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

from app.enums import TransactionStatus, PaymentStatus, TransferStatus
from app.schemas.user_schemas import UserSchema
from app.schemas.listing_item_schemas import ListingItem


class TransactionSchema(BaseModel):
    id: Optional[int] = None
    buyer_user_id: int
    seller_user_id: int
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


class TransactionInfo(BaseModel):
    transactionId: int
    purchaseDate: str
    amount: int

    class Config:
        from_attributes = True


class PropertyInfo(BaseModel):
    id: int
    name: str
    prefecture: str


class ListingInfo(BaseModel):
    id: int
    title: str
    price: int


class PurchasedTransaction(BaseModel):
    id: int
    purchaseDate: datetime
    totalAmount: int
    listing: ListingInfo
    property: PropertyInfo


class PurchasedTransactionsResponse(BaseModel):
    transactions: List[PurchasedTransaction]


class TransactionCheckResponse(BaseModel):
    isPurchased: bool
    purchaseInfo: Optional[dict] = None

    class Config:
        from_attributes = True
