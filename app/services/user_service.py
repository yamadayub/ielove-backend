from sqlalchemy.orm import Session
from app.crud.user import user as user_crud
from app.schemas import UserSchema, SellerProfileSchema
from typing import Optional


class UserService:
    def get_user(self, db: Session, user_id: str):
        """ユーザー情報を取得"""
        return user_crud.get(db, id=user_id)

    def get_seller_profile(self, db: Session, user_id: str):
        """販売者プロフィールを取得"""
        return user_crud.get_seller_profile(db, user_id=user_id)

    def update_user(self, db: Session, user_id: str, user_update: UserSchema):
        """ユーザー情報を更新"""
        user = user_crud.get(db, id=user_id)
        if not user:
            return None
        return user_crud.update(db, db_obj=user, obj_in=user_update)

    def update_seller_profile(self, db: Session, user_id: str, profile_update: SellerProfileSchema):
        """販売者プロフィールを更新"""
        profile = user_crud.get_seller_profile(db, user_id=user_id)
        if not profile:
            return None
        return user_crud.update_seller_profile(db, db_obj=profile, obj_in=profile_update)

    def create_seller_profile(self, db: Session, user_id: str, profile_create: SellerProfileSchema):
        """販売者プロフィールを作成"""
        return user_crud.create_seller_profile(db, user_id=user_id, obj_in=profile_create)

    def create_user(self, db: Session, user_create: UserSchema):
        """ユーザーを作成"""
        return user_crud.create(db, obj_in=user_create)

    def get_user_by_clerk_id(self, db: Session, clerk_user_id: str):
        """Clerk User IDでユーザーを取得"""
        return user_crud.get_by_clerk_id(db, clerk_user_id)


user_service = UserService()
