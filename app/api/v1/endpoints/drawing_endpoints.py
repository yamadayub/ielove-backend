from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.crud.drawing import drawing as drawing_crud
from app.schemas.drawing_schemas import DrawingSchema
from app.schemas.user_schemas import UserSchema

router = APIRouter()


@router.post("", response_model=DrawingSchema, summary="図面を作成する")
def create_drawing(
    drawing_data: DrawingSchema,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """図面を作成します。"""
    return drawing_crud.create(db, obj_in=drawing_data)


@router.get("/{drawing_id}", response_model=DrawingSchema, summary="図面を取得する")
def get_drawing(
    drawing_id: int,
    db: Session = Depends(get_db)
):
    """指定されたIDの図面を取得します。"""
    drawing = drawing_crud.get(db, id=drawing_id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")
    return drawing


@router.get("/property/{property_id}", response_model=List[DrawingSchema], summary="物件の図面一覧を取得する")
def get_drawings_by_property(
    property_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """指定された物件IDに紐づく図面一覧を取得します。"""
    return drawing_crud.get_by_property(db, property_id=property_id, skip=skip, limit=limit)


@router.patch("/{drawing_id}", response_model=DrawingSchema, summary="図面を更新する")
def update_drawing(
    drawing_id: int,
    drawing_data: DrawingSchema,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """指定されたIDの図面を更新します。"""
    drawing = drawing_crud.get(db, id=drawing_id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")
    return drawing_crud.update(db, db_obj=drawing, obj_in=drawing_data)


@router.delete("/{drawing_id}", response_model=DrawingSchema, summary="図面を削除する")
def delete_drawing(
    drawing_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """指定されたIDの図面を削除します。"""
    drawing = drawing_crud.get(db, id=drawing_id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")
    return drawing_crud.delete(db, id=drawing_id)
