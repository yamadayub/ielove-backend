from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import app.schemas as schemas
from app.services.user_service import user_service
from app.database import get_db
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/me", response_model=schemas.UserSchema, summary="現在のユーザー情報を取得する")
def get_me(
    request: Request,
    current_user: schemas.UserSchema = Depends(get_current_user)
):
    """
    現在のユーザー情報を取得します。
    """
    print("Headers:", request.headers)
    print("Clerk User ID:", request.headers.get("x-clerk-user-id"))
    print("Current User:", current_user)
    if not current_user:
        return None
    return current_user


@router.get("/me/seller", response_model=schemas.SellerProfileSchema, summary="現在のユーザーの販売者プロフィールを取得する")
def get_seller_profile(
    db: Session = Depends(get_db),
    current_user: schemas.UserSchema = Depends(get_current_user)
):
    """
    現在のユーザーの販売者プロフィールを取得します。
    """
    if not current_user:
        return None
    profile = user_service.get_seller_profile(db, current_user.id)
    if not profile:
        return None
    return profile


@router.patch("/me", response_model=schemas.UserSchema, summary="ユーザー情報を更新する")
def update_user(
    user_id: str,
    user_update: schemas.UserSchema,
    db: Session = Depends(get_db)
):
    """
    ユーザー情報を更新します。

    Parameters:
    - user_id: ユーザーID
    - user_update: 更新するユーザー情報
    """
    updated_user = user_service.update_user(db, user_id, user_update)
    if not updated_user:
        return None
    return updated_user


@router.patch("/me/seller", response_model=schemas.SellerProfileSchema, summary="Seller情報を更新する")
def update_seller_profile(
    user_id: str,
    profile_update: schemas.SellerProfileSchema,
    db: Session = Depends(get_db)
):
    """
    販売者プロフィールを更新します。

    Parameters:
    - user_id: ユーザーID
    - profile_update: 更新する販売者プロフィール情報
    """
    updated_profile = user_service.update_seller_profile(
        db, user_id, profile_update)
    if not updated_profile:
        return None
    return updated_profile


@router.post("/me/seller", response_model=schemas.SellerProfileSchema, summary="Seller情報を作成する")
def create_seller_profile(
    user_id: str,
    profile_create: schemas.SellerProfileSchema,
    db: Session = Depends(get_db)
):
    """
    販売者プロフィールを作成します。

    Parameters:
    - user_id: ユーザーID
    - profile_create: 作成する販売者プロフィール情報
    """
    return user_service.create_seller_profile(db, user_id, profile_create)


@router.post("", response_model=schemas.UserSchema, summary="ユーザーを作成する")
def create_user(
    user_create: schemas.UserSchema,
    db: Session = Depends(get_db)
):
    """
    新規ユーザーを作成します。

    Parameters:
    - user_create: ユーザー作成情報
        - clerk_user_id: ClerkのユーザーID
        - email: メールアドレス
        - name: ユーザー名
        - user_type: "individual" または "business"
        - role: ユーザーの役割（デフォルト: "buyer"）
        - is_active: アクティブ状態（デフォルト: true）
    """
    return user_service.create_user(db, user_create)
