from pydantic import BaseModel
from typing import Dict, Any


class CheckoutSessionCreate(BaseModel):
    listingId: int
    # customerInfo: Dict[str, Any]


class CheckoutSessionResponse(BaseModel):
    sessionId: str
    url: str


class CheckoutErrorResponse(BaseModel):
    error: str
    message: str
