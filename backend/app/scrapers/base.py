import asyncio
import random
import logging
from abc import ABC
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ProductSchema:
    store_id: int | None = None
    brand: str | None = None
    model: str | None = None
    product_name: str | None = None
    cpu: str | None = None
    cpu_generation: str | None = None
    ram_gb: int | None = None
    storage_gb: int | None = None
    storage_type: str | None = None
    gpu: str | None = None
    display_size: float | None = None
    display_resolution: str | None = None
    condition: str | None = None
    warranty_months: int | None = None
    price: float | None = None
    original_price: float | None = None
    discount: float | None = None
    currency: str = "INR"
    stock_status: str = "unknown"
    product_url: str | None = None
    image_url: str | None = None
    images: list[str] = field(default_factory=list)


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


class BaseScraper(ABC):
    name: str = "base"
    rate_limit: float = 1.0
    max_retries: int = 3
    store_id: int | None = None

    def __init__(self, store_id: int | None = None):
        self._last_request_time: float = 0.0
        if store_id is not None:
            self.store_id = store_id

    async def rate_limit_wait(self):
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self.rate_limit:
            delay = self.rate_limit - elapsed + random.uniform(0.1, 0.5)
            await asyncio.sleep(delay)
        self._last_request_time = asyncio.get_event_loop().time()

    def get_headers(self) -> dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
        }

    async def discover_products(self) -> list[str]:
        return []

    async def fetch_product(self, url: str) -> str:
        return ""

    async def normalize(self, raw_data: str, url: str) -> ProductSchema | None:
        return None

    async def save(self, product: ProductSchema):
        pass  # Implemented by services, not scrapers

    async def scrape_all(self) -> list[ProductSchema]:
        discovered = []
        try:
            discovered = await self.discover_products()
            logger.info(f"[{self.name}] Discovered {len(discovered)} products")
        except Exception as e:
            logger.error(f"[{self.name}] Discovery failed: {e}")
            return []

        products: list[ProductSchema] = []
        for url in discovered:
            await self.rate_limit_wait()
            for attempt in range(self.max_retries):
                try:
                    raw = await self.fetch_product(url)
                    normalized = await self.normalize(raw, url)
                    if normalized:
                        products.append(normalized)
                    break
                except Exception as e:
                    logger.warning(f"[{self.name}] Attempt {attempt + 1}/{self.max_retries} failed for {url}: {e}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                    else:
                        logger.error(f"[{self.name}] All retries exhausted for {url}")

        logger.info(f"[{self.name}] Successfully scraped {len(products)}/{len(discovered)} products")
        return products
