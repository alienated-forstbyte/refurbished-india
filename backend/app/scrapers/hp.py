import asyncio
import logging
import re

import httpx
from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper, ProductSchema

logger = logging.getLogger(__name__)

STORE_BASE = "https://www.hp.com/in-en/shop"
LAPTOPS_URL = f"{STORE_BASE}/laptops-tablets.html"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
}

MAX_DETAIL_PAGES = 20


class HPRefurbScraper(BaseScraper):
    name = "hp_renew"
    rate_limit = 1.5

    def __init__(self, store_id: int | None = None):
        super().__init__(store_id)
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers=HEADERS,
                timeout=30.0,
                follow_redirects=True,
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def scrape_all(self) -> list[ProductSchema]:
        client = await self._get_client()
        products: list[ProductSchema] = []

        listing_products = await self._scrape_listings(client)
        products.extend(listing_products)

        detail_tasks = []
        for p in listing_products[:MAX_DETAIL_PAGES]:
            if p.product_url:
                detail_tasks.append(self._enrich_product(client, p))

        if detail_tasks:
            enriched = await asyncio.gather(*detail_tasks, return_exceptions=True)
            for i, result in enumerate(enriched):
                if isinstance(result, ProductSchema) and i < len(products):
                    products[i] = result

        logger.info(
            f"[{self.name}] Total: {len(products)} products "
            f"({len(detail_tasks)} enriched from detail pages)"
        )
        return products

    async def _scrape_listings(self, client: httpx.AsyncClient) -> list[ProductSchema]:
        products: list[ProductSchema] = []
        seen_urls: set[str] = set()

        for page in range(1, 6):
            await self.rate_limit_wait()
            url = f"{LAPTOPS_URL}?product_list_limit=36&product_list_order=price_asc&p={page}"
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                html = resp.text
            except Exception as e:
                logger.warning(f"[{self.name}] Listing page {page} failed: {e}")
                break

            soup = BeautifulSoup(html, "html.parser")
            items = soup.select("li.product-item")
            if not items:
                break

            for item in items:
                try:
                    product = self._parse_listing_item(item)
                    if product and product.product_url and product.product_url not in seen_urls:
                        seen_urls.add(product.product_url)
                        products.append(product)
                except Exception as e:
                    logger.debug(f"[{self.name}] Parse item error: {e}")

            logger.info(
                f"[{self.name}] Page {page}: {len(items)} items "
                f"(total: {len(products)})"
            )

            if len(items) < 5:
                break

        return products

    def _parse_listing_item(self, item) -> ProductSchema | None:
        name_el = item.select_one(
            ".product-item-name a, .product.name a, "
            "a.product-item-link, strong.product.name a, "
            "[class*=product-item-link]"
        )
        if not name_el:
            return None

        product_name = name_el.get_text(strip=True)
        if not product_name:
            return None

        product_url = name_el.get("href", "")
        if product_url and not product_url.startswith("http"):
            product_url = f"{STORE_BASE}{product_url}" if product_url.startswith("/") else product_url

        price = None
        price_el = item.select_one(
            ".price-wrapper [data-price-type=finalPrice], "
            ".price-wrapper, "
            "span.price, "
            "[class*=price]"
        )
        if price_el:
            price_text = price_el.get_text(strip=True)
            m = re.search(r"₹?\s*([\d,]+\.?\d*)", price_text)
            if m:
                try:
                    price = float(m.group(1).replace(",", ""))
                except ValueError:
                    pass

        image_url = None
        img = item.select_one("img.product-image-photo, img[src*=catalog]")
        if img:
            src = img.get("src", "")
            if src and "data:image" not in src:
                image_url = src

        brand = "HP"
        model = self._extract_model(product_name)

        display_size = self._extract_display(product_name)

        ram_gb = self._extract_ram_from_name(product_name)

        slug = re.sub(r"[^a-z0-9]+", "-", product_name.lower())
        slug = re.sub(r"-+-", "-", slug).strip("-")
        if not product_url or "shop/" not in product_url:
            product_url = f"{STORE_BASE}/{slug}.html"

        return ProductSchema(
            store_id=self.store_id,
            brand=brand,
            model=model,
            product_name=product_name,
            display_size=display_size,
            ram_gb=ram_gb,
            condition="New",
            warranty_months=12,
            price=price,
            currency="INR",
            stock_status="in_stock" if price else "unknown",
            product_url=product_url,
            image_url=image_url,
        )

    async def _enrich_product(
        self, client: httpx.AsyncClient, base: ProductSchema
    ) -> ProductSchema:
        if not base.product_url:
            return base

        await self.rate_limit_wait()
        try:
            resp = await client.get(base.product_url)
            resp.raise_for_status()
            html = resp.text
        except Exception:
            return base

        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text("\n", strip=True)

        cpu = self._extract_cpu(text)
        ram_gb = self._extract_ram(text) or base.ram_gb
        storage_gb, storage_type = self._extract_storage(text)
        gpu = self._extract_gpu(text)
        display_size = self._extract_display(text) or base.display_size
        model = self._extract_model(text) or base.model

        return ProductSchema(
            store_id=base.store_id,
            brand=base.brand,
            model=model,
            product_name=base.product_name,
            cpu=cpu,
            ram_gb=ram_gb,
            storage_gb=storage_gb,
            storage_type=storage_type,
            gpu=gpu,
            display_size=display_size,
            condition="New",
            warranty_months=12,
            price=base.price,
            currency="INR",
            stock_status=base.stock_status,
            product_url=base.product_url,
            image_url=base.image_url or base.image_url,
        )

    def _extract_model(self, name: str) -> str | None:
        patterns = [
            r"(EliteBook\s+\w+\s*\d*)",
            r"(ProBook\s+\w+\s*\d*)",
            r"(ZBook\s+\w+\s*\d*)",
            r"(Pavilion\s+\w+\s*\d*)",
            r"(Envy\s+\w+\s*\d*)",
            r"(Spectre\s+\w+\s*\d*)",
            r"(Omen\s+\w+\s*\d*)",
            r"(Victus\s+\w+\s*\d*)",
            r"(OmniBook\s+\w+\s*\d*)",
            r"(HP\s+\d+\s+\w+)",
            r"(HP\s+\w+\s+\d+)",
        ]
        for p in patterns:
            m = re.search(p, name, re.IGNORECASE)
            if m:
                return m.group(1)
        return None

    def _extract_cpu(self, text: str) -> str | None:
        patterns = [
            r"(Intel\s+Core\s+(?:Ultra\s+)?\d+\s*\w*\s*\d{4,5}[A-Z]*(?:\s+processor)?)",
            r"(Intel\s+Core\s+i[3579][-\s]\d{4,5}[A-Z]*(?:\s+processor)?)",
            r"(AMD\s+Ryzen\s+\d\s*\w*\s*\d{4,5}[A-Z]?(?:\s+processor)?)",
            r"(Intel\s+Core\s+\d+(?:\s+processor)?)",
            r"(Intel\s+[iI]\d[-\s]\d{4,5}(?:\s+processor)?)",
            r"(Snapdragon\s+X\s+\w+)",
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(1).strip().removesuffix(" processor").strip()
        return None

    def _extract_ram(self, text: str) -> int | None:
        valid_rams = {2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 128}
        patterns = [
            r"(\d+)\s*GB\s*(?:LPDDR|DDR)\w*\s*(?:RAM)?",
            r"(\d+)\s*GB\s+(?:RAM|Memory|memory)",
            r"(\d+)\s+GB\s+of\s+(?:RAM|memory)",
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                try:
                    val = int(m.group(1))
                    if val in valid_rams:
                        return val
                except ValueError:
                    pass
        return None

    def _extract_ram_from_name(self, name: str) -> int | None:
        valid_rams = {2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 128}
        m = re.search(r"(\d+)\s*GB\s*(?:RAM|Memory)", name, re.IGNORECASE)
        if m:
            try:
                val = int(m.group(1))
                if val in valid_rams:
                    return val
            except ValueError:
                pass
        return None

    def _extract_storage(self, text: str) -> tuple[int | None, str | None]:
        m = re.search(r"(\d+)\s*(GB|TB)\s*(SSD|HDD|NVMe|Hard Drive)", text, re.IGNORECASE)
        if m:
            size = int(m.group(1))
            unit = m.group(2).upper()
            stype = "SSD" if "SSD" in text.upper() or "NVMe" in text.upper() else "HDD"
            if unit == "TB":
                size *= 1024
            return size, stype
        m = re.search(r"(\d+)\s*GB\s+SSD", text, re.IGNORECASE)
        if m:
            return int(m.group(1)), "SSD"
        return None, None

    def _extract_gpu(self, text: str) -> str | None:
        patterns = [
            r"(NVIDIA\s+GeForce\s+RTX\s+\d+\s*\w*)",
            r"(NVIDIA\s+\w+\s+\w*\d*)",
            r"(Intel\s+(?:UHD|Iris|Arc)\s+\w*)",
            r"(AMD\s+Radeon\s+\w+\s*\w*)",
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return None

    def _extract_display(self, text: str) -> float | None:
        m = re.search(r"(\d+\.?\d*)\s*(?:inch|\"|in\b)", text, re.IGNORECASE)
        if m:
            try:
                val = float(m.group(1))
                if 10 <= val <= 20:
                    return val
            except ValueError:
                pass
        m = re.search(r"(\d+\.?\d*)\s*cm", text, re.IGNORECASE)
        if m:
            try:
                cm = float(m.group(1))
                if 25 <= cm <= 50:
                    return round(cm / 2.54, 1)
            except ValueError:
                pass
        return None
