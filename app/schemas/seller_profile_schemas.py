from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SellerProfileSchema(BaseModel):
    id: Optional[int] = None
    user_id: int
    company_name: Optional[str] = None
    representative_name: Optional[str] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    business_registration_number: Optional[str] = None
    tax_registration_number: Optional[str] = None
    stripe_account_id: Optional[str] = None
    stripe_account_status: Optional[str] = "pending"
    stripe_account_type: Optional[str] = "standard"
    stripe_onboarding_completed: bool = False
    stripe_charges_enabled: bool = False
    stripe_payouts_enabled: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
