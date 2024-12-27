from typing import Optional
from pydantic import BaseModel


class CompanySchema(BaseModel):
    id: Optional[int] = None
    name: str
    company_type: str
    description: Optional[str] = None
    website: Optional[str] = None

    class Config:
        from_attributes = True
