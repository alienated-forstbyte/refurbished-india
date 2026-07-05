import json
import logging
import re
from urllib.parse import urljoin

import httpx

from app.scrapers.base import BaseScraper, ProductSchema

logger = logging.getLogger(__name__)


class ShopifyBaseScraper(BaseScraper):
    shop_domain: str = ""

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
        base_url = f"https://{self.shop_domain}"
        products: list[ProductSchema] = []
        page = 1

        client = await self._get_client()

        while True:
            await self.rate_limit_wait()
            url = f"{base_url}/products.json?limit=250&page={page}"
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                logger.error(f"[{self.name}] Failed to fetch page {page}: {e}")
                break

            items = data.get("products", [])
            if not items:
                break

            logger.info(f"[{self.name}] Page {page}: {len(items)} products")

            for item in items:
                try:
                    product = self._normalize_product(item, base_url)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.warning(f"[{self.name}] Failed to normalize product {item.get('id')}: {e}")

            if len(items) < 250:
                break
            page += 1

        logger.info(f"[{self.name}] Scraped {len(products)} products total")
        return products

    def _normalize_product(self, item: dict, base_url: str) -> ProductSchema | None:
        title = item.get("title", "")
        handle = item.get("handle", "")
        vendor = item.get("vendor", "")
        tags = item.get("tags", [])
        body_html = item.get("body_html", "")
        product_type = item.get("product_type", "")

        variants = item.get("variants", [])
        images = item.get("images", [])

        if not variants:
            return None

        first_variant = variants[0]
        price_str = first_variant.get("price", "0")
        compare_at = first_variant.get("compare_at_price")
        available = first_variant.get("available", False)

        try:
            price = float(price_str) if price_str else None
        except (ValueError, TypeError):
            price = None

        try:
            original_price = float(compare_at) if compare_at else None
        except (ValueError, TypeError):
            original_price = None

        brand = self._extract_brand(vendor, title, tags)
        model = self._extract_model(handle, title)
        cpu = self._extract_cpu(title, body_html, tags)
        ram_gb = self._extract_ram(title, tags, body_html)
        storage_gb, storage_type = self._extract_storage(title, tags, body_html, variants)
        gpu = self._extract_gpu(title, body_html)
        display_size = self._extract_display_size(title, body_html)
        warranty_months = self._extract_warranty(body_html, title, tags)
        condition = self._extract_condition(title, tags, body_html)
        product_url = urljoin(base_url, f"/products/{handle}")
        image_url = images[0]["src"] if images else None
        all_images = [img["src"] for img in images] if images else []

        stock_status = "in_stock" if available else "out_of_stock"

        return ProductSchema(
            store_id=self.store_id,
            brand=brand,
            model=model,
            product_name=title.strip(),
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
            images=all_images,
        )

    def _extract_brand(self, vendor: str, title: str, tags: list[str]) -> str | None:
        known_brands = [
            "lenovo", "thinkpad", "dell", "hp", "hewlett packard", "apple",
            "asus", "acer", "msi", "microsoft", "ibm", "fujitsu", "toshiba",
            "sony", "samsung", "huawei", "xiaomi", "compaq",
        ]
        search_text = f"{title} {' '.join(tags)}".lower()
        for brand in known_brands:
            if brand in search_text:
                return brand.capitalize()
        vendor_lower = vendor.lower()
        for brand in known_brands:
            if brand in vendor_lower:
                return brand.capitalize()
        return None

    def _extract_model(self, handle: str, title: str) -> str | None:
        patterns = [
            r'\b(ThinkPad\s*\w+\d*\w*)',
            r'\b(Latitude\s*\w+\d*)',
            r'\b(EliteBook\s*\w+\d*)',
            r'\b(ProBook\s*\w+\d*)',
            r'\b(Pavilion\s*\w+\d*)',
            r'\b(Spectre\s*\w+\d*)',
            r'\b(Inspiron\s*\w+\d*)',
            r'\b(XPS\s*\w+\d*)',
            r'\b(Vostro\s*\w+\d*)',
            r'\b(Precision\s*\w+\d*)',
            r'\b(OptiPlex\s*\w+\d*)',
            r'\b(MacBook\s*\w+\d*\w*)',
            r'\b(VivoBook\s*\w+\d*)',
            r'\b(ZenBook\s*\w+\d*)',
            r'\b(ROG\s*\w+\d*)',
            r'\b(TUF\s*\w+\d*)',
            r'\b(Swift\s*\w+\d*)',
            r'\b(Nitro\s*\w+\d*)',
            r'\b(Predator\s*\w+\d*)',
            r'\b(ThinkCentre\s*\w+\d*)',
            r'\b(IdeaPad\s*\w+\d*)',
            r'\b(Legion\s*\w+\d*)',
            r'\b( Yoga\s*\w+\d*)',
            r'\b(ThinkStation\s*\w+\d*)',
            r'\b(Surface\s*\w+\d*)',
        ]
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _extract_cpu(self, title: str, body_html: str, tags: list[str]) -> str | None:
        text = f"{title} {body_html} {' '.join(tags)}"
        patterns = [
            r'(Intel\s+Core\s+i[3579][-\s]\d{4,5}[A-Z]?[A-Z]?)',
            r'(Intel\s+Core\s+i[3579][-\s]\d{4,5})',
            r'(Intel\s+Celeron\s+\w+)',
            r'(Intel\s+Pentium\s+\w+)',
            r'(AMD\s+Ryzen\s+\d\s*\w*\s*\d{4,5}[A-Z]?)',
            r'(AMD\s+Ryzen\s+\d)',
            r'(Apple\s+M\d+\s*(Pro|Max|Ultra)?)',
            r'(Intel\s+Core\s+[3579][-\s]\d{4,5})',
            r'(Intel\s+Xeon\s+\w+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_ram(self, title: str, tags: list[str], body_html: str) -> int | None:
        text = f"{title} {' '.join(tags)} {body_html}"
        valid_rams = {2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 128}

        patterns = [
            r'(\d+)\s*GB\s*(?:DDR[34]?\s*)?RAM',
            r'(\d+)\s*GB\s*Memory',
            r'RAM\s*[:\-]\s*(\d+)\s*GB',
            r'(\d+)\s*GB\s*DDR',
            r'[ /]\d+\s*GB[ /]',
            r'(\d+)[gG][bB]\s*(?:RAM|ram|DDR|Memory)',
            r'(\d+)\s*GB\s*(?:of\s*)?RAM',
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                try:
                    val = int(match.group(1))
                    if val in valid_rams:
                        return val
                except (ValueError, IndexError):
                    pass

        match = re.search(r'[^a-zA-Z](\d+)\s*[gG][bB](?!\s*[Ii][nN])', text)
        if match:
            try:
                val = int(match.group(1))
                if val in valid_rams:
                    return val
            except ValueError:
                pass

        return None

    def _extract_storage(self, title: str, tags: list[str], body_html: str, variants: list[dict]) -> tuple[int | None, str | None]:
        text = f"{title} {' '.join(tags)} {body_html}"

        for v in variants:
            opt_title = v.get("title", "")
            m = re.search(r'(\d+)\s*(GB|TB)\s*(SSD|HDD)', opt_title, re.IGNORECASE)
            if m:
                size = int(m.group(1))
                unit = m.group(2).upper()
                stype = m.group(3).upper()
                if unit == "TB":
                    size *= 1024
                return size, stype

        valid_storage_sizes = {64, 120, 128, 180, 240, 250, 256, 320, 500, 512, 750, 1000, 1024, 2000, 2048}

        patterns = [
            r'[ /](\d+)\s*(GB|TB)\s*(SSD|HDD)',
            r'(\d+)\s*GB\s+(SSD|HDD)',
            r'(?:SSD|HDD)\s*[:\-]?\s*(\d+)\s*(GB|TB)',
            r'(\d+)[gG][bB]\s*(SSD|HDD)',
            r'(\d+)[tT][bB]\s*(SSD|HDD)',
            r'[ /](\d+)\s*(TB)(?!\s*[Ii][nN])',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    size = int(groups[0])
                    unit = groups[1].upper()
                    stype = groups[2].upper()
                    if unit == "TB":
                        size *= 1024
                    return size, stype
                elif len(groups) == 2:
                    size = int(groups[0])
                    unit = groups[1].upper()
                    if unit == "TB":
                        size *= 1024
                    if unit == "GB" and size in valid_storage_sizes:
                        return size, "SSD" if size >= 128 else "HDD"
                    if unit == "TB":
                        return size, "SSD"

        match = re.search(r'[^a-zA-Z](\d+)\s*(GB)(?!\s*[Ii][nN])', text)
        if match:
            size = int(match.group(1))
            if size in valid_storage_sizes:
                return size, "SSD" if size >= 128 else "HDD"

        return None, None

    def _extract_gpu(self, title: str, body_html: str) -> str | None:
        text = f"{title} {body_html}"
        patterns = [
            r'(NVIDIA\s+\w+\s+\w*\d*\w*)',
            r'(Intel\s+UHD\s+Graphics\s*\w*)',
            r'(Intel\s+Iris\s+Xe\s+Graphics)',
            r'(AMD\s+Radeon\s+\w+\s*\w*)',
            r'(Apple\s+M\d+\s*(Pro|Max|Ultra)?\s*GPU)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_display_size(self, title: str, body_html: str) -> float | None:
        text = f"{title} {body_html}"
        match = re.search(r'(\d+\.?\d*)\s*[""]\s*(?:HD|FHD|UHD|IPS|LED|LCD|Touch|Display|Screen)', text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        match = re.search(r'(\d+\.?\d*)-inch', text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return None

    def _extract_warranty(self, body_html: str, title: str, tags: list[str]) -> int | None:
        text = f"{body_html} {title} {' '.join(tags)}"
        patterns = [
            r'(\d+)\s*(?:Month|month)\s*(?:Warranty|warranty)',
            r'(?:Warranty|warranty)\s*[:\-]?\s*(\d+)\s*(?:Month|month)',
            r'(\d+)\s*[-\s]Year\s*(?:Warranty|warranty)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                val = int(match.group(1))
                if "Year" in match.group(0):
                    return val * 12
                return val
        return None

    def _extract_condition(self, title: str, tags: list[str], body_html: str) -> str | None:
        text = f"{title} {' '.join(tags)} {body_html}".lower()
        if "grade a" in text or "grade-a" in text or "grade_a" in text:
            return "Grade A"
        if "grade b" in text or "grade-b" in text or "grade_b" in text:
            return "Grade B"
        if "grade c" in text or "grade-c" in text or "grade_c" in text:
            return "Grade C"
        if "refurbished" in text:
            return "Refurbished"
        if "used" in text:
            return "Used"
        if "open box" in text or "open-box" in text or "openbox" in text:
            return "Open Box"
        return None