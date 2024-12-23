from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class ProductCategorySchema(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
