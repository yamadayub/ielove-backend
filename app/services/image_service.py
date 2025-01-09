from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Image
from app.crud.image import image as image_crud
from app.schemas.image_schemas import (
    ImageSchema,
    CreatePresignedUrlRequest,
    CreatePresignedUrlResponse,
    ImageMetadata,
    ImageStatus,
    ImageType
)
from app.utils.s3 import create_presigned_url, delete_s3_object
from app.config import get_settings
import uuid
from fastapi import HTTPException

settings = get_settings()


class ImageService:
    def get_upload_url(self, db: Session, request: CreatePresignedUrlRequest) -> CreatePresignedUrlResponse:
        """プリサインドURLを生成し、一時的な画像レコードを作成"""
        try:
            unique_id = str(uuid.uuid4())
            key = f"temp/{unique_id}/{request.file_name}"

            # プリサインドURL生成
            presigned_url = create_presigned_url(
                bucket=settings.AWS_S3_BUCKET,
                key=key,
                content_type=request.content_type
            )

            # 画像レコード作成
            image_data = ImageSchema(
                url=f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{key}",
                s3_key=key,
                property_id=request.property_id,
                room_id=request.room_id,
                product_id=request.product_id,
                image_type=request.image_type,
                status=ImageStatus.PENDING
            )
            db_image = image_crud.create(db, obj_in=image_data)

            # レスポンス作成
            metadata = ImageMetadata(
                property_id=db_image.property_id,
                room_id=db_image.room_id,
                product_id=db_image.product_id,
                status=ImageStatus.PENDING,
                image_type=db_image.image_type
            )

            return CreatePresignedUrlResponse(
                upload_url=presigned_url,
                image_id=db_image.id,
                image_url=db_image.url,
                image_metadata=metadata
            )

        except Exception as e:
            print(f"Error: {e}")
            raise HTTPException(
                status_code=400,
                detail="プリサインドURL生成中にエラーが発生しました。"
            )

    def update_image_status(self, db: Session, image_id: int, status: ImageStatus) -> Image:
        """画像のステータスを更新"""
        image = image_crud.get(db, id=image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

        update_data = ImageSchema(
            id=image.id,
            url=image.url,
            s3_key=image.s3_key,
            property_id=image.property_id,
            room_id=image.room_id,
            product_id=image.product_id,
            image_type=image.image_type,
            status=status,
            created_at=image.created_at
        )

        return image_crud.update(db, db_obj=image, obj_in=update_data)

    def get_image(self, db: Session, image_id: int) -> Optional[Image]:
        """指定されたIDの画像を取得する"""
        return image_crud.get(db, id=image_id)

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

            raise HTTPException(
                status_code=500,
                detail="Failed to delete image from S3"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

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

    def set_as_main_image(self, db: Session, image_id: int, property_id: Optional[int] = None, room_id: Optional[int] = None, product_id: Optional[int] = None) -> Image:
        """指定された画像をメイン画像に設定し、既存のメイン画像をサブに変更する"""
        # 対象の画像を取得
        image = image_crud.get(db, id=image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

        # 画像が指定されたエンティティに紐づいているか確認
        if property_id and image.property_id != property_id:
            raise HTTPException(
                status_code=400, detail="Image does not belong to the specified property")
        if room_id and image.room_id != room_id:
            raise HTTPException(
                status_code=400, detail="Image does not belong to the specified room")
        if product_id and image.product_id != product_id:
            raise HTTPException(
                status_code=400, detail="Image does not belong to the specified product")

        try:
            # 現在のメイン画像をサブに変更
            current_main = None
            if property_id:
                current_main = db.query(Image).filter(
                    Image.property_id == property_id,
                    Image.image_type == ImageType.MAIN
                ).first()
            elif room_id:
                current_main = db.query(Image).filter(
                    Image.room_id == room_id,
                    Image.image_type == ImageType.MAIN
                ).first()
            elif product_id:
                current_main = db.query(Image).filter(
                    Image.product_id == product_id,
                    Image.image_type == ImageType.MAIN
                ).first()

            if current_main:
                current_main.image_type = ImageType.SUB

            # 指定された画像をメインに設定
            image.image_type = ImageType.MAIN

            db.commit()
            db.refresh(image)
            return image

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    def update_image_type(self, db: Session, image_id: int, image_type: ImageType) -> Image:
        """画像のタイプを更新する"""
        image = image_crud.get(db, id=image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

        try:
            # 画像タイプを更新
            update_data = ImageSchema(
                id=image.id,
                url=image.url,
                s3_key=image.s3_key,
                property_id=image.property_id,
                room_id=image.room_id,
                product_id=image.product_id,
                image_type=image_type,
                status=image.status,
                created_at=image.created_at
            )

            updated_image = image_crud.update(
                db, db_obj=image, obj_in=update_data)
            return updated_image

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))


image_service = ImageService()
