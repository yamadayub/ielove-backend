from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ProductCategorySchema(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class PurchaseSchema(BaseModel):
    id: Optional[int] = None
    buyer_id: str
    product_for_sale_id: int
    amount: int
    status: str
    stripe_payment_intent_id: Optional[str] = None
    stripe_payment_status: Optional[str] = None
    stripe_transfer_id: Optional[str] = None

    class Config:
        from_attributes = True

class SaleSchema(BaseModel):
    id: Optional[int] = None
    seller_id: int
    product_for_sale_id: int
    purchase_id: int
    amount: int
    platform_fee: int
    seller_amount: int
    status: str
    stripe_transfer_id: Optional[str] = None
    stripe_transfer_status: Optional[str] = None

    class Config:
        from_attributes = True

class ProductForSaleSchema(BaseModel):
    id: Optional[int] = None
    seller_id: int
    name: str
    description: Optional[str] = None
    price: int
    sale_type: Literal["property", "room", "product", "consultation"]
    consultation_type: Optional[str] = None
    status: str = "draft"
    property_id: Optional[int] = None
    room_id: Optional[int] = None
    product_id: Optional[int] = None
    is_negotiable: bool = False
    consultation_minutes: Optional[int] = None

    class Config:
        from_attributes = True

class SellerProfileSchema(BaseModel):
    id: Optional[int] = None
    user_id: str
    company_name: Optional[str] = None
    representative_name: Optional[str] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    business_registration_number: Optional[str] = None
    tax_registration_number: Optional[str] = None
    stripe_account_id: Optional[str] = None
    stripe_account_status: Optional[str] = None
    stripe_account_type: Optional[str] = None
    stripe_onboarding_completed: bool = False
    stripe_charges_enabled: bool = False
    stripe_payouts_enabled: bool = False

    class Config:
        from_attributes = True

class CompanySchema(BaseModel):
    id: Optional[int] = None
    name: str
    company_type: Literal["manufacturer", "design", "construction"]
    description: Optional[str] = None
    website: Optional[str] = None

    class Config:
        from_attributes = True

class ImageSchema(BaseModel):
    id: Optional[int] = None
    url: str
    description: Optional[str]
    image_type: Literal["main", "sub"]
    property_id: Optional[int] = None
    room_id: Optional[int] = None
    product_id: Optional[int] = None

class ProductSpecificationSchema(BaseModel):
    id: Optional[int] = None
    product_id: Optional[int] = None
    spec_type: str
    spec_value: str
    manufacturer_id: Optional[int] = None
    model_number: Optional[str] = None

class ProductDimensionSchema(BaseModel):
    id: Optional[int] = None
    product_id: Optional[int] = None
    dimension_type: str
    value: float
    unit: str

class ProductSchema(BaseModel):
    id: Optional[int] = None
    property_id: Optional[int] = None
    room_id: Optional[int] = None
    product_category_id: int
    manufacturer_id: int
    name: str
    model_number: str
    description: Optional[str] = None
    catalog_url: Optional[str] = None
    specifications: Optional[List[ProductSpecificationSchema]] = []
    dimensions: Optional[List[ProductDimensionSchema]] = []
    images: Optional[List[ImageSchema]] = []

class RoomSchema(BaseModel):
    id: Optional[int] = None
    property_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    products: Optional[List[ProductSchema]] = []
    images: Optional[List[ImageSchema]] = []

class PropertySchema(BaseModel):
    id: Optional[int] = None
    user_id: str
    name: str
    description: Optional[str] = None
    property_type: Literal["house", "apartment", "other"]
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

    class Config:
        from_attributes = True

class PropertyDetailSchema(PropertySchema):
    user: Optional[dict] = None
    design_company: Optional[dict] = None
    construction_company: Optional[dict] = None
    rooms: Optional[List[RoomSchema]] = []
    images: Optional[List[ImageSchema]] = []

    class Config:
        from_attributes = True