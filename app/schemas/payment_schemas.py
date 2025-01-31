from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SavedPaymentMethodBase(BaseModel):
    payment_type: str
    card_brand: Optional[str] = None
    card_last4: Optional[str] = None
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None
    is_default: bool = False
    is_active: bool = True


class SavedPaymentMethodCreate(SavedPaymentMethodBase):
    payment_method_id: str
    user_id: int


class SavedPaymentMethodUpdate(SavedPaymentMethodBase):
    payment_method_id: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class SavedPaymentMethodInDB(SavedPaymentMethodBase):
    id: int
    user_id: int
    payment_method_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SavedPaymentMethodResponse(SavedPaymentMethodInDB):
    pass
