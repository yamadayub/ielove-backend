from typing import Optional
from pydantic import BaseModel


class ProductSpecificationSchema(BaseModel):
    id: Optional[int] = None
    product_id: Optional[int] = None
    spec_type: Optional[str] = None
    spec_value: Optional[str] = None
    manufacturer_id: Optional[int] = None
    model_number: Optional[str] = None

    class Config:
        from_attributes = True
