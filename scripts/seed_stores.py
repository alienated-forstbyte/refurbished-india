#!/usr/bin/env python3
"""
Seed the database with initial store entries.
Run: python scripts/seed_stores.py
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import settings
from app.models.store import Store
from app.database import Base

STORES = [
    {"name": "Lenovo Refurbished", "website": "https://www.lenovorefurbished.in", "country": "IN", "scrape_interval": 60},
    {"name": "Asus Refurbished", "website": "https://www.asusrefurbished.in", "country": "IN", "scrape_interval": 60},
    {"name": "Dell Outlet", "website": "https://www.delloutlet.in", "country": "IN", "scrape_interval": 60},
    {"name": "HP Renew", "website": "https://www.hprenew.in", "country": "IN", "scrape_interval": 60},
    {"name": "Amazon Renewed", "website": "https://www.amazon.in/renewed", "country": "IN", "scrape_interval": 120},
    {"name": "Flipkart Refurbished", "website": "https://www.flipkart.com/refurbished", "country": "IN", "scrape_interval": 120},
    {"name": "Cashify", "website": "https://www.cashify.in", "country": "IN", "scrape_interval": 120},
]


async def seed():
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        for store_data in STORES:
            session.add(Store(**store_data))
        await session.commit()
        print(f"Seeded {len(STORES)} stores")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
