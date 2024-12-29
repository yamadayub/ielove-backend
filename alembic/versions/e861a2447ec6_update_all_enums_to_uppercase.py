"""update_all_enums_to_uppercase

Revision ID: e861a2447ec6
Revises: 44c116c35218
Create Date: 2024-12-29 16:32:06.323172

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e861a2447ec6'
down_revision: Union[str, None] = '44c116c35218'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # CompanyType
    op.execute("ALTER TABLE companies ALTER COLUMN company_type TYPE VARCHAR")
    op.execute("DROP TYPE companytype")
    op.execute(
        "CREATE TYPE companytype AS ENUM ('MANUFACTURER', 'DESIGN', 'CONSTRUCTION')")
    op.execute("UPDATE companies SET company_type = UPPER(company_type)")
    op.execute(
        "ALTER TABLE companies ALTER COLUMN company_type TYPE companytype USING company_type::companytype")

    # PropertyType
    op.execute("ALTER TABLE properties ALTER COLUMN property_type TYPE VARCHAR")
    op.execute("DROP TYPE propertytype")
    op.execute("CREATE TYPE propertytype AS ENUM ('HOUSE', 'APARTMENT', 'OTHER')")
    op.execute("UPDATE properties SET property_type = UPPER(property_type)")
    op.execute(
        "ALTER TABLE properties ALTER COLUMN property_type TYPE propertytype USING property_type::propertytype")

    # StructureType
    op.execute("ALTER TABLE properties ALTER COLUMN structure TYPE VARCHAR")
    op.execute("DROP TYPE structuretype")
    op.execute(
        "CREATE TYPE structuretype AS ENUM ('WOODEN', 'STEEL_FRAME', 'RC', 'SRC', 'LIGHT_STEEL')")
    op.execute("UPDATE properties SET structure = UPPER(structure)")
    op.execute(
        "ALTER TABLE properties ALTER COLUMN structure TYPE structuretype USING structure::structuretype")

    # DimensionType
    op.execute(
        "ALTER TABLE product_dimensions ALTER COLUMN dimension_type TYPE VARCHAR")
    op.execute("DROP TYPE dimensiontype")
    op.execute(
        "CREATE TYPE dimensiontype AS ENUM ('WIDTH', 'HEIGHT', 'DEPTH', 'DIAMETER', 'LENGTH')")
    op.execute(
        "UPDATE product_dimensions SET dimension_type = UPPER(dimension_type)")
    op.execute(
        "ALTER TABLE product_dimensions ALTER COLUMN dimension_type TYPE dimensiontype USING dimension_type::dimensiontype")

    # ImageType
    op.execute("ALTER TABLE images ALTER COLUMN image_type TYPE VARCHAR")
    op.execute("DROP TYPE imagetype")
    op.execute("CREATE TYPE imagetype AS ENUM ('MAIN', 'SUB', 'PAID')")
    op.execute("UPDATE images SET image_type = UPPER(image_type)")
    op.execute(
        "ALTER TABLE images ALTER COLUMN image_type TYPE imagetype USING image_type::imagetype")

    # ListingType
    op.execute("ALTER TABLE listing_items ALTER COLUMN listing_type TYPE VARCHAR")
    op.execute("DROP TYPE listingtype")
    op.execute("CREATE TYPE listingtype AS ENUM ('PROPERTY_SPECS', 'ROOM_SPECS', 'PRODUCT_SPECS', 'CONSULTATION', 'PROPERTY_VIEWING')")
    op.execute(
        "UPDATE listing_items SET listing_type = UPPER(REPLACE(listing_type, ' ', '_'))")
    op.execute(
        "ALTER TABLE listing_items ALTER COLUMN listing_type TYPE listingtype USING listing_type::listingtype")

    # Visibility
    op.execute("ALTER TABLE listing_items ALTER COLUMN visibility TYPE VARCHAR")
    op.execute("DROP TYPE visibility")
    op.execute("CREATE TYPE visibility AS ENUM ('PUBLIC', 'PRIVATE')")
    op.execute("UPDATE listing_items SET visibility = UPPER(visibility)")
    op.execute(
        "ALTER TABLE listing_items ALTER COLUMN visibility TYPE visibility USING visibility::visibility")

    # ListingStatus
    op.execute("ALTER TABLE listing_items ALTER COLUMN status TYPE VARCHAR")
    op.execute("DROP TYPE IF EXISTS listingstatus")
    op.execute(
        "CREATE TYPE listingstatus AS ENUM ('DRAFT', 'PUBLISHED', 'RESERVED', 'SOLD', 'CANCELLED')")
    op.execute("UPDATE listing_items SET status = UPPER(status)")
    op.execute(
        "ALTER TABLE listing_items ALTER COLUMN status TYPE listingstatus USING status::listingstatus")


def downgrade() -> None:
    # CompanyType
    op.execute("ALTER TABLE companies ALTER COLUMN company_type TYPE VARCHAR")
    op.execute("DROP TYPE companytype")
    op.execute(
        "CREATE TYPE companytype AS ENUM ('manufacturer', 'design', 'construction')")
    op.execute("UPDATE companies SET company_type = LOWER(company_type)")
    op.execute(
        "ALTER TABLE companies ALTER COLUMN company_type TYPE companytype USING company_type::companytype")

    # PropertyType
    op.execute("ALTER TABLE properties ALTER COLUMN property_type TYPE VARCHAR")
    op.execute("DROP TYPE propertytype")
    op.execute("CREATE TYPE propertytype AS ENUM ('house', 'apartment', 'other')")
    op.execute("UPDATE properties SET property_type = LOWER(property_type)")
    op.execute(
        "ALTER TABLE properties ALTER COLUMN property_type TYPE propertytype USING property_type::propertytype")

    # StructureType
    op.execute("ALTER TABLE properties ALTER COLUMN structure TYPE VARCHAR")
    op.execute("DROP TYPE structuretype")
    op.execute(
        "CREATE TYPE structuretype AS ENUM ('wooden', 'steel_frame', 'rc', 'src', 'light_steel')")
    op.execute("UPDATE properties SET structure = LOWER(structure)")
    op.execute(
        "ALTER TABLE properties ALTER COLUMN structure TYPE structuretype USING structure::structuretype")

    # DimensionType
    op.execute(
        "ALTER TABLE product_dimensions ALTER COLUMN dimension_type TYPE VARCHAR")
    op.execute("DROP TYPE dimensiontype")
    op.execute(
        "CREATE TYPE dimensiontype AS ENUM ('width', 'height', 'depth', 'diameter', 'length')")
    op.execute(
        "UPDATE product_dimensions SET dimension_type = LOWER(dimension_type)")
    op.execute(
        "ALTER TABLE product_dimensions ALTER COLUMN dimension_type TYPE dimensiontype USING dimension_type::dimensiontype")

    # ImageType
    op.execute("ALTER TABLE images ALTER COLUMN image_type TYPE VARCHAR")
    op.execute("DROP TYPE imagetype")
    op.execute("CREATE TYPE imagetype AS ENUM ('main', 'sub', 'paid')")
    op.execute("UPDATE images SET image_type = LOWER(image_type)")
    op.execute(
        "ALTER TABLE images ALTER COLUMN image_type TYPE imagetype USING image_type::imagetype")

    # ListingType
    op.execute("ALTER TABLE listing_items ALTER COLUMN listing_type TYPE VARCHAR")
    op.execute("DROP TYPE listingtype")
    op.execute("CREATE TYPE listingtype AS ENUM ('property_specs', 'room_specs', 'product_specs', 'consultation', 'property_viewing')")
    op.execute("UPDATE listing_items SET listing_type = LOWER(listing_type)")
    op.execute(
        "ALTER TABLE listing_items ALTER COLUMN listing_type TYPE listingtype USING listing_type::listingtype")

    # Visibility
    op.execute("ALTER TABLE listing_items ALTER COLUMN visibility TYPE VARCHAR")
    op.execute("DROP TYPE visibility")
    op.execute("CREATE TYPE visibility AS ENUM ('public', 'private')")
    op.execute("UPDATE listing_items SET visibility = LOWER(visibility)")
    op.execute(
        "ALTER TABLE listing_items ALTER COLUMN visibility TYPE visibility USING visibility::visibility")
