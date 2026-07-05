import logging
from app.scrapers.base import BaseScraper, ProductSchema

logger = logging.getLogger(__name__)


class LenovoScraper(BaseScraper):
    name = "lenovo"

    async def discover_products(self) -> list[str]:
        logger.info("[lenovo] Stub — needs Playwright-based discovery for JS-heavy pages with pagination")
        return []

    async def fetch_product(self, url: str) -> str:
        return ""

    async def normalize(self, raw_data: str, url: str) -> ProductSchema | None:
        return None
