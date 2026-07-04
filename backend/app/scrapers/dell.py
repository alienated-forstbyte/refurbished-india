import logging
from app.scrapers.base import BaseScraper, ProductSchema

logger = logging.getLogger(__name__)


class DellScraper(BaseScraper):
    name = "dell"

    async def discover_products(self) -> list[str]:
        # TODO: Implement Dell Outlet discovery
        logger.info("[dell] discover_products not yet implemented")
        return []

    async def fetch_product(self, url: str) -> str:
        return ""

    async def normalize(self, raw_data: str, url: str) -> ProductSchema | None:
        return None
