from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, Boolean, JSON, Enum, Index, Numeric, Sequence
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.enums import (
    CompanyType,
    PropertyType,
    StructureType,
    DimensionType,
    ImageType,
    ListingType,
    ListingStatus,
    Visibility,
    TransactionStatus,
    PaymentStatus,
    TransferStatus,
    ChangeType,
    ErrorType
)


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, Sequence('companies_id_seq'), primary_key=True)
    name = Column(String, nullable=False)
    company_type = Column(Enum(CompanyType), nullable=False)
    description = Column(Text)
    website = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, Sequence('properties_id_seq'), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    property_type = Column(Enum(PropertyType), nullable=False)
    prefecture = Column(String, nullable=False)
    layout = Column(String)
    construction_year = Column(Integer)
    construction_month = Column(Integer)
    site_area = Column(Float)
    building_area = Column(Float)
    floor_count = Column(Integer)
    structure = Column(Enum(StructureType))
    design_company = Column(String, nullable=True)
    construction_company = Column(String, nullable=True)
    status = Column(String, nullable=False, default='default')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="properties")
    rooms = relationship("Room", back_populates="property",
                         cascade="all, delete-orphan")
    images = relationship("Image", back_populates="property",
                          cascade="all, delete-orphan")
    drawings = relationship("Drawing", back_populates="property",
                            cascade="all, delete-orphan")
    listings = relationship("ListingItem", back_populates="property")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, Sequence('rooms_id_seq'), primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, nullable=False, default='default')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False)

    property = relationship("Property", back_populates="rooms")
    products = relationship("Product",
                            back_populates="room",
                            cascade="all, delete-orphan")
    images = relationship("Image",
                          back_populates="room",
                          cascade="all, delete-orphan")
    listings = relationship("ListingItem", back_populates="room")


class ProductCategory(Base):
    __tablename__ = "product_categories"

    id = Column(Integer, Sequence(
        'product_categories_id_seq', cycle=True), primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    products = relationship("Product", back_populates="product_category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, Sequence('products_id_seq'), primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    product_category_id = Column(Integer,
                                 ForeignKey("product_categories.id"),
                                 nullable=True)
    manufacturer_name = Column(String, nullable=True)
    name = Column(String, nullable=False)
    product_code = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    catalog_url = Column(String, nullable=True)
    status = Column(String, nullable=False, default='default')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False)

    room = relationship("Room", back_populates="products")
    product_category = relationship("ProductCategory",
                                    back_populates="products")
    specifications = relationship("ProductSpecification",
                                  back_populates="product",
                                  cascade="all, delete-orphan")
    dimensions = relationship("ProductDimension",
                              back_populates="product",
                              cascade="all, delete-orphan")
    images = relationship("Image",
                          back_populates="product",
                          cascade="all, delete-orphan")
    listings = relationship("ListingItem", back_populates="product")


class ProductSpecification(Base):
    __tablename__ = "product_specifications"

    id = Column(Integer, Sequence(
        'product_specifications_id_seq'), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    spec_type = Column(String, nullable=False)
    spec_value = Column(String, nullable=False)
    manufacturer_id = Column(Integer,
                             ForeignKey("companies.id"),
                             nullable=True)
    model_number = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="specifications")
    manufacturer = relationship("Company")
    images = relationship(
        "Image", back_populates="product_specification", cascade="all, delete-orphan")


class ProductDimension(Base):
    __tablename__ = "product_dimensions"

    id = Column(Integer, Sequence(
        'product_dimensions_id_seq'), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    dimension_type = Column(String, nullable=True)
    value = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="dimensions")


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, Sequence('images_id_seq'),
                primary_key=True, index=True)
    url = Column(String, nullable=False)
    description = Column(Text)
    s3_key = Column(String, nullable=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    drawing_id = Column(Integer, ForeignKey("drawings.id"), nullable=True)
    product_specification_id = Column(Integer, ForeignKey(
        "product_specifications.id", ondelete="CASCADE"), nullable=True)
    image_type = Column(Enum(ImageType), nullable=True)
    status = Column(String, nullable=False, default='pending')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    property = relationship("Property", back_populates="images")
    room = relationship("Room", back_populates="images")
    product = relationship("Product", back_populates="images")
    drawing = relationship("Drawing", back_populates="images")
    product_specification = relationship(
        "ProductSpecification", back_populates="images")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, Sequence('users_id_seq'), primary_key=True)
    clerk_user_id = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    user_type = Column(String, nullable=False)  # individual, business
    # buyer, seller, both
    role = Column(String, nullable=False, default='buyer')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_sign_in = Column(DateTime(timezone=True))

    properties = relationship("Property", back_populates="user")
    seller_profile = relationship(
        "SellerProfile", back_populates="user", uselist=False)
    buyer_profile = relationship(
        "BuyerProfile", back_populates="user", uselist=False)
    take_rates = relationship(
        "TakeRate", foreign_keys="[TakeRate.user_id]", back_populates="user")


class BuyerProfile(Base):
    __tablename__ = "buyer_profiles"
    __table_args__ = (
        Index('ix_buyer_profiles_stripe_customer_id',
              'stripe_customer_id', unique=True),
    )

    id = Column(Integer, Sequence('buyer_profiles_id_seq'), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"),
                     unique=True, nullable=False)

    # Stripe関連フィールド
    stripe_customer_id = Column(String, unique=True, nullable=True)
    default_payment_method_id = Column(String, nullable=True)
    has_saved_payment_method = Column(Boolean, default=False)
    last_payment_method_type = Column(String, nullable=True)

    # 配送先情報
    shipping_postal_code = Column(String, nullable=True)
    shipping_prefecture = Column(String, nullable=True)
    shipping_city = Column(String, nullable=True)
    shipping_address1 = Column(String, nullable=True)
    shipping_address2 = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="buyer_profile")
    saved_payment_methods = relationship(
        "SavedPaymentMethod", back_populates="buyer_profile", cascade="all, delete-orphan")
    transactions = relationship(
        "Transaction", back_populates="buyer", foreign_keys="[Transaction.buyer_id]")


class SavedPaymentMethod(Base):
    __tablename__ = "saved_payment_methods"
    __table_args__ = (
        Index('ix_saved_payment_methods_buyer_default',
              'buyer_profile_id', 'is_default'),
        Index('ix_saved_payment_methods_active_type',
              'is_active', 'payment_type'),
    )

    id = Column(Integer, Sequence(
        'saved_payment_methods_id_seq'), primary_key=True)
    buyer_profile_id = Column(Integer, ForeignKey(
        "buyer_profiles.id"), nullable=False)

    # Stripe Payment Method情報
    payment_method_id = Column(String, unique=True, nullable=False)
    payment_type = Column(String, nullable=False)  # card, bank_transfer等

    # クレジットカード情報（最小限）
    card_brand = Column(String, nullable=True)  # visa, mastercard等
    card_last4 = Column(String, nullable=True)
    card_exp_month = Column(Integer, nullable=True)
    card_exp_year = Column(Integer, nullable=True)

    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    buyer_profile = relationship(
        "BuyerProfile", back_populates="saved_payment_methods")


class SellerProfile(Base):
    __tablename__ = "seller_profiles"

    id = Column(Integer, Sequence('seller_profiles_id_seq'), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Stripe関連フィールド
    stripe_account_id = Column(String, unique=True, nullable=True)
    stripe_account_status = Column(String, nullable=True, default="pending")
    stripe_account_type = Column(String, nullable=True, default="standard")
    stripe_onboarding_completed = Column(Boolean, default=False)
    stripe_charges_enabled = Column(Boolean, default=False)
    stripe_payouts_enabled = Column(Boolean, default=False)
    stripe_capabilities = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="seller_profile")
    listings = relationship("ListingItem", back_populates="seller")
    transactions = relationship(
        "Transaction", back_populates="seller", foreign_keys="[Transaction.seller_id]")


class ListingItem(Base):
    __tablename__ = "listing_items"
    __table_args__ = (
        Index('ix_listing_items_status_visibility', 'status', 'visibility'),
        Index('ix_listing_items_price', 'price'),
        Index('ix_listing_items_seller_created', 'seller_id', 'created_at'),
        Index('ix_listing_items_property_status', 'property_id', 'status'),
        Index('ix_listing_items_room_status', 'room_id', 'status'),
        Index('ix_listing_items_product_status', 'product_id', 'status'),
    )

    id = Column(Integer, Sequence('listing_items_id_seq'), primary_key=True)
    seller_id = Column(Integer, ForeignKey(
        "seller_profiles.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Integer, nullable=False)
    listing_type = Column(Enum(ListingType), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    is_negotiable = Column(Boolean, default=False)
    service_type = Column(String, nullable=True)
    service_duration = Column(Integer, nullable=True)
    is_featured = Column(Boolean, default=False)
    visibility = Column(Enum(Visibility), default=Visibility.PUBLIC)
    status = Column(Enum(ListingStatus), default=ListingStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)

    seller = relationship("SellerProfile", back_populates="listings")
    property = relationship("Property", back_populates="listings")
    room = relationship("Room", back_populates="listings")
    product = relationship("Product", back_populates="listings")
    transactions = relationship("Transaction", back_populates="listing")


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        Index('ix_transactions_created_at', 'created_at'),
        Index('ix_transactions_transaction_status', 'transaction_status'),
        Index('ix_transactions_payment_transfer_status',
              'payment_status', 'transfer_status'),
        Index('ix_transactions_buyer_created', 'buyer_id', 'created_at'),
        Index('ix_transactions_seller_created', 'seller_id', 'created_at'),
    )

    id = Column(Integer, Sequence('transactions_id_seq'), primary_key=True)
    buyer_id = Column(Integer, ForeignKey("buyer_profiles.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey(
        "seller_profiles.id"), nullable=False)
    listing_id = Column(Integer, ForeignKey(
        "listing_items.id"), nullable=False)
    session_id = Column(String, nullable=True)
    payment_intent_id = Column(String, nullable=True)
    charge_id = Column(String, nullable=True)
    stripe_transfer_id = Column(String, nullable=True)
    total_amount = Column(Integer, nullable=False)
    platform_fee = Column(Integer, nullable=False)
    seller_amount = Column(Integer, nullable=False)
    transaction_status = Column(
        Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    payment_status = Column(Enum(PaymentStatus),
                            nullable=False, default=PaymentStatus.PENDING)
    transfer_status = Column(Enum(TransferStatus),
                             nullable=False, default=TransferStatus.PENDING)

    # エラー関連フィールド
    last_error_at = Column(DateTime(timezone=True), nullable=True)
    error_count = Column(Integer, default=0, nullable=False)
    has_unresolved_error = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    buyer = relationship("BuyerProfile", foreign_keys=[
        buyer_id], back_populates="transactions")
    seller = relationship("SellerProfile", foreign_keys=[
        seller_id], back_populates="transactions")
    listing = relationship("ListingItem", back_populates="transactions")
    audit_logs = relationship(
        "TransactionAuditLog", back_populates="transaction", cascade="all, delete-orphan")
    error_logs = relationship(
        "TransactionErrorLog", back_populates="transaction", cascade="all, delete-orphan")


class TransactionAuditLog(Base):
    __tablename__ = "transaction_audit_logs"

    id = Column(Integer, Sequence(
        'transaction_audit_logs_id_seq'), primary_key=True)
    transaction_id = Column(Integer, ForeignKey(
        "transactions.id"), nullable=False)
    field_name = Column(String, nullable=False)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    changed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    change_type = Column(Enum(ChangeType), nullable=False)
    change_reason = Column(Text, nullable=True)
    change_metadata = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True),
                       server_default=func.now(), nullable=False)

    # Relationships
    transaction = relationship("Transaction", back_populates="audit_logs")
    changed_by_user = relationship("User", backref="transaction_changes")


class TransactionErrorLog(Base):
    __tablename__ = "transaction_error_logs"
    __table_args__ = (
        Index('ix_transaction_error_logs_transaction_error_type',
              'transaction_id', 'error_type'),
        Index('ix_transaction_error_logs_created_at', 'created_at'),
        Index('ix_transaction_error_logs_is_resolved_error_type',
              'is_resolved', 'error_type'),
    )

    id = Column(Integer, Sequence(
        'transaction_error_logs_id_seq'), primary_key=True)
    transaction_id = Column(Integer, ForeignKey(
        "transactions.id"), nullable=True)
    error_type = Column(Enum(ErrorType), nullable=False)
    error_code = Column(String, nullable=False)
    error_message = Column(Text, nullable=False)
    error_details = Column(JSON, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)

    # Relationships
    transaction = relationship("Transaction", back_populates="error_logs")


class TakeRate(Base):
    __tablename__ = "take_rates"

    id = Column(Integer, Sequence('take_rates_id_seq'),
                primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_default = Column(Boolean, nullable=False, default=False)
    take_rate = Column(Numeric(5, 2), nullable=False)
    date_from = Column(DateTime(timezone=True), nullable=False)
    date_to = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    note = Column(String, nullable=True)

    user = relationship("User", foreign_keys=[
                        user_id], back_populates="take_rates")
    created_by_user = relationship("User", foreign_keys=[created_by])


class Drawing(Base):
    __tablename__ = "drawings"

    id = Column(Integer, Sequence('drawings_id_seq'), primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    name = Column(String, nullable=False)  # 平面図、断面図、立面図など
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    property = relationship("Property", back_populates="drawings")
    images = relationship("Image", back_populates="drawing",
                          cascade="all, delete-orphan")
