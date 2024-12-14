
from sqlalchemy.orm import Session
from app.models import Company
from app.schemas import CompanySchema
from .base import BaseCRUD

class CompanyCRUD(BaseCRUD[Company, CompanySchema, CompanySchema]):
    def __init__(self):
        super().__init__(Company)

    def get_by_type(self, db: Session, company_type: str, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(self.model.company_type == company_type)\
            .offset(skip).limit(limit).all()

    def get_manufacturers(self, db: Session, skip: int = 0, limit: int = 100):
        return self.get_by_type(db, "manufacturer", skip, limit)

company = CompanyCRUD()
