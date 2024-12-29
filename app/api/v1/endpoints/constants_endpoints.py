from fastapi import APIRouter
from typing import Dict, List
from app.enums import (
    CompanyType,
    PropertyType,
    StructureType,
    DimensionType,
    ImageType,
    ListingType,
    ListingStatus,
    Visibility
)

router = APIRouter(
    prefix="/constants",
    tags=["constants"]
)


@router.get("")
def get_constants() -> Dict[str, List[Dict[str, str]]]:
    """全ての定数の選択肢を取得"""
    return {
        "company_types": CompanyType.get_labels(),
        "property_types": PropertyType.get_labels(),
        "structure_types": StructureType.get_labels(),
        "dimension_types": DimensionType.get_labels(),
        "image_types": ImageType.get_labels(),
        "listing_types": ListingType.get_labels(),
        "listing_statuses": ListingStatus.get_labels(),
        "visibility_types": Visibility.get_labels()
    }
