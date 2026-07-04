from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.product import Product
from app.models.store import Store
from app.schemas.stats import StatsResponse

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=StatsResponse)
async def get_stats(session: AsyncSession = Depends(get_session)):
    total_products_result = await session.execute(select(func.count(Product.id)))
    total_products = total_products_result.scalar_one()

    in_stock_result = await session.execute(
        select(func.count(Product.id)).where(Product.stock_status == "in_stock")
    )
    in_stock_count = in_stock_result.scalar_one()

    out_of_stock_result = await session.execute(
        select(func.count(Product.id)).where(Product.stock_status == "out_of_stock")
    )
    out_of_stock_count = out_of_stock_result.scalar_one()

    store_count_result = await session.execute(select(func.count(Store.id)).where(Store.enabled == True))
    store_count = store_count_result.scalar_one()

    avg_price_result = await session.execute(
        select(func.avg(Product.price)).where(Product.stock_status == "in_stock")
    )
    average_price = avg_price_result.scalar_one()

    return StatsResponse(
        total_products=total_products,
        in_stock_count=in_stock_count,
        out_of_stock_count=out_of_stock_count,
        store_count=store_count,
        average_price=average_price,
    )
