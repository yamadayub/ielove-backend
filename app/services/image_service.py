from typing import Optional
from sqlalchemy.orm import Session
from app.crud.image import image as image_crud
from app.schemas import ImageCreate, ImageSchema
from app.utils.s3 import create_presigned_url, delete_s3_object
from app.config import get_settings
import uuid
from fastapi import HTTPException

settings = get_settings()


class ImageService:

    def get_upload_url(self, db: Session, file_name: str, content_type: str):
        """プリサインドURLを生成し、一時的な画像レコードを作成"""
        try:
            image_id = str(uuid.uuid4())
            key = f"temp/{image_id}/{file_name}"

            # プリサインドURL生成
            presigned_url = create_presigned_url(bucket=settings.AWS_S3_BUCKET,
                                                 key=key,
                                                 content_type=content_type)

            # 一時的な画像レコード作成
            image_data = ImageCreate(
                id=image_id,
                url=
                f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{key}",
                s3_key=key,
                image_type="temp")
            image_crud.create(db, obj_in=image_data)

            return {
                "upload_url": presigned_url,
                "image_id": image_id,
                "image_url": image_data.url
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def delete_image(self, db: Session, image_id: str):
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

    def complete_upload(self,
                        db: Session,
                        image_id: str,
                        entity_type: Optional[str] = None,
                        entity_id: Optional[int] = None):
        """画像アップロードの完了処理"""
        try:
            image = image_crud.get(db, id=image_id)
            if not image:
                raise HTTPException(status_code=404, detail="Image not found")

            if entity_type and entity_id:
                update_data = {
                    "image_type": "main",
                    f"{entity_type}_id": entity_id
                }

                # S3での移動処理
                new_key = f"{entity_type}s/{entity_id}/{image_id}"
                s3_client.copy_object(
                    Bucket=settings.AWS_S3_BUCKET,
                    CopySource=f"{settings.AWS_S3_BUCKET}/{image.s3_key}",
                    Key=new_key)
                delete_s3_object(settings.AWS_S3_BUCKET, image.s3_key)

                update_data["s3_key"] = new_key
                update_data[
                    "url"] = f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{new_key}"

                image = image_crud.update(db, db_obj=image, obj_in=update_data)

            return image
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


image_service = ImageService()
