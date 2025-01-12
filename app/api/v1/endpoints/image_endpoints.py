from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.image_schemas import (
    ImageSchema,
    CreatePresignedUrlRequest,
    CreatePresignedUrlResponse,
    ImageStatus,
    ImageType
)
from app.services.image_service import image_service
from app.database import get_db

router = APIRouter(
    prefix="/images",
    tags=["images"]
)


@router.post("/presigned-url", response_model=CreatePresignedUrlResponse, summary="画像のアップロードURLを取得する")
def get_presigned_url(
    request: CreatePresignedUrlRequest,
    db: Session = Depends(get_db)
):
    """
    S3へのアップロード用のプリサインドURLを取得します。
    画像のメタデータも同時に作成されます。

    Parameters:
    - request: プリサインドURL生成リクエスト
        - file_name: ファイル名
        - content_type: ファイルのMIMEタイプ
        - property_id: 物件ID（オプション）
        - room_id: 部屋ID（オプション）
        - product_id: 製品ID（オプション）
        - image_type: 画像タイプ（main/sub/temp）
    """
    return image_service.create_presigned_url(db, request)


@router.patch("/{image_id}/status", response_model=ImageSchema, summary="画像のステータスを更新する")
def update_image_status(
    image_id: int,
    status_data: dict = Body(..., example={"status": "completed"}),
    db: Session = Depends(get_db)
):
    """
    画像のステータスを更新します。
    S3へのアップロード完了後に呼び出されることを想定しています。

    Parameters:
    - image_id: 画像ID
    - status_data: 新しいステータス情報
    """
    status = ImageStatus(status_data["status"])
    return image_service.update_image_status(db, image_id, status)


@router.delete("/{image_id}", summary="画像を削除する")
def delete_image(image_id: int, db: Session = Depends(get_db)):
    """指定されたIDの画像を削除する"""
    return image_service.delete_image(db, image_id)


@router.get("", response_model=List[ImageSchema], summary="画像一覧を取得する")
def get_images(
    property_id: Optional[int] = None,
    room_id: Optional[int] = None,
    product_id: Optional[int] = None,
    product_specification_id: Optional[int] = None,
    include_children: bool = True,
    db: Session = Depends(get_db)
):
    """
    指定されたエンティティに関連する画像一覧を取得します。
    より上位の階層が指定された場合、下位の階層の画像も含めて取得できます。

    Parameters:
    - property_id: 物件ID（オプション）
    - room_id: 部屋ID（オプション）
    - product_id: 製品ID（オプション）
    - product_specification_id: 製品仕様ID（オプション）
    - include_children: 下位階層の画像を含めるか（デフォルト: True）

    Note:
    - property_idが指定された場合: 物件、その部屋、製品、製品仕様の画像を取得
    - room_idが指定された場合: 部屋とその製品、製品仕様の画像を取得
    - product_idが指定された場合: 製品とその製品仕様の画像を取得
    - product_specification_idが指定された場合: 製品仕様の画像のみを取得
    - 複数指定された場合は、より上位の階層（property > room > product > product_specification）が優先されます
    """
    return image_service.get_images(
        db,
        property_id=property_id,
        room_id=room_id,
        product_id=product_id,
        product_specification_id=product_specification_id,
        include_children=include_children
    )


@router.get("/{image_id}", response_model=ImageSchema, summary="指定されたIDの画像を取得する")
def get_image(image_id: int, db: Session = Depends(get_db)):
    """指定されたIDの画像を取得する"""
    image = image_service.get_image(db, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@router.patch("/{image_id}/set-main", response_model=ImageSchema, summary="画像をメインに設定する")
def set_as_main_image(
    image_id: int,
    property_id: Optional[int] = None,
    room_id: Optional[int] = None,
    product_id: Optional[int] = None,
    product_specification_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    指定された画像をメイン画像として設定します。
    既存のメイン画像がある場合は、自動的にサブ画像に変更されます。
    property_id, room_id, product_id, product_specification_idのいずれか1つを指定する必要があります。

    Parameters:
    - image_id: 画像ID
    - property_id: 物件ID（オプション）
    - room_id: 部屋ID（オプション）
    - product_id: 製品ID（オプション）
    - product_specification_id: 製品仕様ID（オプション）
    """
    if sum(1 for x in [property_id, room_id, product_id, product_specification_id] if x is not None) != 1:
        raise HTTPException(
            status_code=400,
            detail="Exactly one of property_id, room_id, product_id, or product_specification_id must be specified"
        )

    return image_service.set_as_main_image(
        db,
        image_id=image_id,
        property_id=property_id,
        room_id=room_id,
        product_id=product_id,
        product_specification_id=product_specification_id
    )


@router.patch("/{image_id}/type", response_model=ImageSchema, summary="画像タイプを更新する")
def update_image_type(
    image_id: int,
    image_type: ImageType = Body(..., example={"image_type": "SUB"}),
    db: Session = Depends(get_db)
):
    """
    画像のタイプを更新します。

    Parameters:
    - image_id: 画像ID
    - image_type: 新しい画像タイプ（MAIN/SUB/PAID）
    """
    return image_service.update_image_type(db, image_id, image_type)
