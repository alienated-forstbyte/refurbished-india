import logging

from app.scrapers.shopify_base import ShopifyBaseScraper

logger = logging.getLogger(__name__)


class EFurbishedScraper(ShopifyBaseScraper):
    name = "e_furbished"
    shop_domain = "e-furbished.in"