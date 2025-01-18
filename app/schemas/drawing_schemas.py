from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class DrawingSchema(BaseModel):
    id: Optional[int] = None
    property_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
