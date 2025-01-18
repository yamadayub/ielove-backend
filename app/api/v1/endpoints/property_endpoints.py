from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from typing import List
from app.schemas.property_schemas import (
    PropertySchema,
    PropertyDetailsSchema
)
from app.schemas.user_schemas import UserSchema
from app.services.property_service import property_service
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.services.user_service import user_service
from fastapi import status, Response

router = APIRouter(
    prefix="/properties",
    tags=["properties"]
)


@router.post("", response_model=PropertySchema, summary="物件情報を作成する")
def create_property(
    property_data: PropertySchema,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """物件の基本情報のみを作成する"""
    property_data_dict = property_data.model_dump()
    property_data_dict["user_id"] = current_user.id
    return property_service.create_property(db, PropertySchema(**property_data_dict))


@router.get("", response_model=List[PropertySchema], summary="物件一覧を取得する")
def get_properties(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """物件一覧を取得"""
    return property_service.get_properties(db, skip=skip, limit=limit)


@router.get("/{property_id}", response_model=PropertySchema, summary="指定されたIDの物件情報を取得する")
def get_property(
    property_id: int,
    db: Session = Depends(get_db)
):
    """指定されたIDのproperties tableのデータを取得"""
    property = property_service.get_property(db, property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    return property


@router.get("/{property_id}/is-mine", response_model=bool, summary="指定された物件が自分のものかを確認する")
def is_my_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """
    指定された物件が現在のユーザーのものかを確認する

    Parameters:
    - property_id: 物件ID

    Returns:
    - bool: ユーザーの物件である場合はTrue、そうでない場合はFalse
    """
    return property_service.is_my_property(db, property_id, current_user.id)


@router.get("/{property_id}/details", response_model=PropertyDetailsSchema, summary="物件の詳細情報を取得する")
def get_property_details(
    property_id: int,
    db: Session = Depends(get_db)
):
    """
    物件の詳細情報を、関連する全ての情報（部屋、製品、仕様、寸法、画像）と共に取得します。

    Parameters:
    - property_id: 物件ID

    Returns:
    - 物件の詳細情報（階層構造）
        - 物件情報
        - 物件の画像一覧
        - 部屋一覧
            - 部屋情報
            - 部屋の画像一覧
            - 製品一覧
                - 製品情報
                - 製品の画像一覧
                - 製品仕様一覧
                - 製品寸法一覧
    """
    return property_service.get_property_details(db, property_id)


@router.post("/whole", response_model=int, summary="物件全体の情報を作成する")
def create_property_whole(
    property_data: PropertySchema,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """物件の全情報を作成"""
    property_data_dict = property_data.model_dump()
    property_data_dict["user_id"] = current_user.id
    return property_service.create_property_whole(db, PropertySchema(**property_data_dict))


@router.patch("/{property_id}", response_model=PropertySchema, summary="物件情報を更新する")
async def update_property(
    property_id: int,
    property_data: PropertySchema,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """
    物件情報を更新します。
    - property_id: 更新する物件のID
    - property_data: 更新するデータ（部分的な更新が可能）
    """
    # 所有者チェック
    if not property_service.is_my_property(db, property_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to update this property"
        )
    return await property_service.update_property(db, property_id, property_data)


@router.delete("/{property_id}", response_model=None, summary="物件を削除する")
async def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """指定されたIDの物件を削除します。"""
    return await property_service.delete_property(db, property_id)


@router.get("/by-user/{user_id}", response_model=List[PropertySchema])
def get_properties_by_user(
    user_id: int,
    response: Response,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    property_type: str = None,
    prefecture: str = None
):
    """指定されたユーザーIDの物件一覧を取得"""
    filters = {}
    if property_type:
        filters["property_type"] = property_type
    if prefecture:
        filters["prefecture"] = prefecture

    items, total = property_service.get_properties_by_user(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit,
        filters=filters
    )

    response.headers["X-Total-Count"] = str(total)
    return items

# ... 他の物件関連エンドポイント
