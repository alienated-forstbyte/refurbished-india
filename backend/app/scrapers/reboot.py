import logging

from app.scrapers.shopify_base import ShopifyBaseScraper

logger = logging.getLogger(__name__)


class RebootScraper(ShopifyBaseScraper):
    name = "reboot"
    shop_domain = "estore.reboot.co.in"