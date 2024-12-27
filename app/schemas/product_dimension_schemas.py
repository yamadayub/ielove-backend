from typing import List, Optional
from pydantic import BaseModel


class ProductDimensionSchema(BaseModel):
    id: Optional[int] = None
    product_id: int
    dimension_type: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None

    class Config:
        from_attributes = True
