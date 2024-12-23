from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    company_type = Column(String,
                          nullable=False)  # manufacturer, design, construction
    description = Column(Text)
    website = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    products = relationship("Product", back_populates="manufacturer")
    designed_properties = relationship(
        "Property",
        back_populates="design_company",
        foreign_keys="Property.design_company_id")
    constructed_properties = relationship(
        "Property",
        back_populates="construction_company",
        foreign_keys="Property.construction_company_id")


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    property_type = Column(String, nullable=False)  # house, apartment, other
    prefecture = Column(String, nullable=False)
    layout = Column(String)
    construction_year = Column(Integer)
    construction_month = Column(Integer)
    site_area = Column(Float)
    building_area = Column(Float)
    floor_count = Column(Integer)
    structure = Column(String)
    design_company_id = Column(Integer,
                               ForeignKey("companies.id"),
                               nullable=True)
    construction_company_id = Column(Integer,
                                     ForeignKey("companies.id"),
                                     nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="properties")
    design_company = relationship("Company",
                                  back_populates="designed_properties",
                                  foreign_keys=[design_company_id])
    construction_company = relationship(
        "Company",
        back_populates="constructed_properties",
        foreign_keys=[construction_company_id])
    rooms = relationship("Room",
                         back_populates="property",
                         cascade="all, delete-orphan")
    images = relationship("Image",
                          back_populates="property",
                          cascade="all, delete-orphan")
    products_for_sale = relationship("ProductForSale",
                                     back_populates="property")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    property = relationship("Property", back_populates="rooms")
    products = relationship("Product",
                            back_populates="room",
                            cascade="all, delete-orphan")
    images = relationship("Image",
                          back_populates="room",
                          cascade="all, delete-orphan")


class ProductCategory(Base):
    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    products = relationship("Product", back_populates="product_category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    product_category_id = Column(Integer,
                                 ForeignKey("product_categories.id"),
                                 nullable=False)
    manufacturer_id = Column(Integer,
                             ForeignKey("companies.id"),
                             nullable=True)
    name = Column(String, nullable=False)
    product_code = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    catalog_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("Room", back_populates="products")
    product_category = relationship("ProductCategory",
                                    back_populates="products")
    manufacturer = relationship("Company", back_populates="products")
    specifications = relationship("ProductSpecification",
                                  back_populates="product",
                                  cascade="all, delete-orphan")
    dimensions = relationship("ProductDimension",
                              back_populates="product",
                              cascade="all, delete-orphan")
    images = relationship("Image",
                          back_populates="product",
                          cascade="all, delete-orphan")


class ProductSpecification(Base):
    __tablename__ = "product_specifications"

    id = Column(Integer, primary_key=True)
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


class ProductDimension(Base):
    __tablename__ = "product_dimensions"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    dimension_type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="dimensions")


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    description = Column(Text)
    s3_key = Column(String, nullable=True)  # 追加
    image_type = Column(String, nullable=False)  # main, sub
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    property = relationship("Property", back_populates="images")
    room = relationship("Room", back_populates="images")
    product = relationship("Product", back_populates="images")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
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
    purchases = relationship("Purchase", back_populates="buyer")


class SellerProfile(Base):
    __tablename__ = "seller_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_name = Column(String, nullable=True)
    representative_name = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    address = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    business_registration_number = Column(String, nullable=True)
    tax_registration_number = Column(String, nullable=True)

    stripe_account_id = Column(String, unique=True, nullable=True)
    stripe_account_status = Column(String, nullable=True, default='pending')
    stripe_account_type = Column(String, nullable=True, default='standard')
    stripe_onboarding_completed = Column(Boolean, default=False)
    stripe_charges_enabled = Column(Boolean, default=False)
    stripe_payouts_enabled = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="seller_profile")
    sales = relationship("Sale", back_populates="seller")
    products_for_sale = relationship("ProductForSale", back_populates="seller")


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_for_sale_id = Column(Integer,
                                 ForeignKey("products_for_sale.id"),
                                 nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default='pending')

    stripe_payment_intent_id = Column(String, nullable=True, unique=True)
    stripe_payment_status = Column(String, nullable=True)
    stripe_transfer_id = Column(String, nullable=True, unique=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    buyer = relationship("User", back_populates="purchases")


class ProductForSale(Base):
    __tablename__ = "products_for_sale"

    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer,
                       ForeignKey("seller_profiles.id"),
                       nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Integer, nullable=False)
    sale_type = Column(String,
                       nullable=False)  # property, room, product, consultation
    consultation_type = Column(String, nullable=True)  # online, offline
    status = Column(String, default='draft')  # draft, published, sold

    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)

    is_negotiable = Column(Boolean, default=False)
    consultation_minutes = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    seller = relationship("SellerProfile", back_populates="products_for_sale")
    property = relationship("Property")
    room = relationship("Room")
    product = relationship("Product")
    sales = relationship("Sale", back_populates="product_for_sale")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer,
                       ForeignKey("seller_profiles.id"),
                       nullable=False)
    product_for_sale_id = Column(Integer,
                                 ForeignKey("products_for_sale.id"),
                                 nullable=False)
    purchase_id = Column(Integer,
                         ForeignKey("purchases.id"),
                         nullable=False,
                         unique=True)
    amount = Column(Integer, nullable=False)
    platform_fee = Column(Integer, nullable=False)
    seller_amount = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default='pending')

    stripe_transfer_id = Column(String, nullable=True, unique=True)
    stripe_transfer_status = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    seller = relationship("SellerProfile", back_populates="sales")
    product_for_sale = relationship("ProductForSale", back_populates="sales")
    purchase = relationship("Purchase", backref="sale")
