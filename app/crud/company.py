from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import Company
from app.schemas import CompanySchema
from .base import CRUDBase


class CRUDCompany(CRUDBase[Company, CompanySchema, CompanySchema]):
    def get_by_company_type(self, db: Session, company_type: str) -> List[Company]:
        return db.query(self.model).filter(self.model.company_type == company_type).all()


company = CRUDCompany(Company)
