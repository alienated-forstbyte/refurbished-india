# Scrapers
#
# Functional:
#   RebootScraper     - Shopify (estore.reboot.co.in)
#   EPWIndiaScraper   - Shopify (epwindia.com)
#   EFurbishedScraper - Shopify (e-furbished.in)
#   CashifyScraper    - Custom (cashify.in, RSC push data)
#   EzyRefurbScraper  - Shopify (ezyrefurb.com)
#
# Stubs (need implementation):
#   LenovoScraper     - Playwright needed for JS-heavy pages
#   AsusScraper       - httpx + direct URL discovery
#   DellScraper       - Dell Outlet scraping
#   HPRefurbScraper   - HP Renew scraping

from app.scrapers.base import BaseScraper, ProductSchema
from app.scrapers.shopify_base import ShopifyBaseScraper
from app.scrapers.reboot import RebootScraper
from app.scrapers.epw import EPWIndiaScraper
from app.scrapers.efurbished import EFurbishedScraper
from app.scrapers.cashify import CashifyScraper
from app.scrapers.ezyrefurb import EzyRefurbScraper

__all__ = [
    "BaseScraper",
    "ProductSchema",
    "ShopifyBaseScraper",
    "RebootScraper",
    "EPWIndiaScraper",
    "EFurbishedScraper",
    "CashifyScraper",
    "EzyRefurbScraper",
]
