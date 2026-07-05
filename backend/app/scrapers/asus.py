import logging
from app.scrapers.base import BaseScraper, ProductSchema

logger = logging.getLogger(__name__)


class AsusScraper(BaseScraper):
    name = "asus"

    async def discover_products(self) -> list[str]:
        logger.info("[asus] Stub — needs httpx-based discovery; some products are hidden behind direct URLs")
        return []

    async def fetch_product(self, url: str) -> str:
        return ""

    async def normalize(self, raw_data: str, url: str) -> ProductSchema | None:
        return None
