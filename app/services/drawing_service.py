from sqlalchemy.orm import Session
from app.models import Drawing, Property
from app.crud.drawing import drawing as drawing_crud
from app.schemas.drawing_schemas import DrawingSchema
from fastapi import HTTPException


class DrawingService:
    def is_my_drawing(self, db: Session, drawing_id: int, user_id: int) -> bool:
        """
        指定された図面が現在のユーザーのものかを確認する

        Parameters:
        - db: データベースセッション
        - drawing_id: 図面ID
        - user_id: ユーザーID

        Returns:
        - bool: ユーザーの図面である場合はTrue、そうでない場合はFalse
        """
        drawing = drawing_crud.get(db, id=drawing_id)
        if not drawing:
            return False

        # 図面に紐づく物件を取得し、その所有者を確認
        property = db.query(Property).filter(
            Property.id == drawing.property_id).first()
        if not property:
            return False

        return property.user_id == user_id


drawing_service = DrawingService()
