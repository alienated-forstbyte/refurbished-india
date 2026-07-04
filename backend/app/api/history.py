from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.price_history import PriceHistory
from app.models.stock_history import StockHistory

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/{product_id}")
async def get_product_history(product_id: int, session: AsyncSession = Depends(get_session)):
    price_result = await session.execute(
        select(PriceHistory).where(PriceHistory.product_id == product_id).order_by(PriceHistory.timestamp.asc())
    )
    stock_result = await session.execute(
        select(StockHistory).where(StockHistory.product_id == product_id).order_by(StockHistory.timestamp.asc())
    )
    return {
        "price_history": [
            {"price": ph.price, "timestamp": ph.timestamp.isoformat()} for ph in price_result.scalars().all()
        ],
        "stock_history": [
            {"stock_status": sh.stock_status, "timestamp": sh.timestamp.isoformat()} for sh in stock_result.scalars().all()
        ],
    }
