"""Initial migration

Revision ID: 001
Revises:
Create Date: 2026-07-04
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "stores",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("website", sa.String(512), nullable=False),
        sa.Column("country", sa.String(8), server_default="IN"),
        sa.Column("enabled", sa.Boolean(), server_default="true"),
        sa.Column("last_scrape", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scrape_interval", sa.Integer(), server_default="60"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(256), nullable=False),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("store_id", sa.Integer(), nullable=False),
        sa.Column("brand", sa.String(128), nullable=True),
        sa.Column("model", sa.String(256), nullable=True),
        sa.Column("product_name", sa.String(512), nullable=True),
        sa.Column("cpu", sa.String(256), nullable=True),
        sa.Column("cpu_generation", sa.String(64), nullable=True),
        sa.Column("ram_gb", sa.Integer(), nullable=True),
        sa.Column("storage_gb", sa.Integer(), nullable=True),
        sa.Column("storage_type", sa.String(32), nullable=True),
        sa.Column("gpu", sa.String(256), nullable=True),
        sa.Column("display_size", sa.Float(), nullable=True),
        sa.Column("display_resolution", sa.String(64), nullable=True),
        sa.Column("condition", sa.String(64), nullable=True),
        sa.Column("warranty_months", sa.Integer(), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("original_price", sa.Float(), nullable=True),
        sa.Column("discount", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(8), server_default="INR"),
        sa.Column("stock_status", sa.String(32), server_default="unknown"),
        sa.Column("product_url", sa.Text(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("first_seen", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_seen", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_updated", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_products_price", "products", ["price"])
    op.create_index("ix_products_stock_status", "products", ["stock_status"])
    op.create_index("ix_products_brand", "products", ["brand"])
    op.create_index("ix_products_model", "products", ["model"])
    op.create_index("ix_products_cpu_generation", "products", ["cpu_generation"])
    op.create_index("ix_products_last_seen", "products", ["last_seen"])

    op.create_table(
        "price_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_price_history_product_id", "price_history", ["product_id"])
    op.create_index("ix_price_history_timestamp", "price_history", ["timestamp"])

    op.create_table(
        "stock_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("stock_status", sa.String(32), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_stock_history_product_id", "stock_history", ["product_id"])
    op.create_index("ix_stock_history_timestamp", "stock_history", ["timestamp"])

    op.create_table(
        "images",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), server_default="0"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("brand", sa.String(128), nullable=True),
        sa.Column("cpu", sa.String(256), nullable=True),
        sa.Column("max_price", sa.Float(), nullable=True),
        sa.Column("ram", sa.Integer(), nullable=True),
        sa.Column("storage", sa.Integer(), nullable=True),
        sa.Column("gpu", sa.String(256), nullable=True),
        sa.Column("notify_stock", sa.Boolean(), server_default="true"),
        sa.Column("notify_price", sa.Boolean(), server_default="true"),
        sa.Column("enabled", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alerts_user_id", "alerts", ["user_id"])
    op.create_index("ix_alerts_enabled", "alerts", ["enabled"])

    op.create_table(
        "notification_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("alert_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(64), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("status", sa.String(32), server_default="pending"),
        sa.ForeignKeyConstraint(["alert_id"], ["alerts.id"], ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "scrape_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("store_id", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("products_found", sa.Integer(), server_default="0"),
        sa.Column("errors", sa.Text(), nullable=True),
        sa.Column("status", sa.String(32), server_default="running"),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("scrape_logs")
    op.drop_table("notification_history")
    op.drop_index("ix_alerts_enabled")
    op.drop_index("ix_alerts_user_id")
    op.drop_table("alerts")
    op.drop_table("images")
    op.drop_index("ix_stock_history_timestamp")
    op.drop_index("ix_stock_history_product_id")
    op.drop_table("stock_history")
    op.drop_index("ix_price_history_timestamp")
    op.drop_index("ix_price_history_product_id")
    op.drop_table("price_history")
    op.drop_index("ix_products_last_seen")
    op.drop_index("ix_products_cpu_generation")
    op.drop_index("ix_products_model")
    op.drop_index("ix_products_brand")
    op.drop_index("ix_products_stock_status")
    op.drop_index("ix_products_price")
    op.drop_table("products")
    op.drop_table("users")
    op.drop_table("stores")
