from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class ProductDimensionSchema(BaseModel):
    id: Optional[int] = None
    product_id: int
    dimension_type: str
    value: float
    unit: str
    created_at: datetime

    class Config:
        from_attributes = True
