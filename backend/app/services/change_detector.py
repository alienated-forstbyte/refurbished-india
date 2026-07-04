import logging
from dataclasses import dataclass
from enum import Enum

from app.scrapers.base import ProductSchema

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    NEW_PRODUCT = "new_product"
    PRICE_CHANGED = "price_changed"
    BACK_IN_STOCK = "back_in_stock"
    OUT_OF_STOCK = "out_of_stock"
    REMOVED = "removed"


@dataclass
class ChangeEvent:
    type: ChangeType
    product: ProductSchema
    old_price: float | None = None
    new_price: float | None = None
    old_stock: str | None = None
    new_stock: str | None = None


class ChangeDetector:
    async def detect(self, scraped: list[ProductSchema], existing: dict[str, ProductSchema]) -> list[ChangeEvent]:
        events: list[ChangeEvent] = []

        scraped_urls = {p.product_url for p in scraped if p.product_url}
        existing_urls = set(existing.keys())

        for product in scraped:
            if not product.product_url:
                continue
            if product.product_url not in existing:
                events.append(ChangeEvent(type=ChangeType.NEW_PRODUCT, product=product))
                logger.info(f"New product detected: {product.product_name}")
            else:
                old = existing[product.product_url]
                if old.price != product.price:
                    events.append(
                        ChangeEvent(
                            type=ChangeType.PRICE_CHANGED,
                            product=product,
                            old_price=old.price,
                            new_price=product.price,
                        )
                    )
                    logger.info(f"Price changed: {product.product_name} ₹{old.price} → ₹{product.price}")
                if old.stock_status != product.stock_status:
                    ct = ChangeType.BACK_IN_STOCK if product.stock_status == "in_stock" else ChangeType.OUT_OF_STOCK
                    events.append(
                        ChangeEvent(
                            type=ct,
                            product=product,
                            old_stock=old.stock_status,
                            new_stock=product.stock_status,
                        )
                    )
                    logger.info(f"Stock changed: {product.product_name} {old.stock_status} → {product.stock_status}")

        for url in existing_urls - scraped_urls:
            events.append(
                ChangeEvent(
                    type=ChangeType.REMOVED,
                    product=existing[url],
                    old_stock=existing[url].stock_status,
                    new_stock="removed",
                )
            )
            logger.info(f"Product removed: {existing[url].product_name}")

        return events
