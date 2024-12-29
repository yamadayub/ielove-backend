# alembic/versions/cf254705a790_add_enum_types.py の内容として保存
"""add_enum_types

Revision ID: cf254705a790
Revises: c98fdc7057d4
Create Date: 2024-12-29 21:01:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'cf254705a790'
down_revision = 'c98fdc7057d4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ENUMタイプの作成
    op.execute(
        "CREATE TYPE companytype AS ENUM ('MANUFACTURER', 'DESIGN', 'CONSTRUCTION')")
    op.execute("CREATE TYPE propertytype AS ENUM ('HOUSE', 'APARTMENT', 'OTHER')")
    op.execute(
        "CREATE TYPE structure AS ENUM ('WOODEN', 'STEEL_FRAME', 'RC', 'SRC', 'LIGHT_STEEL')")
    op.execute(
        "CREATE TYPE dimensiontype AS ENUM ('WIDTH', 'HEIGHT', 'DEPTH', 'DIAMETER', 'LENGTH')")
    op.execute("CREATE TYPE imagetype AS ENUM ('MAIN', 'SUB', 'PAID')")
    op.execute("CREATE TYPE listingtype AS ENUM ('PROPERTY_SPECS', 'ROOM_SPECS', 'PRODUCT_SPECS', 'CONSULTATION', 'PROPERTY_VIEWING')")
    op.execute(
        "CREATE TYPE listingstatus AS ENUM ('DRAFT', 'PUBLISHED', 'RESERVED', 'SOLD', 'CANCELLED')")
    op.execute("CREATE TYPE visibility AS ENUM ('PUBLIC', 'PRIVATE')")


def downgrade() -> None:
    # ENUMタイプの削除
    op.execute("DROP TYPE IF EXISTS companytype")
    op.execute("DROP TYPE IF EXISTS propertytype")
    op.execute("DROP TYPE IF EXISTS structure")
    op.execute("DROP TYPE IF EXISTS dimensiontype")
    op.execute("DROP TYPE IF EXISTS imagetype")
    op.execute("DROP TYPE IF EXISTS listingtype")
    op.execute("DROP TYPE IF EXISTS listingstatus")
    op.execute("DROP TYPE IF EXISTS visibility")
