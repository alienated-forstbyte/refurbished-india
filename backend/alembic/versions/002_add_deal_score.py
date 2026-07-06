"""Add deal_score column to products

Revision ID: 002
Revises: 001
Create Date: 2026-07-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("products", sa.Column("deal_score", sa.Float(), nullable=True))
    op.create_index("ix_products_deal_score", "products", ["deal_score"])


def downgrade() -> None:
    op.drop_index("ix_products_deal_score")
    op.drop_column("products", "deal_score")
