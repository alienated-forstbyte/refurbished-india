import logging
from app.scrapers.base import BaseScraper, ProductSchema

logger = logging.getLogger(__name__)


class LenovoScraper(BaseScraper):
    name = "lenovo"

    async def discover_products(self) -> list[str]:
        # TODO: Implement Playwright-based discovery for Lenovo Refurbished
        # Lenovo uses dynamic JS-loaded pages with pagination
        # Return list of product URLs
        logger.info("[lenovo] discover_products not yet implemented")
        return []

    async def fetch_product(self, url: str) -> str:
        # TODO: Use Playwright to render JS-heavy pages
        return ""

    async def normalize(self, raw_data: str, url: str) -> ProductSchema | None:
        # TODO: Parse Lenovo's product page structure
        return None
