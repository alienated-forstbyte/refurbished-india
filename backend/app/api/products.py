from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.product import Product
from app.models.price_history import PriceHistory
from app.models.stock_history import StockHistory
from app.schemas.product import ProductResponse, ProductList

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductList)
async def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=100),
    brand: str | None = None,
    stock: str | None = None,
    price_min: float | None = None,
    price_max: float | None = None,
    cpu: str | None = None,
    ram: int | None = None,
    gpu: str | None = None,
    sort: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    query = select(Product)
    count_query = select(func.count(Product.id))

    if brand:
        query = query.where(Product.brand.ilike(f"%{brand}%"))
        count_query = count_query.where(Product.brand.ilike(f"%{brand}%"))
    if stock:
        query = query.where(Product.stock_status == stock)
        count_query = count_query.where(Product.stock_status == stock)
    if price_min is not None:
        query = query.where(Product.price >= price_min)
        count_query = count_query.where(Product.price >= price_min)
    if price_max is not None:
        query = query.where(Product.price <= price_max)
        count_query = count_query.where(Product.price <= price_max)
    if cpu:
        query = query.where(Product.cpu.ilike(f"%{cpu}%"))
        count_query = count_query.where(Product.cpu.ilike(f"%{cpu}%"))
    if ram is not None:
        query = query.where(Product.ram_gb == ram)
        count_query = count_query.where(Product.ram_gb == ram)
    if gpu:
        query = query.where(Product.gpu.ilike(f"%{gpu}%"))
        count_query = count_query.where(Product.gpu.ilike(f"%{gpu}%"))

    total_result = await session.execute(count_query)
    total = total_result.scalar_one()

    sort_map = {
        "price_asc": Product.price.asc(),
        "price_desc": Product.price.desc(),
        "discount": Product.discount.desc().nullslast(),
        "newest": Product.first_seen.desc(),
        "updated": Product.last_seen.desc(),
        "name": Product.product_name.asc(),
    }
    if sort and sort in sort_map:
        query = query.order_by(sort_map[sort])
    else:
        query = query.order_by(Product.last_seen.desc())

    query = query.offset((page - 1) * limit).limit(limit)
    result = await session.execute(query)
    products = result.scalars().all()

    return ProductList(total=total, page=page, limit=limit, products=[ProductResponse.model_validate(p) for p in products])


@router.get("/search", response_model=ProductList)
async def search_products(
    query_str: str = Query(..., alias="query"),
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    like_pattern = f"%{query_str}%"
    conditions = [
        Product.product_name.ilike(like_pattern),
        Product.brand.ilike(like_pattern),
        Product.model.ilike(like_pattern),
        Product.cpu.ilike(like_pattern),
        Product.gpu.ilike(like_pattern),
    ]
    from sqlalchemy import or_
    query = select(Product).where(or_(*conditions)).order_by(Product.last_seen.desc())
    count_query = select(func.count(Product.id)).where(or_(*conditions))

    total_result = await session.execute(count_query)
    total = total_result.scalar_one()

    query = query.offset((page - 1) * limit).limit(limit)
    result = await session.execute(query)
    products = result.scalars().all()

    return ProductList(total=total, page=page, limit=limit, products=[ProductResponse.model_validate(p) for p in products])


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse.model_validate(product)
