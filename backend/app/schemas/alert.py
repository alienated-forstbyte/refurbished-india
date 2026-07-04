import datetime
from pydantic import BaseModel, ConfigDict


class AlertCreate(BaseModel):
    brand: str | None = None
    cpu: str | None = None
    max_price: float | None = None
    ram: int | None = None
    storage: int | None = None
    gpu: str | None = None
    notify_stock: bool = True
    notify_price: bool = True


class AlertResponse(AlertCreate):
    id: int
    user_id: int
    enabled: bool
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
