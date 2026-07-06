# Writing a Scraper

Every scraper follows the same lifecycle.

```
Collect (discover URLs or direct API call)
    ↓
Extract (fetch each page / call API)
    ↓
Normalize (into ProductSchema)
    ↓
Return ProductSchema list (saving handled by task pipeline)
```

Never skip normalization.

---

# Base Interface

Every scraper extends `BaseScraper` and must set:

- `name` — unique scraper identifier

Two implementation patterns exist:

## Pattern 1: `scrape_all()` (preferred)

Override `scrape_all()` to return `list[ProductSchema]` directly. Used when the store has a single API endpoint or page that lists all products.

```python
class MyScraper(BaseScraper):
    name = "my_store"

    async def scrape_all(self) -> list[ProductSchema]:
        # Fetch products from API or page
        # Parse into ProductSchema objects
        return products
```

Examples: `CashifyScraper`, `LenovoScraper`, all Shopify scrapers.

## Pattern 2: discover → fetch → normalize (for multi-page stores)

Override `discover_products()`, `fetch_product()`, and `normalize()`:

```python
class MyScraper(BaseScraper):
    name = "my_store"

    async def discover_products(self) -> list[str]:
        # Return list of product URLs
        return urls

    async def fetch_product(self, url: str) -> str:
        # Download one product page
        return html

    async def normalize(self, raw_data: str, url: str) -> ProductSchema | None:
        # Parse HTML/JSON into ProductSchema
        return schema
```

The base class `scrape_all()` handles retries (3 attempts with exponential backoff) and rate limiting automatically.

---

# store_id

The `store_id` is passed to the constructor and set as `self.store_id`. All `ProductSchema` objects should include it so the save pipeline knows which store the product belongs to.

---

# ProductSchema

```python
@dataclass
class ProductSchema:
    store_id: int | None = None
    brand: str | None = None
    model: str | None = None
    product_name: str | None = None
    cpu: str | None = None
    cpu_generation: str | None = None
    ram_gb: int | None = None
    storage_gb: int | None = None
    storage_type: str | None = None
    gpu: str | None = None
    display_size: float | None = None
    display_resolution: str | None = None
    condition: str | None = None
    warranty_months: int | None = None
    price: float | None = None
    original_price: float | None = None
    discount: float | None = None
    currency: str = "INR"
    stock_status: str = "unknown"
    product_url: str | None = None
    image_url: str | None = None
    images: list[str] = field(default_factory=list)
```

All fields are optional — set what you can extract, leave the rest as `None`.

---

# Registration

After writing a scraper:

1. Import it in `app/scrapers/__init__.py` and add to `__all__`
2. Add a matching store entry in the database (`INSERT INTO stores`)
3. Register the scraper in `app/tasks.py` `SCRAPER_MAP`

```python
SCRAPER_MAP: dict[str, type] = {
    "Store Name Exactly": MyScraper,
}
```

The store `name` in the DB must match the key in `SCRAPER_MAP`.

---

# Error Handling

- Network errors: retry 3 times with exponential backoff (built into base class)
- Parsing errors: log and continue
- Missing fields: return as `None`
- Never crash the scraper
- Each scraper has its own `close()` method for cleanup

---

# Rate Limiting

Set `rate_limit` on the class (default 1.0 second). Call `await self.rate_limit_wait()` before each request.

Random delays and User-Agent rotation are handled by the base class.

---

# Logging

Use `self.name` prefix for all log messages:

```python
logger.info(f"[{self.name}] My log message")
```

---

# Images

Store only image URLs. Do not download image files. Set `image_url` for the primary image and `images` list for gallery images if available.

---

# Product Identity

Products are identified by the combination of `store_id` + `product_url`. The `_upsert_product` function in `tasks.py` uses this to determine whether to create a new product or update an existing one.

Never identify products by title alone — titles change.
