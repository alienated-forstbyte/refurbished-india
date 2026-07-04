import datetime
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    brand: Mapped[str | None] = mapped_column(String(128), nullable=True)
    cpu: Mapped[str | None] = mapped_column(String(256), nullable=True)
    max_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    ram: Mapped[int | None] = mapped_column(Integer, nullable=True)
    storage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gpu: Mapped[str | None] = mapped_column(String(256), nullable=True)

    notify_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_price: Mapped[bool] = mapped_column(Boolean, default=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="alerts")
    notifications = relationship("NotificationHistory", back_populates="alert", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_alerts_user_id", "user_id"),
        Index("ix_alerts_enabled", "enabled"),
    )
