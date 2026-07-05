import json
import logging
import re

import httpx

from app.scrapers.base import BaseScraper, ProductSchema

logger = logging.getLogger(__name__)

RSC_PUSH_RE = re.compile(r'self\.__next_f\.push\(\[1,"((?:\\.|[^"\\])*)"\]\)')

BRAND_SLUGS = [
    "apple",
    "dell",
    "lenovo",
    "hp-compaq",
    "acer",
    "asus",
]

BASE_URL = "https://www.cashify.in"


def _unescape_rsc(s: str) -> str:
    return s.encode("utf-8").decode("unicode_escape")


def _extract_product_lists(html: str) -> list[dict]:
    products: list[dict] = []
    seen_ids: set[str] = set()

    for match in RSC_PUSH_RE.finditer(html):
        try:
            decoded = _unescape_rsc(match.group(1))
        except Exception:
            continue

        idx = decoded.find('"productList"')
        if idx == -1:
            continue

        arr_start = decoded.find("[", idx)
        if arr_start == -1:
            continue

        depth = 0
        arr_end = -1
        for pos in range(arr_start, len(decoded)):
            ch = decoded[pos]
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    arr_end = pos + 1
                    break

        if arr_end == -1:
            continue

        array_str = decoded[arr_start:arr_end]

        try:
            items = json.loads(array_str)
        except json.JSONDecodeError:
            continue

        if not isinstance(items, list):
            continue

        for item in items:
            pid = item.get("productId") or item.get("slug")
            if pid and pid not in seen_ids:
                seen_ids.add(pid)
                products.append(item)

    return products


def _extract_brand_from_name(name: str) -> str | None:
    name_lower = name.lower()
    brands = ["apple", "dell", "lenovo", "hp", "asus", "acer", "msi", "microsoft",
              "samsung", "huawei", "xiaomi", "compaq", "ibm", "fujitsu", "toshiba"]
    for b in brands:
        if b in name_lower:
            return b.capitalize()
    return None


def _extract_cpu_from_name(name: str) -> str | None:
    patterns = [
        r'(Intel\s+Core\s+i[3579][-\s]\d{4,5}[A-Z]?[A-Z]?)',
        r'(Intel\s+Core\s+i[3579][-\s]\d{4,5})',
        r'(Apple\s+M\d+\s*(?:Pro|Max|Ultra)?)',
        r'(AMD\s+Ryzen\s+\d\s*\w*\s*\d{4,5}[A-Z]?)',
        r'(Intel\s+Celeron\s+\w+)',
        r'(Intel\s+Pentium\s+\w+)',
    ]
    for p in patterns:
        m = re.search(p, name, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def _extract_ram_from_name(name: str) -> int | None:
    m = re.search(r'(\d+)\s*GB\s*(?:DDR[34]?\s*)?RAM', name, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.search(r'(\d+)\s*GB', name)
    if m:
        val = int(m.group(1))
        if val in (2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 128):
            return val
    return None


def _extract_storage_from_name(name: str) -> tuple[int | None, str | None]:
    m = re.search(r'(\d+)\s*(GB|TB)\s*(SSD|HDD)', name, re.IGNORECASE)
    if m:
        size = int(m.group(1))
        unit = m.group(2).upper()
        stype = m.group(3).upper()
        if unit == "TB":
            size *= 1024
        return size, stype
    m = re.search(r'(\d+)\s*GB', name)
    if m:
        size = int(m.group(1))
        if size >= 64:
            return size, "SSD" if size >= 128 else "HDD"
    return None, None


def _extract_display_from_name(name: str) -> float | None:
    m = re.search(r'(\d+\.?\d*)\s*[""]?\s*(?:Inch|inch|")', name)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return None


def _item_to_product(item: dict, store_id: int | None = None) -> ProductSchema:
    product_name = item.get("productName", "")
    slug = item.get("slug", "")
    mrp = item.get("mrp")
    sale_price = item.get("salePrice")
    image_url = item.get("image")
    inventory = item.get("inventory", 0)

    price = None
    if sale_price:
        try:
            price = float(sale_price)
        except (ValueError, TypeError):
            pass

    original_price = None
    if mrp:
        try:
            original_price = float(mrp)
        except (ValueError, TypeError):
            pass

    stock_status = "in_stock" if inventory and int(inventory) > 0 else "out_of_stock"

    brand = _extract_brand_from_name(product_name)
    cpu = _extract_cpu_from_name(product_name)
    ram_gb = _extract_ram_from_name(product_name)
    storage_gb, storage_type = _extract_storage_from_name(product_name)
    display_size = _extract_display_from_name(product_name)
    product_url = f"{BASE_URL}{slug}" if slug else None

    return ProductSchema(
        store_id=store_id,
        brand=brand,
        model=None,
        product_name=product_name,
        cpu=cpu,
        ram_gb=ram_gb,
        storage_gb=storage_gb,
        storage_type=storage_type,
        gpu=None,
        display_size=display_size,
        condition="Refurbished",
        price=price,
        original_price=original_price,
        currency="INR",
        stock_status=stock_status,
        product_url=product_url,
        image_url=image_url,
    )


class CashifyScraper(BaseScraper):
    name = "cashify"

    def __init__(self, store_id: int | None = None):
        super().__init__(store_id)
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers=self.get_headers(),
                timeout=30.0,
                follow_redirects=True,
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def discover_products(self) -> list[str]:
        return []

    async def fetch_product(self, url: str) -> str:
        return ""

    async def scrape_all(self) -> list[ProductSchema]:
        pages_to_fetch = [
            "/buy-refurbished-laptops/all-laptops",
        ]

        for brand in BRAND_SLUGS:
            pages_to_fetch.append(f"/buy-refurbished-laptops/{brand}")

        all_products: dict[str, ProductSchema] = {}
        client = await self._get_client()

        for path in pages_to_fetch:
            await self.rate_limit_wait()
            url = f"{BASE_URL}{path}"
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                html = resp.text
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to fetch {url}: {e}")
                continue

            items = _extract_product_lists(html)
            logger.info(f"[{self.name}] {path}: extracted {len(items)} products")

            for item in items:
                product = _item_to_product(item, self.store_id)
                dedup_key = product.product_url or product.product_name or item.get("productId", "")
                if dedup_key not in all_products:
                    all_products[dedup_key] = product

        logger.info(f"[{self.name}] Total unique products: {len(all_products)}")
        return list(all_products.values())