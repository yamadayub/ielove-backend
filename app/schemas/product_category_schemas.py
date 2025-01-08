from typing import Optional
from pydantic import BaseModel


class ProductCategorySchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True
