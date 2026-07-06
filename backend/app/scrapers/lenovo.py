import asyncio
import json
import logging
import re
from urllib.parse import urljoin

import httpx

from app.scrapers.base import BaseScraper, ProductSchema

logger = logging.getLogger(__name__)

OUTLET_BASE = "https://www.lenovo.com/in/outletin/en"
SEARCH_API = "https://openapi.lenovo.com/in/outletin/en/ofp/search/dlp/product/query/get/_tsc"
PAGE_FILTER_ID = "afdcd3f7-d8e6-4e9e-a76a-d6060dc75ae9"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IN,en;q=0.9",
    "Origin": "https://www.lenovo.com",
    "Referer": "https://www.lenovo.com/in/outletin/en/laptops/",
}


class LenovoScraper(BaseScraper):
    name = "lenovo"
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
            await self._client.get(OUTLET_BASE)
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def discover_products(self) -> list[str]:
        return []

    async def fetch_product(self, url: str) -> str:
        return ""

    async def normalize(self, raw_data: str, url: str) -> ProductSchema | None:
        return None

    def _build_search_params(self, page: int = 1, page_size: int = 30) -> dict:
        params_obj = {
            "classificationGroupIds": "400001",
            "pageFilterId": PAGE_FILTER_ID,
            "facets": [],
            "page": str(page),
            "pageSize": page_size,
            "groupCode": "",
            "init": True,
            "sorts": ["newest", "priceUp"],
            "version": "v2",
            "enablePreselect": True,
            "subseriesCode": "",
        }
        return {
            "pageFilterId": PAGE_FILTER_ID,
            "subSeriesCode": "",
            "loyalty": "false",
            "params": json.dumps(params_obj, separators=(",", ":")),
        }

    async def scrape_all(self) -> list[ProductSchema]:
        client = await self._get_client()

        all_products_data: list[dict] = []
        page = 1

        while True:
            await self.rate_limit_wait()
            params = self._build_search_params(page=page)
            try:
                resp = await client.get(SEARCH_API, params=params)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                logger.error(f"[{self.name}] Search API page {page} failed: {e}")
                break

            if not data.get("success"):
                logger.warning(f"[{self.name}] Search API page {page} returned unsuccessful")
                break

            products = data.get("data", {}).get("data", [])
            if not products:
                break

            page_products = products[0].get("products", [])
            if not page_products:
                break

            all_products_data.extend(page_products)
            total_pages = data["data"].get("pageCount", 1)
            logger.info(
                f"[{self.name}] Page {page}/{total_pages}: {len(page_products)} products"
            )

            if page >= total_pages:
                break
            page += 1

        logger.info(f"[{self.name}] Discovered {len(all_products_data)} products total")

        results: list[ProductSchema] = []
        for prod in all_products_data:
            await self.rate_limit_wait()
            try:
                schema = await self._process_product(prod, client)
                if schema:
                    results.append(schema)
            except Exception as e:
                logger.warning(
                    f"[{self.name}] Failed to process {prod.get('productCode')}: {e}"
                )

        logger.info(f"[{self.name}] Successfully scraped {len(results)} products")
        return results

    async def _process_product(
        self, prod: dict, client: httpx.AsyncClient
    ) -> ProductSchema | None:
        product_code = prod.get("productCode", "")
        product_name = prod.get("productName", "")

        if not product_code or not product_name:
            return None

        price = _parse_price(prod.get("finalPrice"))
        original_price = _parse_price(prod.get("webPrice"))
        discount = _parse_float(prod.get("savePercent"))

        marketing_status = prod.get("marketingStatus", "")
        inventory_status = prod.get("inventoryStatus", 0)
        stock_status = "in_stock" if (marketing_status == "Available" and inventory_status == 1) else "out_of_stock"

        image_url = None
        media = prod.get("media", {})
        thumbnail = media.get("thumbnail", {})
        if thumbnail:
            image_url = thumbnail.get("imageAddress")

        category_path = prod.get("categoryPath", [])
        product_url = self._build_product_url(product_code, category_path)

        specs = await self._fetch_specs(product_code, category_path, client)

        model = _extract_model(specs, product_name)
        brand = "Lenovo"
        cpu = specs.get("Processor")
        cpu_gen = _extract_cpu_generation(cpu)
        ram_gb = _extract_ram(specs)
        storage_gb, storage_type = _extract_storage(specs)
        gpu = specs.get("Graphic Card")
        display_size = _extract_display_size(specs)
        display_resolution = specs.get("Screen Resolution") or _extract_resolution_from_display(
            specs.get("Display")
        )
        condition = "Certified Refurbished"
        warranty_months = _extract_warranty_months(specs)

        return ProductSchema(
            store_id=self.store_id,
            brand=brand,
            model=model,
            product_name=product_name.strip(),
            cpu=cpu,
            cpu_generation=cpu_gen,
            ram_gb=ram_gb,
            storage_gb=storage_gb,
            storage_type=storage_type,
            gpu=gpu,
            display_size=display_size,
            display_resolution=display_resolution,
            condition=condition,
            warranty_months=warranty_months,
            price=price,
            original_price=original_price,
            discount=discount,
            currency="INR",
            stock_status=stock_status,
            product_url=product_url,
            image_url=image_url,
        )

    def _build_product_url(
        self, product_code: str, category_path: list[str]
    ) -> str:
        if len(category_path) >= 4:
            series = "/".join(category_path[2:4])
        else:
            series = "laptops"
        return f"{OUTLET_BASE}/p/laptops/{series}/{product_code}"

    async def _fetch_specs(
        self,
        product_code: str,
        category_path: list[str],
        client: httpx.AsyncClient,
    ) -> dict[str, str]:
        product_url = self._build_product_url(product_code, category_path)
        try:
            resp = await client.get(product_url)
            resp.raise_for_status()
            html = resp.text
        except Exception as e:
            logger.debug(
                f"[{self.name}] Failed to fetch product page {product_code}: {e}"
            )
            return {}

        idx = html.find('"classification":[')
        if idx < 0:
            idx = html.find('"classification"')
            if idx < 0:
                return {}

            colon_idx = html.find(":", idx)
            if colon_idx < 0:
                return {}
            idx = colon_idx

        arr_start = html.find("[", idx)
        if arr_start < 0:
            return {}

        depth = 0
        arr_end = -1
        for i in range(arr_start, len(html)):
            ch = html[i]
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    arr_end = i + 1
                    break

        if arr_end < 0:
            return {}

        json_str = html[arr_start:arr_end]

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            return {}

        specs: dict[str, str] = {}
        for group in data:
            for s in group.get("specs", []):
                a = s.get("a")
                b = s.get("b")
                if a and b:
                    specs[a] = b
        return specs


def _parse_price(val) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _parse_float(val) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _extract_model(specs: dict[str, str], product_name: str) -> str | None:
    brand_val = specs.get("Brand", "")
    if brand_val:
        return brand_val.capitalize()
    known_series = ["ThinkPad", "IdeaPad", "Legion", "Yoga", "ThinkBook"]
    for s in known_series:
        if s.lower() in product_name.lower():
            return s
    return None


def _extract_cpu_generation(cpu_str: str | None) -> str | None:
    if not cpu_str:
        return None
    m = re.search(r"(\d+)(?:th|nd|rd|st)\s+Gen", cpu_str, re.IGNORECASE)
    if m:
        return f"{m.group(1)}th Gen Intel"
    m = re.search(r"(Intel[^,]+)", cpu_str)
    if m:
        return m.group(1).strip()
    return None


def _extract_ram(specs: dict[str, str]) -> int | None:
    mem = specs.get("Memory", "")
    if not mem:
        return None
    m = re.search(r"(\d+)\s*GB", mem, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


def _extract_storage(specs: dict[str, str]) -> tuple[int | None, str | None]:
    storage = specs.get("Storage", "")
    if not storage:
        return None, None
    m = re.search(r"(\d+)\s*(GB|TB)\s*(SSD|HDD)", storage, re.IGNORECASE)
    if m:
        size = int(m.group(1))
        unit = m.group(2).upper()
        stype = m.group(3).upper()
        if unit == "TB":
            size *= 1024
        return size, stype
    m = re.search(r"(\d+)\s*GB", storage)
    if m:
        size = int(m.group(1))
        return size, "SSD" if size >= 128 else None
    return None, None


def _extract_display_size(specs: dict[str, str]) -> float | None:
    display = specs.get("Display", "")
    if not display:
        return None
    m = re.search(r'(\d+\.?\d*)\s*"', display)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return None


def _extract_resolution_from_display(display: str | None) -> str | None:
    if not display:
        return None
    m = re.search(r"(\d+\s*x\s*\d+)", display, re.IGNORECASE)
    if m:
        return m.group(1).replace(" ", "")
    return None


def _extract_warranty_months(specs: dict[str, str]) -> int | None:
    warranty = specs.get("Warranty", "")
    if not warranty:
        return None
    m = re.search(r"(\d+)\s*Year", warranty, re.IGNORECASE)
    if m:
        return int(m.group(1)) * 12
    m = re.search(r"(\d+)\s*Month", warranty, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None
