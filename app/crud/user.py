from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserSchema
from .base import BaseCRUD

class UserCRUD(BaseCRUD[User, UserSchema, UserSchema]):
    def __init__(self):
        super().__init__(User)

    def create(self, db: Session, *, obj_in: UserSchema) -> User:
        db_obj = User(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in: UserSchema) -> User:
        update_data = obj_in.dict(exclude_unset=True)
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

user = UserCRUD()