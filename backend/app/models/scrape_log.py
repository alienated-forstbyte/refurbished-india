import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ScrapeLog(Base):
    __tablename__ = "scrape_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[int] = mapped_column(Integer, ForeignKey("stores.id"), nullable=False)

    start_time: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    products_found: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="running")
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    store = relationship("Store", back_populates="scrape_logs")
