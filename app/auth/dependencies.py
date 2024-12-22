from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.user_service import user_service
from app.schemas import UserSchema
from typing import Optional, Annotated


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    clerk_user_id: Annotated[str, Query(description="ClerkのユーザーID")],
    db: Session = Depends(get_db)
) -> UserSchema:
    """
    現在のユーザーを取得する依存関数

    Args:
        clerk_user_id (str): ClerkのユーザーID
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
