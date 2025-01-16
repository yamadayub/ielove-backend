from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.room_schemas import (
    RoomSchema,
    RoomDetailsSchema
)
from app.schemas.user_schemas import UserSchema
from app.services.room_service import room_service
from app.database import get_db
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/rooms",
    tags=["rooms"]
)


@router.post("", response_model=RoomSchema, summary="部屋情報を作成する")
def create_room(
    room_data: RoomSchema,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """物件に紐づく部屋情報を作成する"""
    return room_service.create_room(db, room_data)


@router.get("", response_model=List[RoomSchema], summary="部屋情報（複数）を取得する")
def get_rooms(
    property_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """指定された物件の部屋一覧を取得"""
    return room_service.get_rooms(db, property_id=property_id, skip=skip, limit=limit)


@router.get("/{room_id}", response_model=RoomSchema, summary="部屋情報を取得する")
def get_room(room_id: int, db: Session = Depends(get_db)):
    """指定されたIDの部屋を取得"""
    room = room_service.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.get("/{room_id}/is-mine", response_model=bool, summary="指定された部屋が自分の物件に属しているかを確認する")
def is_my_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """
    指定された部屋が現在のユーザーの物件に属しているかを確認する

    Parameters:
    - room_id: 部屋ID

    Returns:
    - bool: ユーザーの物件に属する部屋である場合はTrue、そうでない場合はFalse
    """
    return room_service.is_my_room(db, room_id, current_user.id)


@router.patch("/{room_id}", response_model=RoomSchema, summary="部屋情報を更新する")
async def update_room(
    room_id: int,
    room_data: RoomSchema,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """指定されたIDの部屋情報を更新する"""
    return await room_service.update_room(db, room_id, room_data)


@router.delete("/{room_id}", response_model=None, summary="部屋を削除する")
async def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """指定されたIDの部屋を削除する"""
    return await room_service.delete_room(db, room_id)


@router.get("/{room_id}/details", response_model=RoomDetailsSchema, summary="部屋の詳細情報を取得する")
def get_room_details(
    room_id: int,
    db: Session = Depends(get_db)
):
    """
    部屋の詳細情報を、関連する全ての情報（製品、仕様、寸法、画像）と共に取得します。
    また、部屋が属する物件の基本情報も含みます。

    Parameters:
    - room_id: 部屋ID

    Returns:
    - 部屋の詳細情報（階層構造）
        - 部屋情報
        - 部屋の画像一覧
        - 製品一覧
            - 製品情報
            - 製品の画像一覧
            - 製品仕様一覧
            - 製品寸法一覧
        - 物件の基本情報
    """
    return room_service.get_room_details(db, room_id)
