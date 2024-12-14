
from sqlalchemy.orm import Session
from app.models import Company
from app.schemas import CompanySchema
from .base import BaseCRUD

class CompanyCRUD(BaseCRUD[Company, CompanySchema, CompanySchema]):
    def __init__(self):
        super().__init__(Company)

    def create(self, db: Session, *, obj_in: CompanySchema) -> Company:
        db_obj = Company(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Company, obj_in: CompanySchema) -> Company:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> Company:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def get_by_type(self, db: Session, company_type: str, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(self.model.company_type == company_type)\
            .offset(skip).limit(limit).all()

    def get_manufacturers(self, db: Session, skip: int = 0, limit: int = 100):
        return self.get_by_type(db, "manufacturer", skip, limit)

company = CompanyCRUD()
