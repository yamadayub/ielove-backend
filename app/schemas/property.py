from pydantic import BaseModel
from datetime import datetime


class PropertySchema(BaseModel):
    id: int
    name: str
    description: str
    address: str
    property_type: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PropertyCreateSchema(BaseModel):
    name: str
    description: str
    address: str
    property_type: str
    status: str = "available"
