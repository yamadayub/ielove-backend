from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Literal
import app.schemas as schemas
from app.services.image_service import image_service
from app.database import get_db

router = APIRouter(
    prefix="/images",
    tags=["images"]
)


@router.post("/presigned-url", summary="画像のアップロードURLを取得する")
def get_presigned_url(
    file_data: dict = Body(..., example={
        "file_name": "example.jpg",
        "content_type": "image/jpeg"
    }),
    db: Session = Depends(get_db)
):
    """
    S3へのアップロード用のプリサインドURLを取得します。

    Parameters:
    - file_data: ファイル情報
        - file_name: ファイル名
        - content_type: ファイルのMIMEタイプ
    """
    try:
        file_name = file_data.get("file_name")
        content_type = file_data.get("content_type")

        if not file_name or not content_type:
            raise HTTPException(
                status_code=400,
                detail="file_name and content_type are required"
            )

        return image_service.get_upload_url(db, file_name, content_type)
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(
            status_code=400,
            detail="リクエスト処理中にエラーが発生しました。"
        )


@router.delete("/{image_id}", summary="画像を削除する")
def delete_image(image_id: str, db: Session = Depends(get_db)):
    """指定されたIDの画像を削除する"""
    return image_service.delete_image(db, image_id)


@router.post("/{image_id}/complete", summary="画像のアップロードを完了する")
def complete_image_upload(
    image_id: str,
    property_id: Optional[int] = None,
    room_id: Optional[int] = None,
    product_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    画像のアップロードを完了し、指定された各エンティティに関連付けます。
    一つの画像を複数の階層（物件、部屋、製品）に同時に関連付けることができます。

    Parameters:
    - image_id: 画像ID
    - property_id: 物件ID（オプション）
    - room_id: 部屋ID（オプション）
    - product_id: 製品ID（オプション）
    """
    return image_service.complete_upload(
        db,
        image_id,
        property_id=property_id,
        room_id=room_id,
        product_id=product_id
    )


@router.get("", response_model=List[schemas.ImageSchema], summary="画像一覧を取得する")
def get_images(
    property_id: Optional[int] = None,
    room_id: Optional[int] = None,
    product_id: Optional[int] = None,
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
    - include_children: 下位階層の画像を含めるか（デフォルト: True）

    Note:
    - property_idが指定された場合: 物件、その部屋、製品の画像を取得
    - room_idが指定された場合: 部屋とその製品の画像を取得
    - product_idが指定された場合: 製品の画像のみを取得
    - 複数指定された場合は、より上位の階層（property > room > product）が優先されます
    """
    return image_service.get_images(
        db,
        property_id=property_id,
        room_id=room_id,
        product_id=product_id,
        include_children=include_children
    )


@router.get("/{image_id}", response_model=schemas.ImageSchema, summary="指定されたIDの画像を取得する")
def get_image(image_id: str, db: Session = Depends(get_db)):
    """指定されたIDの画像を取得する"""
    image = image_service.get_image(db, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image
