from sqlalchemy.orm import Session
from app.models import User, SellerProfile
from app.schemas import UserSchema, UserUpdate, SellerProfileSchema
from .base import BaseCRUD


class UserCRUD(BaseCRUD[User, UserSchema, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    def create(self, db: Session, *, obj_in: UserSchema) -> User:
        """ユーザーを作成"""
        db_obj = User(
            clerk_user_id=obj_in.clerk_user_id,
            email=obj_in.email,
            name=obj_in.name,
            user_type=obj_in.user_type,
            role=obj_in.role,
            is_active=obj_in.is_active
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> User:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def get_by_email(self, db: Session, email: str):
        return db.query(self.model).filter(self.model.email == email).first()

    def get_by_role(self, db: Session, role: str, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(self.model.role == role)\
            .offset(skip).limit(limit).all()

    def get_active_users(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(self.model.is_active == True)\
            .offset(skip).limit(limit).all()

    def get_seller_profile(self, db: Session, user_id: str):
        return db.query(SellerProfile).filter(SellerProfile.user_id == user_id).first()

    def create_seller_profile(self, db: Session, *, user_id: str, obj_in: SellerProfileSchema):
        db_obj = SellerProfile(
            user_id=user_id,
            **obj_in.model_dump(exclude_unset=True)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_seller_profile(self, db: Session, *, db_obj: SellerProfile, obj_in: SellerProfileSchema):
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_clerk_id(self, db: Session, clerk_user_id: str):
        return db.query(self.model).filter(self.model.clerk_user_id == clerk_user_id).first()


user = UserCRUD()
