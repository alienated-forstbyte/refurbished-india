import logging

from app.scrapers.shopify_base import ShopifyBaseScraper

logger = logging.getLogger(__name__)

NON_LAPTOP_KW = [
    "desktop", "tower", "tablet", "monitor", "keyboard", "mouse",
    "charger", "adapter", "server", "mini pc", "cable", "headphone",
    "speaker", "watch", "bag", "case", "ssd", "hard disk", "external",
    "pendrive", "usb", "ram", "printer", "all-in-one", "workstation",
    "led monitor", "lcd monitor",
]

LAPTOP_KW = [
    "laptop", "notebook", "macbook", "thinkpad", "elitebook", "probook",
    "latitude", "xps", "inspiron", "vostro", "precision", "chromebook",
    "vivobook", "zenbook", "tuf gaming", "rog", "legion", "ideapad",
    "yoga", "thinkbook", "surface", "spectre", "envy", "pavilion",
    "omen", "zbook", "swift", "nitro", "predator", "aspire",
    "travelmate", "galaxy book", "matebook", "redmibook",
]


class EPWIndiaScraper(ShopifyBaseScraper):
    name = "epw_india"
    shop_domain = "www.epwindia.com"

    def _normalize_product(self, item: dict, base_url: str):
        product_type = (item.get("product_type") or "").lower()
        title = item.get("title", "")

        if product_type == "laptop":
            return super()._normalize_product(item, base_url)

        if product_type in ("desktop", "computer"):
            return None

        title_lower = title.lower()
        has_laptop_kw = any(kw in title_lower for kw in LAPTOP_KW)
        has_non_laptop = any(kw in title_lower for kw in NON_LAPTOP_KW)

        if has_laptop_kw and not has_non_laptop:
            return super()._normalize_product(item, base_url)

        return None