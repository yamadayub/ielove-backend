from sqlalchemy.orm import Session
from app.models import Drawing
from app.schemas.drawing_schemas import DrawingSchema
from .base import BaseCRUD
from typing import List, Optional


class DrawingCRUD(BaseCRUD[Drawing, DrawingSchema, DrawingSchema]):
    def get_by_property(
        self,
        db: Session,
        property_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Drawing]:
        """
        指定された物件に紐づく図面一覧を取得する
        """
        return (
            db.query(self.model)
            .filter(Drawing.property_id == property_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


drawing = DrawingCRUD(Drawing)
