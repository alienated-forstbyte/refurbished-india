import asyncio
import logging
from datetime import datetime, timezone

from celery import Celery
from sqlalchemy import select

from app.config import settings
from app.database import async_session_factory
from app.models.store import Store
from app.models.scrape_log import ScrapeLog
from app.models.product import Product
from app.models.price_history import PriceHistory
from app.models.stock_history import StockHistory
from app.models.image import Image
from app.scrapers import (
    RebootScraper,
    EPWIndiaScraper,
    EFurbishedScraper,
    CashifyScraper,
    EzyRefurbScraper,
    LenovoScraper,
    AsusScraper,
    DellScraper,
    HPRefurbScraper,
)
from app.scrapers.base import ProductSchema
from app.services.normalizer import ProductNormalizer
from app.services.change_detector import ChangeDetector, ChangeEvent
from app.services.notifier import Notifier
from app.services.deal_scorer import refresh_deal_scores
from app.models.alert import Alert
from app.models.notification_history import NotificationHistory

logger = logging.getLogger(__name__)

celery_app = Celery(
    "refurbhub",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    beat_schedule={
        "scrape-all-stores": {
            "task": "app.tasks.scrape_all_stores",
            "schedule": settings.scheduler_interval_minutes * 60,
        },
        "refresh-deal-scores": {
            "task": "app.tasks.refresh_deal_scores_task",
            "schedule": 1800,
        },
    },
)

SCRAPER_MAP: dict[str, type] = {
    "Reboot Estore": RebootScraper,
    "EPW India": EPWIndiaScraper,
    "e-furbished": EFurbishedScraper,
    "Cashify": CashifyScraper,
    "EzyRefurb": EzyRefurbScraper,
    "Lenovo Outlet": LenovoScraper,
    "Asus Outlet": AsusScraper,
    "Dell Outlet": DellScraper,
    "HP Renew": HPRefurbScraper,
}

normalizer = ProductNormalizer()
change_detector = ChangeDetector()


async def _upsert_product(session, schema: ProductSchema, now: datetime) -> Product | None:
    if not schema.product_url:
        return None

    result = await session.execute(
        select(Product).where(
            Product.store_id == schema.store_id,
            Product.product_url == schema.product_url,
        )
    )
    product = result.scalar_one_or_none()

    if product:
        old_price = product.price
        old_stock = product.stock_status

        product.brand = schema.brand
        product.model = schema.model
        product.product_name = schema.product_name
        product.cpu = schema.cpu
        product.cpu_generation = schema.cpu_generation
        product.ram_gb = schema.ram_gb
        product.storage_gb = schema.storage_gb
        product.storage_type = schema.storage_type
        product.gpu = schema.gpu
        product.display_size = schema.display_size
        product.display_resolution = schema.display_resolution
        product.condition = schema.condition
        product.warranty_months = schema.warranty_months
        product.price = schema.price
        product.original_price = schema.original_price
        product.discount = schema.discount
        product.currency = schema.currency
        product.stock_status = schema.stock_status
        product.image_url = schema.image_url
        product.last_seen = now

        if old_price != schema.price and schema.price is not None:
            session.add(PriceHistory(product_id=product.id, price=schema.price))
        if old_stock != schema.stock_status:
            session.add(StockHistory(product_id=product.id, stock_status=schema.stock_status))
    else:
        product = Product(
            store_id=schema.store_id,
            brand=schema.brand,
            model=schema.model,
            product_name=schema.product_name,
            cpu=schema.cpu,
            cpu_generation=schema.cpu_generation,
            ram_gb=schema.ram_gb,
            storage_gb=schema.storage_gb,
            storage_type=schema.storage_type,
            gpu=schema.gpu,
            display_size=schema.display_size,
            display_resolution=schema.display_resolution,
            condition=schema.condition,
            warranty_months=schema.warranty_months,
            price=schema.price,
            original_price=schema.original_price,
            discount=schema.discount,
            currency=schema.currency,
            stock_status=schema.stock_status,
            product_url=schema.product_url,
            image_url=schema.image_url,
        )
        session.add(product)
        await session.flush()

        if schema.price is not None:
            session.add(PriceHistory(product_id=product.id, price=schema.price))
        session.add(StockHistory(product_id=product.id, stock_status=schema.stock_status))

    await session.flush()

    if schema.images:
        await session.execute(
            __import__("sqlalchemy").delete(Image).where(Image.product_id == product.id)
        )
        for i, url in enumerate(schema.images):
            session.add(Image(product_id=product.id, url=url, position=i))

    return product


async def _run_scraper_for_store(scraper_cls: type, store_id: int, store_name: str):
    scraper = scraper_cls(store_id=store_id)
    start_time = datetime.now(timezone.utc)
    log_entry = ScrapeLog(
        store_id=store_id,
        start_time=start_time,
        status="running",
    )

    products: list[ProductSchema] = []
    errors: list[str] = []

    try:
        raw_products = await scraper.scrape_all()
        products = [normalizer.normalize(p) for p in raw_products if p is not None]
    except Exception as e:
        errors.append(str(e))
        logger.exception(f"[tasks] Scraper {store_name} failed: {e}")
    finally:
        await scraper.close()

    end_time = datetime.now(timezone.utc)
    duration_ms = int((end_time - start_time).total_seconds() * 1000)

    saved_count = 0
    events: list[ChangeEvent] = []
    async with async_session_factory() as session:
        try:
            result = await session.execute(
                select(Product).where(Product.store_id == store_id)
            )
            existing_products = result.scalars().all()
            existing_map = {p.product_url: ProductSchema(
                store_id=p.store_id,
                brand=p.brand,
                model=p.model,
                product_name=p.product_name,
                cpu=p.cpu,
                cpu_generation=p.cpu_generation,
                ram_gb=p.ram_gb,
                storage_gb=p.storage_gb,
                storage_type=p.storage_type,
                gpu=p.gpu,
                display_size=p.display_size,
                display_resolution=p.display_resolution,
                condition=p.condition,
                warranty_months=p.warranty_months,
                price=p.price,
                original_price=p.original_price,
                discount=p.discount,
                currency=p.currency,
                stock_status=p.stock_status,
                product_url=p.product_url,
                image_url=p.image_url,
            ) for p in existing_products if p.product_url}

            for schema in products:
                try:
                    p = await _upsert_product(session, schema, end_time)
                    if p:
                        saved_count += 1
                except Exception as e:
                    errors.append(f"Failed to save product {schema.product_url}: {e}")
                    logger.exception(f"[tasks] Product save error: {e}")

            events = await change_detector.detect(products, existing_map)

            log_entry.end_time = end_time
            log_entry.duration_ms = duration_ms
            log_entry.products_found = saved_count
            log_entry.errors = "; ".join(errors) if errors else None
            log_entry.status = "completed" if not errors else "partial" if saved_count > 0 else "failed"
            session.add(log_entry)

            store = await session.get(Store, store_id)
            if store:
                store.last_scrape = end_time

            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.exception(f"[tasks] Failed to save scrape results for {store_name}: {e}")

    logger.info(
        f"[tasks] {store_name}: {saved_count}/{len(products)} products saved in {duration_ms}ms"
        f"{' with errors: ' + str(errors) if errors else ''}"
    )

    if events:
        await _notify_events(events, store_id)

    return products


async def _notify_events(events: list[ChangeEvent], store_id: int):
    async with async_session_factory() as session:
        result = await session.execute(
            select(Alert).where(Alert.enabled == True)
        )
        alerts = result.scalars().all()

    notifier = Notifier()
    for event in events:
        product = event.product
        for alert in alerts:
            if alert.brand and product.brand and alert.brand.lower() not in product.brand.lower():
                continue
            if alert.max_price and product.price and product.price > alert.max_price:
                continue
            if alert.ram and product.ram_gb and product.ram_gb < alert.ram:
                continue
            if alert.cpu and product.cpu and alert.cpu.lower() not in product.cpu.lower():
                continue
            if alert.gpu and product.gpu and alert.gpu.lower() not in product.gpu.lower():
                continue

            event_type = event.type.value
            if event_type in ("price_changed",) and not alert.notify_price:
                continue
            if event_type in ("back_in_stock", "out_of_stock") and not alert.notify_stock:
                continue

            await notifier.send_notification(event, channels=["log"])
            async with async_session_factory() as session:
                try:
                    session.add(NotificationHistory(
                        alert_id=alert.id,
                        product_id=0,
                        type=event_type,
                        status="sent",
                    ))
                    await session.commit()
                except Exception:
                    await session.rollback()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def scrape_all_stores(self):
    async def _run():
        async with async_session_factory() as session:
            result = await session.execute(
                select(Store).where(Store.enabled == True)
            )
            stores = result.scalars().all()

        all_products = 0
        for store in stores:
            scraper_cls = SCRAPER_MAP.get(store.name)
            if not scraper_cls:
                logger.warning(f"[tasks] No scraper for store: {store.name} (ID: {store.id})")
                continue
            products = await _run_scraper_for_store(scraper_cls, store.id, store.name)
            all_products += len(products)

        logger.info(f"[tasks] All stores done: {all_products} total products")
        return all_products

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.exception("[tasks] scrape_all_stores failed")
        raise self.retry(exc=exc)


@celery_app.task
def scrape_store(store_name: str):
    async def _run():
        async with async_session_factory() as session:
            result = await session.execute(
                select(Store).where(Store.name == store_name, Store.enabled == True)
            )
            store = result.scalar_one_or_none()

        if not store:
            logger.error(f"[tasks] Store not found or disabled: {store_name}")
            return

        scraper_cls = SCRAPER_MAP.get(store.name)
        if not scraper_cls:
            logger.error(f"[tasks] No scraper for store: {store.name}")
            return

        await _run_scraper_for_store(scraper_cls, store.id, store.name)

    asyncio.run(_run())


@celery_app.task
def refresh_deal_scores_task():
    async def _run():
        async with async_session_factory() as session:
            await refresh_deal_scores(session)

    asyncio.run(_run())
