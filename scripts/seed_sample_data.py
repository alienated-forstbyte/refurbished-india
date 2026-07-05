#!/usr/bin/env python3
import asyncio
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import settings
from app.database import Base
from app.models.product import Product
from app.models.price_history import PriceHistory
from app.models.stock_history import StockHistory
from app.models.image import Image
from app.models.store import Store

PRODUCTS = [
    {
        "store_id": 1,
        "brand": "Lenovo",
        "model": "ThinkPad X1 Carbon Gen 11",
        "product_name": "ThinkPad X1 Carbon Gen 11 (Intel i7-1365U, 16GB, 512GB)",
        "cpu": "Intel Core i7-1365U",
        "cpu_generation": "13th Gen Intel",
        "ram_gb": 16,
        "storage_gb": 512,
        "storage_type": "SSD",
        "gpu": "Intel Iris Xe",
        "display_size": 14.0,
        "display_resolution": "1920x1200",
        "condition": "Excellent",
        "warranty_months": 12,
        "price": 89999,
        "original_price": 159999,
        "discount": 44,
        "stock_status": "in_stock",
        "product_url": "https://www.lenovorefurbished.in/thinkpad-x1-carbon-gen11",
        "image_url": "https://picsum.photos/seed/thinkpad1/400/300",
    },
    {
        "store_id": 1,
        "brand": "Lenovo",
        "model": "ThinkPad T14 Gen 4",
        "product_name": "ThinkPad T14 Gen 4 (AMD Ryzen 7 PRO 7840U, 32GB, 1TB)",
        "cpu": "AMD Ryzen 7 PRO 7840U",
        "cpu_generation": "AMD Ryzen 7000",
        "ram_gb": 32,
        "storage_gb": 1024,
        "storage_type": "SSD",
        "gpu": "AMD Radeon 780M",
        "display_size": 14.0,
        "display_resolution": "1920x1200",
        "condition": "Very Good",
        "warranty_months": 6,
        "price": 74999,
        "original_price": 135000,
        "discount": 44,
        "stock_status": "in_stock",
        "product_url": "https://www.lenovorefurbished.in/thinkpad-t14-gen4",
        "image_url": "https://picsum.photos/seed/thinkpad2/400/300",
    },
    {
        "store_id": 1,
        "brand": "Lenovo",
        "model": "ThinkPad X280",
        "product_name": "ThinkPad X280 (Intel i5-8350U, 8GB, 256GB)",
        "cpu": "Intel Core i5-8350U",
        "cpu_generation": "8th Gen Intel",
        "ram_gb": 8,
        "storage_gb": 256,
        "storage_type": "SSD",
        "gpu": "Intel UHD 620",
        "display_size": 12.5,
        "display_resolution": "1366x768",
        "condition": "Good",
        "warranty_months": 3,
        "price": 29999,
        "original_price": 55000,
        "discount": 45,
        "stock_status": "out_of_stock",
        "product_url": "https://www.lenovorefurbished.in/thinkpad-x280",
        "image_url": "https://picsum.photos/seed/thinkpad3/400/300",
    },
    {
        "store_id": 1,
        "brand": "Lenovo",
        "model": "Legion 5 Pro",
        "product_name": "Legion 5 Pro (AMD Ryzen 7 5800H, RTX 3060, 16GB, 512GB)",
        "cpu": "AMD Ryzen 7 5800H",
        "cpu_generation": "AMD Ryzen 5000",
        "ram_gb": 16,
        "storage_gb": 512,
        "storage_type": "SSD",
        "gpu": "NVIDIA RTX 3060",
        "display_size": 16.0,
        "display_resolution": "2560x1600",
        "condition": "Excellent",
        "warranty_months": 12,
        "price": 84999,
        "original_price": 145000,
        "discount": 41,
        "stock_status": "in_stock",
        "product_url": "https://www.lenovorefurbished.in/legion-5-pro",
        "image_url": "https://picsum.photos/seed/legion1/400/300",
    },
    {
        "store_id": 2,
        "brand": "Asus",
        "model": "ZenBook 14 OLED",
        "product_name": "ZenBook 14 OLED (Intel i7-1355U, 16GB, 512GB)",
        "cpu": "Intel Core i7-1355U",
        "cpu_generation": "13th Gen Intel",
        "ram_gb": 16,
        "storage_gb": 512,
        "storage_type": "SSD",
        "gpu": "Intel Iris Xe",
        "display_size": 14.0,
        "display_resolution": "2880x1800",
        "condition": "Excellent",
        "warranty_months": 12,
        "price": 67999,
        "original_price": 119999,
        "discount": 43,
        "stock_status": "in_stock",
        "product_url": "https://www.asusrefurbished.in/zenbook-14-oled",
        "image_url": "https://picsum.photos/seed/zenbook1/400/300",
    },
    {
        "store_id": 2,
        "brand": "Asus",
        "model": "Vivobook 16X",
        "product_name": "Vivobook 16X (Intel i5-12500H, 16GB, 512GB)",
        "cpu": "Intel Core i5-12500H",
        "cpu_generation": "12th Gen Intel",
        "ram_gb": 16,
        "storage_gb": 512,
        "storage_type": "SSD",
        "gpu": "Intel Iris Xe",
        "display_size": 16.0,
        "display_resolution": "1920x1200",
        "condition": "Very Good",
        "warranty_months": 6,
        "price": 49999,
        "original_price": 84999,
        "discount": 41,
        "stock_status": "in_stock",
        "product_url": "https://www.asusrefurbished.in/vivobook-16x",
        "image_url": "https://picsum.photos/seed/vivobook1/400/300",
    },
    {
        "store_id": 2,
        "brand": "Asus",
        "model": "ROG Zephyrus G14",
        "product_name": "ROG Zephyrus G14 (AMD Ryzen 9 7940HS, RTX 4060, 16GB, 1TB)",
        "cpu": "AMD Ryzen 9 7940HS",
        "cpu_generation": "AMD Ryzen 7000",
        "ram_gb": 16,
        "storage_gb": 1024,
        "storage_type": "SSD",
        "gpu": "NVIDIA RTX 4060",
        "display_size": 14.0,
        "display_resolution": "2560x1600",
        "condition": "Excellent",
        "warranty_months": 12,
        "price": 114999,
        "original_price": 189999,
        "discount": 39,
        "stock_status": "in_stock",
        "product_url": "https://www.asusrefurbished.in/rog-zephyrus-g14",
        "image_url": "https://picsum.photos/seed/rog1/400/300",
    },
    {
        "store_id": 3,
        "brand": "Dell",
        "model": "Latitude 7440",
        "product_name": "Latitude 7440 (Intel i7-1365U, 16GB, 512GB)",
        "cpu": "Intel Core i7-1365U",
        "cpu_generation": "13th Gen Intel",
        "ram_gb": 16,
        "storage_gb": 512,
        "storage_type": "SSD",
        "gpu": "Intel Iris Xe",
        "display_size": 14.0,
        "display_resolution": "1920x1200",
        "condition": "Excellent",
        "warranty_months": 12,
        "price": 74999,
        "original_price": 139999,
        "discount": 46,
        "stock_status": "in_stock",
        "product_url": "https://www.delloutlet.in/latitude-7440",
        "image_url": "https://picsum.photos/seed/latitude1/400/300",
    },
    {
        "store_id": 3,
        "brand": "Dell",
        "model": "XPS 15 9530",
        "product_name": "XPS 15 9530 (Intel i7-13700H, RTX 4050, 32GB, 1TB)",
        "cpu": "Intel Core i7-13700H",
        "cpu_generation": "13th Gen Intel",
        "ram_gb": 32,
        "storage_gb": 1024,
        "storage_type": "SSD",
        "gpu": "NVIDIA RTX 4050",
        "display_size": 15.6,
        "display_resolution": "3456x2160",
        "condition": "Excellent",
        "warranty_months": 12,
        "price": 119999,
        "original_price": 219999,
        "discount": 45,
        "stock_status": "out_of_stock",
        "product_url": "https://www.delloutlet.in/xps-15-9530",
        "image_url": "https://picsum.photos/seed/xps1/400/300",
    },
    {
        "store_id": 3,
        "brand": "Dell",
        "model": "Latitude 5430",
        "product_name": "Latitude 5430 (Intel i5-1235U, 8GB, 256GB)",
        "cpu": "Intel Core i5-1235U",
        "cpu_generation": "12th Gen Intel",
        "ram_gb": 8,
        "storage_gb": 256,
        "storage_type": "SSD",
        "gpu": "Intel Iris Xe",
        "display_size": 14.0,
        "display_resolution": "1920x1080",
        "condition": "Good",
        "warranty_months": 3,
        "price": 34999,
        "original_price": 65000,
        "discount": 46,
        "stock_status": "in_stock",
        "product_url": "https://www.delloutlet.in/latitude-5430",
        "image_url": "https://picsum.photos/seed/latitude2/400/300",
    },
    {
        "store_id": 4,
        "brand": "HP",
        "model": "EliteBook 840 G10",
        "product_name": "EliteBook 840 G10 (Intel i7-1365U, 16GB, 512GB)",
        "cpu": "Intel Core i7-1365U",
        "cpu_generation": "13th Gen Intel",
        "ram_gb": 16,
        "storage_gb": 512,
        "storage_type": "SSD",
        "gpu": "Intel Iris Xe",
        "display_size": 14.0,
        "display_resolution": "1920x1200",
        "condition": "Excellent",
        "warranty_months": 12,
        "price": 69999,
        "original_price": 129999,
        "discount": 46,
        "stock_status": "in_stock",
        "product_url": "https://www.hprenew.in/elitebook-840-g10",
        "image_url": "https://picsum.photos/seed/elitebook1/400/300",
    },
    {
        "store_id": 4,
        "brand": "HP",
        "model": "ProBook 450 G10",
        "product_name": "ProBook 450 G10 (Intel i5-1335U, 16GB, 512GB)",
        "cpu": "Intel Core i5-1335U",
        "cpu_generation": "13th Gen Intel",
        "ram_gb": 16,
        "storage_gb": 512,
        "storage_type": "SSD",
        "gpu": "Intel Iris Xe",
        "display_size": 15.6,
        "display_resolution": "1920x1080",
        "condition": "Very Good",
        "warranty_months": 6,
        "price": 44999,
        "original_price": 79999,
        "discount": 44,
        "stock_status": "in_stock",
        "product_url": "https://www.hprenew.in/probook-450-g10",
        "image_url": "https://picsum.photos/seed/probook1/400/300",
    },
    {
        "store_id": 4,
        "brand": "HP",
        "model": "Spectre x360 14",
        "product_name": "Spectre x360 14 (Intel i7-1355U, 16GB, 1TB, OLED)",
        "cpu": "Intel Core i7-1355U",
        "cpu_generation": "13th Gen Intel",
        "ram_gb": 16,
        "storage_gb": 1024,
        "storage_type": "SSD",
        "gpu": "Intel Iris Xe",
        "display_size": 14.0,
        "display_resolution": "2880x1800",
        "condition": "Excellent",
        "warranty_months": 12,
        "price": 94999,
        "original_price": 169999,
        "discount": 44,
        "stock_status": "out_of_stock",
        "product_url": "https://www.hprenew.in/spectre-x360-14",
        "image_url": "https://picsum.photos/seed/spectre1/400/300",
    },
    {
        "store_id": 5,
        "brand": "Apple",
        "model": "MacBook Air M2",
        "product_name": "MacBook Air M2 (2023) - 8GB/256GB",
        "cpu": "Apple M2",
        "cpu_generation": "Apple M2",
        "ram_gb": 8,
        "storage_gb": 256,
        "storage_type": "SSD",
        "gpu": "Apple M2 (8-core)",
        "display_size": 13.6,
        "display_resolution": "2560x1664",
        "condition": "Excellent",
        "warranty_months": 6,
        "price": 69999,
        "original_price": 114999,
        "discount": 39,
        "stock_status": "in_stock",
        "product_url": "https://www.amazon.in/renewed/macbook-air-m2",
        "image_url": "https://picsum.photos/seed/macbook1/400/300",
    },
    {
        "store_id": 6,
        "brand": "Samsung",
        "model": "Galaxy Book3 Pro",
        "product_name": "Galaxy Book3 Pro (Intel i5-1340P, 16GB, 512GB)",
        "cpu": "Intel Core i5-1340P",
        "cpu_generation": "13th Gen Intel",
        "ram_gb": 16,
        "storage_gb": 512,
        "storage_type": "SSD",
        "gpu": "Intel Iris Xe",
        "display_size": 16.0,
        "display_resolution": "2880x1800",
        "condition": "Very Good",
        "warranty_months": 6,
        "price": 54999,
        "original_price": 94999,
        "discount": 42,
        "stock_status": "in_stock",
        "product_url": "https://www.flipkart.com/refurbished/galaxy-book3-pro",
        "image_url": "https://picsum.photos/seed/galaxy1/400/300",
    },
]


async def seed():
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        now = datetime.now(timezone.utc)

        for i, p in enumerate(PRODUCTS):
            product = Product(**{k: v for k, v in p.items() if k != "images"})
            session.add(product)
            await session.flush()

            price_entry = PriceHistory(
                product_id=product.id,
                price=p["price"],
                timestamp=now - timedelta(days=30),
            )
            session.add(price_entry)

            price_entry2 = PriceHistory(
                product_id=product.id,
                price=p["price"] * random.uniform(1.05, 1.15),
                timestamp=now - timedelta(days=15),
            )
            session.add(price_entry2)

            price_entry3 = PriceHistory(
                product_id=product.id,
                price=p["price"],
                timestamp=now - timedelta(days=1),
            )
            session.add(price_entry3)

            stock_entry = StockHistory(
                product_id=product.id,
                stock_status=p["stock_status"],
                timestamp=now - timedelta(days=1),
            )
            session.add(stock_entry)

            if p.get("image_url"):
                image = Image(
                    product_id=product.id,
                    url=p["image_url"],
                    position=0,
                )
                session.add(image)

            product.last_seen = now
            product.last_updated = now
            product.first_seen = now - timedelta(days=30)

        await session.commit()
        print(f"Seeded {len(PRODUCTS)} products with price and stock history")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
