from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, model_validator
from datetime import datetime
from app.schemas.image_schemas import ImageSchema


class UserSchema(BaseModel):
    id: int
    clerk_user_id: str
    email: str
    name: str
    user_type: Literal["individual", "business"]
    role: str = "buyer"
    is_active: bool = True
    last_sign_in: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProductCategorySchema(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class CompanySchema(BaseModel):
    id: Optional[int] = None
    name: str
    company_type: Literal["manufacturer", "design", "construction"]
    description: Optional[str] = None
    website: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PurchaseSchema(BaseModel):
    id: Optional[int] = None
    buyer_id: int
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
    user_id: int
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


class ProductSpecificationSchema(BaseModel):
    id: Optional[int] = None
    product_id: Optional[int] = None
    spec_type: str
    spec_value: str
    manufacturer_id: Optional[int] = None
    model_number: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=()
    )


class ProductDimensionSchema(BaseModel):
    id: Optional[int] = None
    product_id: Optional[int] = None
    dimension_type: str
    value: float
    unit: str


class ProductBase(BaseModel):
    id: Optional[int] = None
    property_id: Optional[int] = None
    room_id: Optional[int] = None
    product_category_id: int
    manufacturer_id: Optional[int] = None
    name: str
    product_code: str
    description: Optional[str] = None
    catalog_url: Optional[str] = None


class ProductCreate(ProductBase):
    room_id: int


class ProductSchema(BaseModel):
    id: Optional[int] = None
    room_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    product_category_id: Optional[int] = None
    manufacturer_name: Optional[str] = None
    product_code: Optional[str] = None
    catalog_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: Optional[str] = None
    is_deleted: Optional[bool] = None
    specifications: Optional[List["ProductSpecificationSchema"]] = None
    dimensions: Optional[List["ProductDimensionSchema"]] = None
    images: Optional[List["ImageSchema"]] = None

    class Config:
        from_attributes = True


class ProductDetailSchema(ProductSchema):
    specifications: List[ProductSpecificationSchema] = []
    dimensions: List[ProductDimensionSchema] = []

    model_config = ConfigDict(from_attributes=True)


class RoomBase(BaseModel):
    id: Optional[int] = None
    property_id: Optional[int] = None
    name: str
    description: Optional[str] = None


class RoomCreate(RoomBase):
    property_id: int


class RoomSchema(BaseModel):
    id: Optional[int] = None
    property_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: Optional[str] = None
    is_deleted: Optional[bool] = None
    products: Optional[List["ProductSchema"]] = None
    images: Optional[List["ImageSchema"]] = None

    class Config:
        from_attributes = True


class RoomDetailSchema(RoomBase):
    products: List[ProductSchema] = []
    images: List[ImageSchema] = []


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
    design_company: Optional[str] = None
    construction_company: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: Optional[str] = None
    is_deleted: Optional[bool] = None
    rooms: Optional[List["RoomSchema"]] = None
    images: Optional[List["ImageSchema"]] = None

    class Config:
        from_attributes = True


class PropertyDetailSchema(PropertySchema):
    user: Optional[dict] = None
    design_company: Optional[dict] = None
    construction_company: Optional[dict] = None
    rooms: Optional[List[RoomSchema]] = []
    images: Optional[List[ImageSchema]] = []

    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True)


class PropertyCreateBaseSchema(BaseModel):
    user_id: int
    name: str
    description: Optional[str] = None
    property_type: Literal["HOUSE", "APARTMENT", "OTHER"]
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


class PropertyCreateSchema(BaseModel):
    user_id: int
    name: str
    description: Optional[str] = None
    property_type: Literal["HOUSE", "APARTMENT", "OTHER"]
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
    rooms: Optional[List[RoomSchema]] = []
    images: Optional[List[ImageSchema]] = []


class PreSignedUrlResponse(BaseModel):
    upload_url: str
    image_id: str
    image_url: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    user_type: Optional[Literal["individual", "business"]] = None
    role: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SellerProfileCreate(BaseModel):
    company_name: Optional[str] = None
    representative_name: Optional[str] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    business_registration_number: Optional[str] = None
    tax_registration_number: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SellerProfileUpdate(SellerProfileCreate):
    pass


class UserCreate(BaseModel):
    clerk_user_id: str
    email: str
    name: str
    user_type: Literal["individual", "business"]
    role: str = "buyer"
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class PropertyUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    property_type: Optional[Literal["HOUSE", "APARTMENT", "OTHER"]] = None
    prefecture: Optional[str] = None
    layout: Optional[str] = None
    construction_year: Optional[int] = None
    construction_month: Optional[int] = None
    site_area: Optional[float] = None
    building_area: Optional[float] = None
    floor_count: Optional[int] = None
    structure: Optional[str] = None
    design_company_id: Optional[int] = None
    construction_company_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ProductSpecificationsUpdateSchema(BaseModel):
    specifications: List[ProductSpecificationSchema]

    model_config = ConfigDict(from_attributes=True)


class ProductDimensionsUpdateSchema(BaseModel):
    dimensions: List[ProductDimensionSchema]

    model_config = ConfigDict(from_attributes=True)
