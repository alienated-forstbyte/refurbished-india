import asyncio
import logging
import re

import httpx

from app.scrapers.base import BaseScraper, ProductSchema

logger = logging.getLogger(__name__)

SEARCH_URL = "https://outlet.us.dell.com/GDOOnline/api/Search/GetSearchResults"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://outlet.us.dell.com",
    "Referer": "https://outlet.us.dell.com/GDOOnline/Online/InventorySearch",
}

SEARCH_BODY = {
    "buid": "11",
    "localChannel": "28",
    "brandId": "2801",
    "pageIndex": 1,
    "pageSize": "100",
    "sortOrder": "2",
    "country": "us",
    "language": "en",
    "segment": "dfb",
}

BRAND_IDS = ["2801", "2828"]


class DellScraper(BaseScraper):
    name = "dell"
    rate_limit = 2.0

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

        tasks = [self._fetch_brand_products(client, bid) for bid in BRAND_IDS]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, list):
                products.extend(r)
            elif isinstance(r, Exception):
                logger.warning(f"[{self.name}] Brand fetch failed: {r}")

        logger.info(f"[{self.name}] Total: {len(products)} products")
        return products

    async def _fetch_brand_products(
        self, client: httpx.AsyncClient, brand_id: str
    ) -> list[ProductSchema]:
        products: list[ProductSchema] = []
        page = 1
        total_pages = 1

        while page <= total_pages:
            await self.rate_limit_wait()
            try:
                body = {**SEARCH_BODY, "brandId": brand_id, "pageIndex": page}
                resp = await client.post(SEARCH_URL, json=body)
                if resp.status_code != 200:
                    logger.warning(
                        f"[{self.name}] Bad response page {page} "
                        f"(brand {brand_id}): {resp.status_code}"
                    )
                    break
                data = resp.json()
            except Exception as e:
                logger.warning(
                    f"[{self.name}] Failed page {page} (brand {brand_id}): {e}"
                )
                break

            items = data.get("searchData", []) or data.get("data", [])
            if not items:
                break

            total_pages = data.get("totalPages", page)
            if total_pages > 50:
                total_pages = 50

            for item in items:
                try:
                    product = self._parse_item(item)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.debug(f"[{self.name}] Parse error: {e}")

            logger.info(
                f"[{self.name}] Brand {brand_id} page {page}/{total_pages}: "
                f"{len(items)} items"
            )
            page += 1

        return products

    def _parse_item(self, item: dict) -> ProductSchema | None:
        if not isinstance(item, dict):
            return None

        family_name = item.get("familyName", "")
        if not family_name:
            return None

        cat = str(item.get("categoryDescription", "") or "")
        if cat and "laptop" not in cat.lower() and "notebook" not in cat.lower():
            if family_name and "laptop" not in family_name.lower() and "notebook" not in family_name.lower() and "2-in-1" not in family_name.lower():
                if "chromebook" not in family_name.lower():
                    return None

        product_name = item.get("modInfoDesc", [{}])[-1].get("modInfoDesc", "") if isinstance(item.get("modInfoDesc"), list) and item.get("modInfoDesc") else ""
        if not product_name:
            product_name = family_name

        price = None
        if item.get("unitPrice") and float(item["unitPrice"]) > 0:
            price = float(item["unitPrice"])
        elif item.get("minPrice"):
            price = float(item["minPrice"])

        if price and price > 50000:
            price = None

        image_url = item.get("familyImageURL", "") or None

        cpu = self._extract_from_mods(item.get("modInfoDesc", []), "processor")
        if not cpu:
            cpu = self._extract_cpu_text(item)

        ram_gb = self._extract_ram(item)
        storage_gb, storage_type = self._extract_storage(item)
        gpu = self._extract_gpu(item)
        display_size = self._extract_display(item)

        condition = "Certified Refurbished"
        cond = item.get("condition", "")
        if cond:
            cond_str = str(cond).strip()
            if cond_str:
                condition = cond_str

        stock_status = "out_of_stock"
        qty = item.get("quantityInStock", 0)
        if qty and int(qty) > 0:
            stock_status = "in_stock"

        variant = item.get("productVariantName", "") or ""
        if variant:
            product_url = f"https://www.dell.com/en-us/shop/{variant}"
        else:
            item_id = str(item.get("id", "") or "")
            if item_id:
                product_url = f"https://www.dell.com/en-us/shop/p/{item_id}"
            else:
                slug = re.sub(r"[^a-z0-9]+", "-", product_name.lower())
                slug = re.sub(r"-+-", "-", slug).strip("-")
                product_url = f"https://www.dell.com/en-us/shop/{slug}"

        brand = "Dell"
        brand_name = item.get("brandName", "")
        if isinstance(brand_name, list) and brand_name:
            brand = "Dell"
        elif isinstance(brand_name, str):
            brand = "Dell"

        model = self._extract_model(family_name)

        return ProductSchema(
            store_id=self.store_id,
            brand=brand,
            model=model,
            product_name=product_name or family_name,
            cpu=cpu,
            ram_gb=ram_gb,
            storage_gb=storage_gb,
            storage_type=storage_type,
            gpu=gpu,
            display_size=display_size,
            condition=condition,
            warranty_months=12,
            price=price,
            currency="USD",
            stock_status=stock_status,
            product_url=product_url,
            image_url=image_url,
        )

    def _extract_from_mods(
        self, mods: list, commodity_keyword: str
    ) -> str | None:
        if not mods:
            return None
        for mod in mods:
            desc = mod.get("commodityDesc", "") or ""
            if commodity_keyword.lower() in desc.lower():
                return mod.get("modInfoDesc", "").strip() or None
        return None

    def _extract_cpu_text(self, item: dict) -> str | None:
        text = str(item.get("processor", ""))
        if text and text not in ("None", "", "[]", "{}"):
            return text
        for mod in item.get("modInfoDesc", []):
            desc = mod.get("modInfoDesc", "")
            if any(
                kw in desc
                for kw in ["Intel", "Core", "AMD", "Ryzen", "Snapdragon"]
            ):
                return desc.strip()
        return None

    def _extract_ram(self, item: dict) -> int | None:
        valid_rams = {2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 128}
        ram_text = self._extract_from_mods(item.get("modInfoDesc", []), "memory")
        if ram_text:
            m = re.search(r"(\d+)\s*GB", ram_text, re.IGNORECASE)
            if m:
                val = int(m.group(1))
                if val in valid_rams:
                    return val
        mem = item.get("memory", "")
        if mem:
            mem_str = str(mem)
            m = re.search(r"(\d+)\s*GB", mem_str, re.IGNORECASE)
            if m:
                val = int(m.group(1))
                if val in valid_rams:
                    return val
        return None

    def _extract_storage(self, item: dict) -> tuple[int | None, str | None]:
        storage_text = self._extract_from_mods(
            item.get("modInfoDesc", []), "hard disk"
        )
        if not storage_text:
            storage_text = self._extract_from_mods(
                item.get("modInfoDesc", []), "solid state"
            )
        if storage_text:
            m = re.search(
                r"(\d+)\s*(GB|TB)\s*(SSD|HDD|NVMe|SATA)?",
                storage_text,
                re.IGNORECASE,
            )
            if m:
                size = int(m.group(1))
                unit = m.group(2).upper()
                stype = (m.group(3) or "SSD").upper()
                if unit == "TB":
                    size *= 1024
                return size, stype
            m = re.search(r"(\d+)\s*[gG][bB]", storage_text)
            if m:
                return int(m.group(1)), "SSD"
        st = item.get("storageType", "")
        if st:
            st_str = str(st)
            m = re.search(r"(\d+)", st_str)
            if m:
                return int(m.group(1)), "SSD"
        return None, None

    def _extract_gpu(self, item: dict) -> str | None:
        gpu = self._extract_from_mods(item.get("modInfoDesc", []), "graphics")
        if gpu:
            return gpu
        gpu_field = item.get("graphics", "")
        if gpu_field:
            return str(gpu_field).strip()
        for mod in item.get("modInfoDesc", []):
            desc = mod.get("modInfoDesc", "")
            if any(kw in desc for kw in ["GeForce", "Radeon", "Intel Graphics", "Arc", "RTX"]):
                return desc.strip()
        return None

    def _extract_display(self, item: dict) -> float | None:
        screen = item.get("screenSize", "")
        if screen:
            screen_str = str(screen)
            m = re.search(r"(\d+\.?\d*)", screen_str)
            if m:
                val = float(m.group(1))
                if 10 <= val <= 20:
                    return val
        for mod in item.get("modInfoDesc", []):
            desc = mod.get("modInfoDesc", "")
            m = re.search(r"(\d+\.?\d*)\s*(?:inch|\"|in\b)", desc, re.IGNORECASE)
            if m:
                val = float(m.group(1))
                if 10 <= val <= 20:
                    return val
            m = re.search(r"(\d+\.?\d*)\s*(?:cm)", desc, re.IGNORECASE)
            if m:
                val = float(m.group(1))
                if 25 <= val <= 50:
                    return round(val / 2.54, 1)
        return None

    def _extract_model(self, name: str) -> str | None:
        patterns = [
            r"(Latitude\s+\w+\s*\d*)",
            r"(XPS\s+\w+\s*\d*)",
            r"(Inspiron\s+\w+\s*\d*)",
            r"(Precision\s+\w+\s*\d*)",
            r"(Alienware\s+\w+\s*\d*)",
            r"(Vostro\s+\w+\s*\d*)",
            r"(Dell\s+\w+)",
        ]
        for p in patterns:
            m = re.search(p, name, re.IGNORECASE)
            if m:
                return m.group(1)
        return None
