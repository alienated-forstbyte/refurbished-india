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
    {"name": "Reboot Estore", "website": "https://estore.reboot.co.in", "country": "IN", "scrape_interval": 60},
    {"name": "EPW India", "website": "https://www.epwindia.com", "country": "IN", "scrape_interval": 60},
    {"name": "e-furbished", "website": "https://e-furbished.in", "country": "IN", "scrape_interval": 60},
    {"name": "Cashify", "website": "https://www.cashify.in", "country": "IN", "scrape_interval": 120},
    {"name": "EzyRefurb", "website": "https://www.ezyrefurb.com", "country": "IN", "scrape_interval": 60},
    {"name": "Lenovo Outlet", "website": "https://www.lenovo.com/in/outletin/en", "country": "IN", "scrape_interval": 120},
    {"name": "Asus Outlet", "website": "https://www.asus.com/in/deals/outlet/", "country": "IN", "scrape_interval": 120},
    {"name": "Dell Outlet", "website": "https://outlet.us.dell.com", "country": "IN", "scrape_interval": 120},
    {"name": "HP Renew", "website": "https://www.hp.com/in-en/services/workforce-solutions/workforce-computing/renew-solutions/refurbished-hardware.html", "country": "IN", "scrape_interval": 120},
    {"name": "Refurbr", "website": "https://www.refurbr.in", "country": "IN", "scrape_interval": 60},
    {"name": "Amazon Renewed", "website": "https://www.amazon.in/renewed", "country": "IN", "scrape_interval": 120},
]


async def seed():
    from sqlalchemy import text

    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        for store_data in STORES:
            await session.execute(
                text("""
                    INSERT INTO stores (name, website, country, enabled, scrape_interval)
                    VALUES (:name, :website, :country, :enabled, :scrape_interval)
                    ON CONFLICT (name) DO UPDATE SET
                        website = EXCLUDED.website,
                        country = EXCLUDED.country,
                        enabled = EXCLUDED.enabled,
                        scrape_interval = EXCLUDED.scrape_interval
                """),
                {**store_data, "enabled": True},
            )
        await session.commit()
        print(f"Seeded/updated {len(STORES)} stores")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
