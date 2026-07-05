import logging

from app.scrapers.shopify_base import ShopifyBaseScraper

logger = logging.getLogger(__name__)


class EzyRefurbScraper(ShopifyBaseScraper):
    name = "ezy_refurb"
    shop_domain = "www.ezyrefurb.com"