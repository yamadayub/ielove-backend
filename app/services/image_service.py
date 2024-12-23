from typing import List, Optional, Literal
from sqlalchemy.orm import Session
from app.models import Image
from app.crud.image import image as image_crud
from app.schemas import ImageSchema
from app.utils.s3 import create_presigned_url, delete_s3_object
from app.config import get_settings
import uuid
from fastapi import HTTPException

settings = get_settings()


class ImageService:

    def get_image(self, db: Session, image_id: int) -> Optional[Image]:
        """指定されたIDの画像を取得する"""
        return image_crud.get(db, id=image_id)

    def get_upload_url(self, db: Session, file_name: str, content_type: str):
        """プリサインドURLを生成し、一時的な画像レコードを作成"""
        try:
            unique_id = str(uuid.uuid4())
            key = f"temp/{unique_id}/{file_name}"

            # プリサインドURL生成
            presigned_url = create_presigned_url(bucket=settings.AWS_S3_BUCKET,
                                                 key=key,
                                                 content_type=content_type)

            # 一時的な画像レコード作成
            image_data = ImageSchema(
                url=f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{key}",
                s3_key=key,
                image_type="temp")
            db_image = image_crud.create(db, obj_in=image_data)

            return {
                "upload_url": presigned_url,
                "image_id": db_image.id,
                "image_url": db_image.url
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def delete_image(self, db: Session, image_id: int):
        """画像の削除"""
        try:
            image = image_crud.get(db, id=image_id)
            if not image:
                raise HTTPException(status_code=404, detail="Image not found")

            # S3から画像を削除
            if delete_s3_object(settings.AWS_S3_BUCKET, image.s3_key):
                image_crud.delete(db, id=image_id)
                return {"status": "success"}

            raise HTTPException(status_code=500,
                                detail="Failed to delete image from S3")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def complete_upload(
        self,
        db: Session,
        image_id: int,
        property_id: Optional[int] = None,
        room_id: Optional[int] = None,
        product_id: Optional[int] = None
    ) -> Image:
        """
        画像のアップロードを完了し、指定された各エンティティに関連付けます。

        Args:
            db: データベースセッション
            image_id: 画像ID
            property_id: 物件ID（オプション）
            room_id: 部屋ID（オプション）
            product_id: 製品ID（オプション）

        Returns:
            更新された画像エンティティ
        """
        image = image_crud.get(db, id=image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

        # 各エンティティIDを設定
        update_data = {
            "property_id": property_id,
            "room_id": room_id,
            "product_id": product_id,
            "image_type": "main"  # 一時的なステータスから本番のステータスに変更
        }

        return image_crud.update(db, db_obj=image, obj_in=update_data)

    def get_images(
        self,
        db: Session,
        property_id: Optional[int] = None,
        room_id: Optional[int] = None,
        product_id: Optional[int] = None,
        include_children: bool = True
    ) -> List[Image]:
        """
        指定された条件に基づいて画像を検索します。

        Args:
            db: データベースセッション
            property_id: 物件ID（オプション）
            room_id: 部屋ID（オプション）
            product_id: 製品ID（オプション）
            include_children: 下位階層の画像を含めるか（デフォルト: True）

        Note:
            優先順位: property_id > room_id > product_id
        """
        if not include_children:
            # 指定された階層の画像のみを取得
            return image_crud.get_images(
                db,
                property_id=property_id,
                room_id=room_id,
                product_id=product_id
            )

        # include_children=Trueの場合の処理
        if property_id:
            # 物件に関連する全ての画像を取得
            return image_crud.get_images(db, property_id=property_id)
        elif room_id:
            # 部屋に関連する全ての画像を取得
            return image_crud.get_images(db, room_id=room_id)
        elif product_id:
            # 製品の画像のみを取得
            return image_crud.get_images(db, product_id=product_id)

        return []


image_service = ImageService()
