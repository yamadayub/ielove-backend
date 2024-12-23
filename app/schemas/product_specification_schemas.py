from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class ProductSpecificationSchema(BaseModel):
    id: Optional[int] = None
    product_id: int
    spec_type: str
    spec_value: str
    manufacturer_id: Optional[int] = None
    model_number: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
