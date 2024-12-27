from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import company_service
from app.schemas.company_schemas import CompanySchema

router = APIRouter(
    prefix="/companies",
    tags=["companies"]
)


@router.get("/by-type/{company_type}", response_model=List[CompanySchema], summary="会社情報をタイプ別に取得する")
def get_companies_by_type(
    company_type: str,
    db: Session = Depends(get_db)
):
    """指定されたcompany_typeに基づいて会社情報を取得する

    Args:
        company_type (str): 会社タイプ（manufacturer, design, construction）
        db (Session): データベースセッション

    Returns:
        List[CompanySchema]: 会社情報のリスト
    """
    return company_service.get_companies_by_type(db, company_type)
