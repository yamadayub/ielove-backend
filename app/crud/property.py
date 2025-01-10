from sqlalchemy.orm import Session
from app.models import Property
from app.schemas import PropertySchema
from .base import BaseCRUD
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.sql import desc
from datetime import datetime


class PropertyCRUD(BaseCRUD[Property, PropertySchema, PropertySchema]):
    def __init__(self):
        super().__init__(Property)

    def create(self, db: Session, *, obj_in: PropertySchema) -> Property:
        db_obj = Property(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Property, obj_in: PropertySchema) -> Property:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> Property:
        """
        指定されたIDの物件を論理削除する
        """
        obj = db.query(self.model).get(id)
        if obj:
            obj.is_deleted = True
            obj.deleted_at = datetime.now()
            db.add(obj)
            db.commit()
            db.refresh(obj)
        return obj

    def get_by_user(self, db: Session, user_id: str, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(self.model.user_id == user_id)\
            .offset(skip).limit(limit).all()

    def get_by_prefecture(self, db: Session, prefecture: str, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(self.model.prefecture == prefecture)\
            .offset(skip).limit(limit).all()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Property]:
        """
        物件の一覧を取得する（論理削除されていないもののみ）
        """
        return db.query(self.model).filter(
            self.model.is_deleted == False
        ).offset(skip).limit(limit).all()

    def get(self, db: Session, id: int) -> Optional[Property]:
        """
        指定されたIDの物件を取得する（論理削除されていないもののみ）
        """
        return db.query(self.model).filter(
            self.model.id == id,
            self.model.is_deleted == False
        ).first()

    def get_by_user_with_filters(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None
    ) -> Tuple[List[Property], int]:
        """
        指定されたユーザーIDの物件一覧をフィルター条件付きで取得する（論理削除されていないもののみ）
        """
        query = db.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.is_deleted == False
        )

        if filters:
            if filters.get("property_type"):
                query = query.filter(
                    self.model.property_type == filters["property_type"])
            if filters.get("prefecture"):
                query = query.filter(
                    self.model.prefecture == filters["prefecture"])

        total = query.count()
        items = query.order_by(desc(self.model.created_at)).offset(
            skip).limit(limit).all()

        return items, total


property = PropertyCRUD()
