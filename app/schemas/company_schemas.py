from typing import Optional, Literal
from pydantic import BaseModel


class CompanySchema(BaseModel):
    id: Optional[int] = None
    name: str
    company_type: Literal["manufacturer", "design", "construction"]
    description: Optional[str] = None
    website: Optional[str] = None

    class Config:
        from_attributes = True
