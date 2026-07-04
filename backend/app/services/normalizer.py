import logging
import re
from app.scrapers.base import ProductSchema

logger = logging.getLogger(__name__)


class ProductNormalizer:
    def normalize(self, raw: ProductSchema) -> ProductSchema:
        raw.brand = self._normalize_brand(raw.brand)
        raw.cpu_generation = self._extract_cpu_generation(raw.cpu)
        raw.discount = self._compute_discount(raw.price, raw.original_price)
        raw.storage_gb, raw.storage_type = self._normalize_storage(raw.storage_gb, raw.storage_type)
        return raw

    def _normalize_brand(self, brand: str | None) -> str | None:
        if not brand:
            return None
        mapping = {
            "lenovo": "Lenovo",
            "thinkpad": "Lenovo",
            "asus": "Asus",
            "dell": "Dell",
            "hp": "HP",
            "hewlett packard": "HP",
        }
        return mapping.get(brand.lower().strip(), brand)

    def _extract_cpu_generation(self, cpu: str | None) -> str | None:
        if not cpu:
            return None
        patterns = [
            r"(\d+th\s+Gen)",
            r"Gen\s*(\d+)",
            r"Core\s+i[3579][-\s](\d+)",
            r"Ryzen\s+\d+",
        ]
        for pattern in patterns:
            match = re.search(pattern, cpu, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def _compute_discount(self, price: float | None, original_price: float | None) -> float | None:
        if price and original_price and original_price > 0:
            return round((original_price - price) / original_price * 100, 1)
        return None

    def _normalize_storage(self, storage_gb: int | None, storage_type: str | None) -> tuple[int | None, str | None]:
        if storage_gb is not None and not storage_type:
            if storage_gb >= 128:
                storage_type = "SSD"
            else:
                storage_type = "HDD"
        return storage_gb, storage_type
