from sqlalchemy.orm import Session
from app.models import Company
from typing import List


def get_companies_by_type(db: Session, company_type: str) -> List[Company]:
    """指定されたcompany_typeに基づいて会社情報を取得する"""
    companies = db.query(Company).filter(
        Company.company_type == company_type).all()
    return companies  # 0件の場合は空のリストが返される
