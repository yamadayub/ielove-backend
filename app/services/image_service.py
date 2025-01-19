from typing import List, Optional, Dict, Tuple
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
import boto3

settings = get_settings()


class ImageService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

    def create_presigned_url(
        self,
        db: Session,
        request: CreatePresignedUrlRequest
    ) -> CreatePresignedUrlResponse:
        """
        画像アップロード用の署名付きURLを生成し、画像メタデータを作成する

        Parameters:
        - db: データベースセッション
        - request: プリサインドURL生成リクエスト

        Returns:
        - CreatePresignedUrlResponse: 署名付きURLとメタデータを含むレスポンス

        Raises:
        - HTTPException: S3の操作やデータベースの操作が失敗した場合
        """
        try:
            # S3メタデータの作成
            metadata = {
                'property_id': str(request.property_id) if request.property_id else '',
                'room_id': str(request.room_id) if request.room_id else '',
                'product_id': str(request.product_id) if request.product_id else '',
                'product_specification_id': str(request.product_specification_id) if request.product_specification_id else '',
                'drawing_id': str(request.drawing_id) if request.drawing_id else '',
                'image_type': request.image_type.value if request.image_type else ImageType.SUB.value,
                'description': request.description if request.description else ''
            }

            # S3キーの生成
            key = f"uploads/{uuid.uuid4()}/{request.file_name}"

            # S3パラメータの設定
            params = {
                'Bucket': settings.AWS_S3_BUCKET,
                'Key': key,
                'ContentType': request.content_type,
                'Metadata': metadata
            }

            try:
                # プリサインドURLの生成
                upload_url = self.s3_client.generate_presigned_url(
                    'put_object',
                    Params=params,
                    ExpiresIn=3600
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to generate presigned URL: {str(e)}"
                )

            # 画像URLの生成
            image_url = f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"

            try:
                # 画像レコードの作成
                image = image_crud.create(
                    db,
                    obj_in=ImageSchema(
                        url=image_url,
                        s3_key=key,
                        property_id=request.property_id,
                        room_id=request.room_id,
                        product_id=request.product_id,
                        product_specification_id=request.product_specification_id,
                        drawing_id=request.drawing_id,
                        image_type=request.image_type or ImageType.SUB,
                        description=request.description,
                        status=ImageStatus.PENDING
                    )
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to create image record: {str(e)}"
                )

            # ImageMetadataの作成
            image_metadata = ImageMetadata(
                property_id=request.property_id,
                room_id=request.room_id,
                product_id=request.product_id,
                product_specification_id=request.product_specification_id,
                image_type=request.image_type or ImageType.SUB,
                description=request.description,
                status=ImageStatus.PENDING
            )

            # レスポンスの作成と返却
            return CreatePresignedUrlResponse(
                upload_url=upload_url,
                image_id=image.id,
                image_url=image_url,
                image_metadata=image_metadata
            )

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process image upload request: {str(e)}"
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
        product_specification_id: Optional[int] = None,
        drawing_id: Optional[int] = None,
        include_children: bool = True
    ) -> List[Image]:
        """
        指定された条件に基づいて画像を検索します。

        Args:
            db: データベースセッション
            property_id: 物件ID（オプション）
            room_id: 部屋ID（オプション）
            product_id: 製品ID（オプション）
            product_specification_id: 製品仕様ID（オプション）
            drawing_id: 図面ID（オプション）
            include_children: 下位階層の画像を含めるか（デフォルト: True）

        Note:
            drawing_idが指定された場合は、他のパラメータに関係なく図面の画像のみを返します。
            property_idが指定された場合は、そのプロパティに紐づく全ての画像（図面の画像含む）を返します。
            それ以外の場合は以下の優先順位で処理します：
            room_id > product_id > product_specification_id
        """
        # drawing_idが指定された場合は、他のパラメータに関係なく図面の画像のみを返す
        if drawing_id is not None:
            return image_crud.get_images(db, drawing_id=drawing_id)

        if not include_children:
            # 指定された階層の画像のみを取得（drawing以外）
            return image_crud.get_images(
                db,
                property_id=property_id,
                room_id=room_id,
                product_id=product_id,
                product_specification_id=product_specification_id
            )

        # include_children=Trueの場合の処理
        if property_id:
            # 物件に関連する全ての画像を取得（drawing以外）
            return image_crud.get_images(db, property_id=property_id)
        elif room_id:
            # 部屋に関連する全ての画像を取得
            return image_crud.get_images(db, room_id=room_id)
        elif product_id:
            # 製品の画像のみを取得
            return image_crud.get_images(db, product_id=product_id)
        elif product_specification_id:
            # 製品仕様の画像のみを取得
            return image_crud.get_images(db, product_specification_id=product_specification_id)

        return []

    def set_as_main_image(
        self,
        db: Session,
        image_id: int,
        property_id: Optional[int] = None,
        room_id: Optional[int] = None,
        product_id: Optional[int] = None,
        product_specification_id: Optional[int] = None
    ) -> Image:
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
        if product_specification_id and image.product_specification_id != product_specification_id:
            raise HTTPException(
                status_code=400, detail="Image does not belong to the specified product specification")

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
            elif product_specification_id:
                current_main = db.query(Image).filter(
                    Image.product_specification_id == product_specification_id,
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
