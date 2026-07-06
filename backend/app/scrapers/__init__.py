from app.scrapers.base import BaseScraper, ProductSchema
from app.scrapers.shopify_base import ShopifyBaseScraper
from app.scrapers.reboot import RebootScraper
from app.scrapers.epw import EPWIndiaScraper
from app.scrapers.efurbished import EFurbishedScraper
from app.scrapers.cashify import CashifyScraper
from app.scrapers.ezyrefurb import EzyRefurbScraper
from app.scrapers.lenovo import LenovoScraper
from app.scrapers.asus import AsusScraper
from app.scrapers.dell import DellScraper
from app.scrapers.hp import HPRefurbScraper

__all__ = [
    "BaseScraper",
    "ProductSchema",
    "ShopifyBaseScraper",
    "RebootScraper",
    "EPWIndiaScraper",
    "EFurbishedScraper",
    "CashifyScraper",
    "EzyRefurbScraper",
    "LenovoScraper",
    "AsusScraper",
    "DellScraper",
    "HPRefurbScraper",
]
