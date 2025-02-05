"""make transaction_id nullable in transaction_error_logs

Revision ID: c188816df799
Revises: 3314937609d2
Create Date: 2024-12-30 15:44:20.405802

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c188816df799'
down_revision: Union[str, None] = '3314937609d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('transaction_error_logs', 'transaction_id',
                    existing_type=sa.INTEGER(),
                    nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('transaction_error_logs', 'transaction_id',
                    existing_type=sa.INTEGER(),
                    nullable=False)
    # ### end Alembic commands ###
