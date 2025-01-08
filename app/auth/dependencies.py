from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.user_service import user_service
from app.schemas import UserSchema
from typing import Optional


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    clerk_user_id: str = Header(..., description="ClerkのユーザーID",
                                alias="x-clerk-user-id"),
    db: Session = Depends(get_db)
) -> UserSchema:
    """
    現在のユーザーを取得する依存関数

    Args:
        clerk_user_id (str): ClerkのユーザーID（ヘッダーから取得）
        db (Session): データベースセッション

    Returns:
        UserSchema: 認証されたユーザー情報

    Raises:
        HTTPException: 認証エラーの場合
    """
    user = user_service.get_user_by_clerk_id(db, clerk_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_user_optional(
    clerk_user_id: Optional[str] = Header(
        None, description="ClerkのユーザーID", alias="x-clerk-user-id"),
    db: Session = Depends(get_db)
) -> Optional[UserSchema]:
    """
    現在のユーザーを任意で取得する依存関数
    認証ヘッダーがない場合はNoneを返します

    Args:
        clerk_user_id (Optional[str]): ClerkのユーザーID（ヘッダーから取得）
        db (Session): データベースセッション

    Returns:
        Optional[UserSchema]: 認証されたユーザー情報、または未認証の場合はNone
    """
    if not clerk_user_id:
        return None

    user = user_service.get_user_by_clerk_id(db, clerk_user_id)
    return user
