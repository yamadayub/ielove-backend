from typing import List, Optional
from pydantic import BaseModel


class ProductSpecificationSchema(BaseModel):
    id: Optional[int] = None
    product_id: int
    spec_type: Optional[str] = None
    spec_value: Optional[str] = None
    manufacturer_id: Optional[int] = None
    model_number: Optional[str] = None

    class Config:
        from_attributes = True
