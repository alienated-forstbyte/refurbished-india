import datetime
from sqlalchemy import String, Boolean, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    website: Mapped[str] = mapped_column(String(512), nullable=False)
    country: Mapped[str] = mapped_column(String(8), default="IN")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_scrape: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scrape_interval: Mapped[int] = mapped_column(Integer, default=60)

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    products = relationship("Product", back_populates="store")
    scrape_logs = relationship("ScrapeLog", back_populates="store")
