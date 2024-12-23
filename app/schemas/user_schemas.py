from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Optional


class UserSchema(BaseModel):
    id: Optional[int] = None
    clerk_user_id: str
    email: str
    name: str
    user_type: Literal["individual", "business"]
    role: str = "buyer"
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_sign_in: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    user_type: Optional[Literal["individual", "business"]] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    last_sign_in: Optional[datetime] = None

    class Config:
        from_attributes = True
