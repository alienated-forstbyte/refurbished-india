import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StockHistory(Base):
    __tablename__ = "stock_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    stock_status: Mapped[str] = mapped_column(String(32), nullable=False)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="stock_history")

    __table_args__ = (
        Index("ix_stock_history_product_id", "product_id"),
        Index("ix_stock_history_timestamp", "timestamp"),
    )
