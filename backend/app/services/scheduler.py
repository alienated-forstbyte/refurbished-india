import logging
import time
from datetime import datetime, timezone

from app.scrapers.base import BaseScraper
from app.services.normalizer import ProductNormalizer
from app.services.change_detector import ChangeDetector

logger = logging.getLogger(__name__)


class ScrapeScheduler:
    def __init__(self):
        self.normalizer = ProductNormalizer()
        self.change_detector = ChangeDetector()

    async def run_scraper(self, scraper: BaseScraper):
        start = time.monotonic()
        logger.info(f"[scheduler] Starting scrape: {scraper.name}")

        try:
            products = await scraper.scrape_all()
            normalized = [self.normalizer.normalize(p) for p in products if p is not None]
            elapsed = time.monotonic() - start
            logger.info(
                f"[scheduler] Finished {scraper.name}: "
                f"{len(normalized)} products in {elapsed:.1f}s"
            )
            return normalized
        except Exception as e:
            elapsed = time.monotonic() - start
            logger.error(f"[scheduler] Failed {scraper.name} after {elapsed:.1f}s: {e}")
            return []
