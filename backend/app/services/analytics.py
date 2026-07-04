import logging
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.store import Store

logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def average_discount(self) -> float | None:
        result = await self.session.execute(
            select(func.avg(Product.discount)).where(
                Product.discount.isnot(None),
                Product.stock_status == "in_stock",
            )
        )
        return result.scalar_one()

    async def stock_turnover(self) -> dict[str, int]:
        total = await self.session.execute(select(func.count(Product.id)))
        in_stock = await self.session.execute(
            select(func.count(Product.id)).where(Product.stock_status == "in_stock")
        )
        out_stock = await self.session.execute(
            select(func.count(Product.id)).where(Product.stock_status == "out_of_stock")
        )
        return {
            "total": total.scalar_one(),
            "in_stock": in_stock.scalar_one(),
            "out_of_stock": out_stock.scalar_one(),
        }

    async def popular_brands(self, limit: int = 10) -> list[dict]:
        result = await self.session.execute(
            select(Product.brand, func.count(Product.id).label("count"))
            .where(Product.brand.isnot(None))
            .group_by(Product.brand)
            .order_by(func.count(Product.id).desc())
            .limit(limit)
        )
        return [{"brand": row[0], "count": row[1]} for row in result.all()]

    async def average_selling_price(self) -> float | None:
        result = await self.session.execute(
            select(func.avg(Product.price)).where(Product.stock_status == "in_stock")
        )
        return result.scalar_one()
