from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal
from enum import Enum


class ImageStatus(str, Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'


class ImageType(str, Enum):
    MAIN = 'main'
    SUB = 'sub'
    TEMP = 'temp'


class CreatePresignedUrlRequest(BaseModel):
    file_name: str
    content_type: str
    property_id: Optional[int] = None
    room_id: Optional[int] = None
    product_id: Optional[int] = None
    image_type: ImageType = ImageType.TEMP
    description: Optional[str] = None


class ImageMetadata(BaseModel):
    property_id: Optional[int] = None
    room_id: Optional[int] = None
    product_id: Optional[int] = None
    status: ImageStatus
    image_type: ImageType
    description: Optional[str] = None


class CreatePresignedUrlResponse(BaseModel):
    upload_url: str
    image_id: int
    image_url: str
    image_metadata: ImageMetadata


class ImageSchema(BaseModel):
    id: Optional[int] = None
    url: Optional[str] = None
    description: Optional[str] = None
    s3_key: Optional[str] = None
    property_id: Optional[int] = None
    room_id: Optional[int] = None
    product_id: Optional[int] = None
    image_type: ImageType = ImageType.TEMP
    status: ImageStatus = ImageStatus.PENDING
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
