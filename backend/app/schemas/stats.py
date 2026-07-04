from pydantic import BaseModel


class StatsResponse(BaseModel):
    total_products: int
    in_stock_count: int
    out_of_stock_count: int
    store_count: int
    average_price: float | None = None
