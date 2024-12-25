from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ImageSchema(BaseModel):
    id: int
    url: str
    s3_key: Optional[str] = None
    property_id: Optional[int] = None
    room_id: Optional[int] = None
    product_id: Optional[int] = None
    image_type: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
