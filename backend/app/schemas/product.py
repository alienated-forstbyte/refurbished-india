import datetime
from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    store_id: int
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


class ProductResponse(ProductCreate):
    id: int
    deal_score: float | None = None
    store_name: str | None = None
    first_seen: datetime.datetime
    last_seen: datetime.datetime
    last_updated: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class ProductList(BaseModel):
    total: int
    page: int
    limit: int
    products: list[ProductResponse]
