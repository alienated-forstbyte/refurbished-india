import logging
from app.scrapers.base import BaseScraper, ProductSchema

logger = logging.getLogger(__name__)


class AsusScraper(BaseScraper):
    name = "asus"

    async def discover_products(self) -> list[str]:
        # TODO: Implement Asus Refurbished discovery
        # Asus hides some products behind direct URLs
        logger.info("[asus] discover_products not yet implemented")
        return []

    async def fetch_product(self, url: str) -> str:
        # TODO: Use httpx to fetch Asus product pages
        return ""

    async def normalize(self, raw_data: str, url: str) -> ProductSchema | None:
        # TODO: Parse Asus product page structure
        return None
