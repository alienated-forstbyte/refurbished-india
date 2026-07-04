from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.store import Store
from app.models.product import Product
from app.schemas.store import StoreResponse

router = APIRouter(prefix="/stores", tags=["stores"])


@router.get("", response_model=list[StoreResponse])
async def list_stores(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Store).where(Store.enabled == True))
    stores = result.scalars().all()
    return [StoreResponse.model_validate(s) for s in stores]


@router.get("/{store_id}", response_model=StoreResponse)
async def get_store(store_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Store).where(Store.id == store_id))
    store = result.scalar_one_or_none()
    if not store:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Store not found")
    return StoreResponse.model_validate(store)
