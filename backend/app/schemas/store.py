import datetime
from pydantic import BaseModel, ConfigDict


class StoreResponse(BaseModel):
    id: int
    name: str
    website: str
    country: str
    enabled: bool
    last_scrape: datetime.datetime | None = None
    scrape_interval: int

    model_config = ConfigDict(from_attributes=True)
