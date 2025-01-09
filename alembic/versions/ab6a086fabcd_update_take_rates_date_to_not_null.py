"""update take_rates date_to not null

Revision ID: ab6a086fabcd
Revises: d3a6ae95c286
Create Date: 2024-01-09 18:08:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'ab6a086fabcd'
down_revision = 'd3a6ae95c286'
branch_labels = None
depends_on = None


def upgrade():
    # まず、NULLのdate_toを2099-12-31 23:59:59に更新
    op.execute("""
        UPDATE take_rates 
        SET date_to = '2099-12-31 23:59:59'
        WHERE date_to IS NULL
    """)

    # date_toをnullable=Falseに変更
    op.alter_column('take_rates', 'date_to',
                    existing_type=sa.DateTime(timezone=True),
                    nullable=False
                    )


def downgrade():
    # date_toをnullable=Trueに戻す
    op.alter_column('take_rates', 'date_to',
                    existing_type=sa.DateTime(timezone=True),
                    nullable=True
                    )
