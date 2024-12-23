from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from .image_schemas import ImageSchema
from .room_schemas import RoomDetailsSchema


class PropertySchema(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    property_type: str
    prefecture: str
    layout: Optional[str] = None
    construction_year: Optional[int] = None
    construction_month: Optional[int] = None
    site_area: Optional[float] = None
    building_area: Optional[float] = None
    floor_count: Optional[int] = None
    structure: Optional[str] = None
    design_company_id: Optional[int] = None
    construction_company_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 詳細表示用の拡張スキーマ
class PropertyDetailsSchema(PropertySchema):
    rooms: List[RoomDetailsSchema]
    images: List[ImageSchema]
