import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[int] = mapped_column(Integer, ForeignKey("stores.id"), nullable=False)

    brand: Mapped[str | None] = mapped_column(String(128), nullable=True)
    model: Mapped[str | None] = mapped_column(String(256), nullable=True)
    product_name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    cpu: Mapped[str | None] = mapped_column(String(256), nullable=True)
    cpu_generation: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ram_gb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    storage_gb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    storage_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    gpu: Mapped[str | None] = mapped_column(String(256), nullable=True)
    display_size: Mapped[float | None] = mapped_column(Float, nullable=True)
    display_resolution: Mapped[str | None] = mapped_column(String(64), nullable=True)
    condition: Mapped[str | None] = mapped_column(String(64), nullable=True)
    warranty_months: Mapped[int | None] = mapped_column(Integer, nullable=True)

    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    original_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    discount: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(8), default="INR")

    stock_status: Mapped[str] = mapped_column(String(32), default="unknown")
    product_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    first_seen: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_updated: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    store = relationship("Store", back_populates="products")
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    stock_history = relationship("StockHistory", back_populates="product", cascade="all, delete-orphan")
    images = relationship("Image", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_products_price", "price"),
        Index("ix_products_stock_status", "stock_status"),
        Index("ix_products_brand", "brand"),
        Index("ix_products_model", "model"),
        Index("ix_products_cpu_generation", "cpu_generation"),
        Index("ix_products_last_seen", "last_seen"),
    )
