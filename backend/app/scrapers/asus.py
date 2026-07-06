import asyncio
import logging
import re

import httpx
from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper, ProductSchema

logger = logging.getLogger(__name__)

OUTLET_URL = "https://www.asus.com/in/deals/outlet/"
STORE_BASE = "https://in.store.asus.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
}

STORE_HEADERS = {
    **HEADERS,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.asus.com/in/deals/outlet/",
}


class AsusScraper(BaseScraper):
    name = "asus"
    rate_limit = 2.0

    def __init__(self, store_id: int | None = None):
        super().__init__(store_id)
        self._client: httpx.AsyncClient | None = None
        self._store_client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers=HEADERS,
                timeout=30.0,
                follow_redirects=True,
            )
        return self._client

    async def _get_store_client(self) -> httpx.AsyncClient:
        if self._store_client is None:
            self._store_client = httpx.AsyncClient(
                headers=STORE_HEADERS,
                timeout=15.0,
                follow_redirects=True,
                max_redirects=3,
            )
        return self._store_client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
        if self._store_client:
            await self._store_client.aclose()
            self._store_client = None

    async def scrape_all(self) -> list[ProductSchema]:
        client = await self._get_client()
        products: list[ProductSchema] = []

        await self.rate_limit_wait()
        try:
            resp = await client.get(OUTLET_URL)
            resp.raise_for_status()
            html = resp.text
        except Exception as e:
            logger.error(f"[{self.name}] Failed to fetch outlet page: {e}")
            return products

        soup = BeautifulSoup(html, "html.parser")
        cards = soup.find_all(
            "div", class_=lambda c: c and "ProductCardSimple__productCardContainer" in c
        )
        logger.info(f"[{self.name}] Found {len(cards)} product cards on outlet page")

        for card in cards:
            try:
                product = self._parse_card(card)
                if product:
                    products.append(product)
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to parse card: {e}")

        detail_tasks = []
        for p in products[:10]:
            if p.product_url and ("in.store.asus.com" in p.product_url or "asus.com/in" in p.product_url):
                detail_tasks.append(self._enrich_product(p))

        if detail_tasks:
            enriched = await asyncio.gather(*detail_tasks, return_exceptions=True)
            for i, result in enumerate(enriched):
                if isinstance(result, ProductSchema) and i < len(products):
                    products[i] = result

        logger.info(
            f"[{self.name}] Successfully scraped {len(products)} products "
            f"({sum(1 for p in products if p.cpu)} with CPU, "
            f"{sum(1 for p in products if p.ram_gb)} with RAM)"
        )
        return products

    async def _enrich_product(self, base: ProductSchema) -> ProductSchema:
        store_client = await self._get_store_client()
        url = base.product_url
        if not url:
            return base

        await self.rate_limit_wait()
        for retry in range(2):
            try:
                resp = await store_client.get(url)
                if resp.status_code == 403:
                    alt_urls = self._generate_alt_urls(base.product_name)
                    for alt in alt_urls:
                        try:
                            resp2 = await store_client.get(alt)
                            if resp2.status_code == 200:
                                resp = resp2
                                break
                        except Exception:
                            continue
                    if resp.status_code == 403:
                        break

                html = resp.text
                if len(html) < 500:
                    break

                soup = BeautifulSoup(html, "html.parser")
                text = soup.get_text("\n", strip=True)

                cpu = self._extract_cpu(base.product_name, text) or base.cpu
                ram_gb = self._extract_ram_from_text(text) or base.ram_gb
                storage_gb, storage_type = self._extract_storage_from_text(text)
                if not storage_gb:
                    storage_gb, storage_type = base.storage_gb, base.storage_type
                gpu = self._extract_gpu_from_text(text) or base.gpu
                display_size = self._extract_display_from_text(text) or base.display_size
                original_price = self._extract_original_price(text) or base.original_price

                return ProductSchema(
                    store_id=base.store_id,
                    brand=base.brand,
                    model=base.model,
                    product_name=base.product_name,
                    cpu=cpu,
                    ram_gb=ram_gb,
                    storage_gb=storage_gb,
                    storage_type=storage_type,
                    gpu=gpu,
                    display_size=display_size,
                    condition=base.condition,
                    warranty_months=base.warranty_months,
                    price=base.price,
                    original_price=original_price,
                    currency=base.currency,
                    stock_status=base.stock_status,
                    product_url=url,
                    image_url=base.image_url,
                )
            except Exception:
                continue

        return base

    def _generate_alt_urls(self, product_name: str) -> list[str]:
        slug = re.sub(r"[^a-z0-9]+", "-", product_name.lower())
        slug = re.sub(r"-+", "-", slug).strip("-")
        return [
            f"{STORE_BASE}/{slug}.html",
            f"{STORE_BASE}/catalog/product/view/",
        ]

    def _parse_card(self, card) -> ProductSchema | None:
        a_tag = card.find("a", href=re.compile(r"(?:refurbished-laptop|product)"))
        if not a_tag:
            a_tag = card.find("a", href=True)
        if not a_tag:
            return None

        product_url = a_tag.get("href", "")
        product_name = a_tag.get_text(strip=True)
        if not product_name or "(Refurbished Laptop)" not in product_name:
            img = card.find("img")
            if img and img.get("alt"):
                product_name = img["alt"]

        image_url = None
        img = card.find("img")
        if img and img.get("src"):
            src = img["src"]
            if src.startswith("//"):
                src = "https:" + src
            image_url = src

        price = None
        original_price = None
        price_el = self._find_text_by_pattern(
            card, r"(?:ProductCardSimple__priceDiscount|ProductCardSimple__regularPrice)"
        )
        if price_el:
            price_text = price_el.get_text(strip=True)
            price = self._parse_price(price_text)

        orig_el = self._find_text_by_pattern(
            card, r"ProductCardSimple__regularPrice"
        )
        if orig_el:
            orig_text = orig_el.get_text(strip=True)
            original_price = self._parse_price(orig_text)

        stock_status = "out_of_stock"
        for btn in card.find_all("a", href=True):
            btn_text = btn.get_text(strip=True).lower()
            if "buy" in btn_text and "notify" not in btn_text:
                stock_status = "in_stock"
                break

        desc_text = ""
        desc_el = self._find_text_by_pattern(
            card, r"ProductCardSimple__featureDescriptionRow"
        )
        if desc_el:
            for p in desc_el.find_all(["p", "span"]):
                text = p.get_text(strip=True)
                if text and len(text) > 30 and "Refurbished" not in text and "FAQ" not in text:
                    desc_text = text
                    break

        brand = "Asus"
        model = self._extract_model(product_name)
        cpu = self._extract_cpu(product_name, desc_text)
        ram_gb = self._extract_ram(product_name, desc_text)
        storage_gb, storage_type = self._extract_storage(product_name, desc_text)
        gpu = self._extract_gpu(product_name, desc_text)
        display_size = self._extract_display(product_name, desc_text)

        condition = "Refurbished"
        warranty_months = 12

        return ProductSchema(
            store_id=self.store_id,
            brand=brand,
            model=model,
            product_name=product_name,
            cpu=cpu,
            ram_gb=ram_gb,
            storage_gb=storage_gb,
            storage_type=storage_type,
            gpu=gpu,
            display_size=display_size,
            condition=condition,
            warranty_months=warranty_months,
            price=price,
            original_price=original_price,
            currency="INR",
            stock_status=stock_status,
            product_url=product_url,
            image_url=image_url,
        )

    def _find_text_by_pattern(self, card, pattern: str) -> object | None:
        result = card.find("div", class_=lambda c: c and re.search(pattern, str(c or "")))
        if result:
            return result
        result = card.find("span", class_=lambda c: c and re.search(pattern, str(c or "")))
        return result

    def _parse_price(self, text: str) -> float | None:
        cleaned = text.replace("₹", "").replace(",", "").replace(" ", "").strip()
        m = re.search(r"([\d]+\.?\d*)", cleaned)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                pass
        return None

    def _extract_model(self, name: str) -> str | None:
        patterns = [
            r"(Vivobook\s+\S+)",
            r"(Zenbook\s+\S+)",
            r"(ExpertBook\s+\S+)",
            r"(ROG\s+\S+\s+\S+)",
            r"(TUF\s+Gaming\s+\S+)",
            r"(ProArt\s+\S+)",
            r"(Chromebook\s+\S+)",
            r"(ROG\s+\S+)",
        ]
        for p in patterns:
            m = re.search(p, name, re.IGNORECASE)
            if m:
                return m.group(1)
        return None

    def _extract_cpu(self, name: str, desc: str) -> str | None:
        text = f"{name} {desc}"
        patterns = [
            r"(Intel\s+Core\s+(?:Ultra\s+)?\d+\s*\w*\s*\d{4,5}[A-Z]*)",
            r"(Intel\s+Core\s+i[3579][- ]\d{4,5}[A-Z]*)",
            r"(AMD\s+Ryzen\s+\d\s*\w*\s*\d{4,5}[A-Z]?)",
            r"(AMD\s+Ryzen\s+\d+)",
            r"(Intel\s+Core\s+\d+)",
            r"(Snapdragon\s+X\s+Series)",
            r"(Intel\s+[iI]\d[-\s]\d{4,5})",
            r"(Intel\s+[Cc]ore\s+H-series)",
            r"(Intel\s+[Cc]ore\s+[3579][- ]\d{4,5})",
            r"(Intel\s+N[uv]+\d+)",
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return None

    def _extract_ram(self, name: str, desc: str) -> int | None:
        return self._extract_ram_from_text(f"{name} {desc}")

    def _extract_ram_from_text(self, text: str) -> int | None:
        valid_rams = {2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 128}
        patterns = [
            r"(\d+)\s*GB\s*(?:LPDDR|DDR)\w*\s*(?:RAM)?",
            r"(\d+)\s*GB\s+(?:RAM|Memory|memory)",
            r"(\d+)\s*GB\s+of\s+(?:RAM|memory)",
            r"(\d+)\s*[gG][bB]\s*(?:RAM|ram|DDR|ddr)",
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                try:
                    val = int(m.group(1))
                    if val in valid_rams:
                        return val
                except ValueError:
                    pass

        m = re.search(r"(\d+)\s*[gG][bB]\s*(?:RAM|ram|DDR|ddr)", text)
        if m:
            try:
                val = int(m.group(1))
                if val in valid_rams:
                    return val
            except ValueError:
                pass
        return None

    def _extract_storage(self, name: str, desc: str) -> tuple[int | None, str | None]:
        return self._extract_storage_from_text(f"{name} {desc}")

    def _extract_storage_from_text(self, text: str) -> tuple[int | None, str | None]:
        m = re.search(r"(\d+)\s*(GB|TB)\s*(SSD|HDD|NVMe)", text, re.IGNORECASE)
        if m:
            size = int(m.group(1))
            unit = m.group(2).upper()
            stype = m.group(3).upper()
            if unit == "TB":
                size *= 1024
            return size, stype
        m = re.search(r"(\d+)\s*GB\s+(SSD)", text, re.IGNORECASE)
        if m:
            return int(m.group(1)), m.group(2).upper()
        m = re.search(r"(\d+)\s*[tT][bB]\s+(SSD|HDD)", text)
        if m:
            return int(m.group(1)) * 1024, m.group(2).upper()
        return None, None

    def _extract_gpu(self, name: str, desc: str) -> str | None:
        return self._extract_gpu_from_text(f"{name} {desc}")

    def _extract_gpu_from_text(self, text: str) -> str | None:
        patterns = [
            r"(NVIDIA\s+GeForce\s+RTX\s+\d+\s*\w*)",
            r"(NVIDIA\s+GeForce\s+RTX\s+\w+)",
            r"(NVIDIA\s+\w+\s+\w*\d*)",
            r"(Intel\s+(?:UHD|Iris|Arc)\s+\w*)",
            r"(AMD\s+Radeon\s+\w+\s*\w*)",
            r"(NVIDIA\s+RTX\s+\d+)",
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return None

    def _extract_display(self, name: str, desc: str) -> float | None:
        return self._extract_display_from_text(f"{name} {desc}")

    def _extract_display_from_text(self, text: str) -> float | None:
        m = re.search(r"(\d+\.?\d*)\s*(?:cms|cm)\s", text)
        if m:
            try:
                cm = float(m.group(1))
                if 25 <= cm <= 50:
                    return round(cm / 2.54, 1)
            except ValueError:
                pass
        m = re.search(
            r"(\d+\.?\d*)\s*[\"](?:\s*(?:HD|FHD|UHD|OLED|WUXGA|QHD))?", text
        )
        if m:
            try:
                val = float(m.group(1))
                if 10 <= val <= 20:
                    return val
            except ValueError:
                pass
        m = re.search(r"(\d+\.?\d*)\s*(?:inch|\"|in\b)", text, re.IGNORECASE)
        if m:
            try:
                val = float(m.group(1))
                if 10 <= val <= 20:
                    return val
            except ValueError:
                pass
        return None

    def _extract_original_price(self, text: str) -> float | None:
        patterns = [
            r"(?:was|was\s*:?|original|original\s*price|MRP)\s*:?\s*₹?\s*([\d,]+\.?\d*)",
            r"₹\s*([\d,]+\.?\d*)\s*(?:was|orig)",
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                try:
                    return float(m.group(1).replace(",", ""))
                except ValueError:
                    pass
        return None
