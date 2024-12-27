from sqlalchemy.orm import Session
from app.models import Company


def get_companies_by_type(db: Session, company_type: str):
    """指定されたcompany_typeに基づいて会社情報を取得する"""
    return db.query(Company).filter(Company.company_type == company_type).all()
