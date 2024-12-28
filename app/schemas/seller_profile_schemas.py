from typing import Optional, Dict
from pydantic import BaseModel
from datetime import datetime


class SellerProfileSchema(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
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
    stripe_capabilities: Optional[Dict] = None

    class Config:
        from_attributes = True


class StripeAccountLink(BaseModel):
    url: str
    expires_at: int


class StripeDashboardLink(BaseModel):
    url: str
