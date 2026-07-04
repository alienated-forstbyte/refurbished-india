import pytest
from app.services.change_detector import ChangeDetector, ChangeType
from app.scrapers.base import ProductSchema


@pytest.fixture
def detector():
    return ChangeDetector()


def make_product(url: str, price: float = 1000.0, stock: str = "in_stock") -> ProductSchema:
    return ProductSchema(
        store_id=1,
        product_name="Test Product",
        product_url=url,
        price=price,
        stock_status=stock,
    )


@pytest.mark.asyncio
async def test_detect_new_product(detector):
    scraped = [make_product("/product/1")]
    existing = {}
    events = await detector.detect(scraped, existing)
    assert len(events) == 1
    assert events[0].type == ChangeType.NEW_PRODUCT


@pytest.mark.asyncio
async def test_detect_price_change(detector):
    scraped = [make_product("/product/1", price=800.0)]
    existing = {"/product/1": make_product("/product/1", price=1000.0)}
    events = await detector.detect(scraped, existing)
    assert len(events) == 1
    assert events[0].type == ChangeType.PRICE_CHANGED
    assert events[0].old_price == 1000.0
    assert events[0].new_price == 800.0


@pytest.mark.asyncio
async def test_detect_stock_change(detector):
    scraped = [make_product("/product/1", stock="out_of_stock")]
    existing = {"/product/1": make_product("/product/1", stock="in_stock")}
    events = await detector.detect(scraped, existing)
    assert len(events) == 1
    assert events[0].type == ChangeType.OUT_OF_STOCK


@pytest.mark.asyncio
async def test_detect_removed(detector):
    scraped = []
    existing = {"/product/1": make_product("/product/1")}
    events = await detector.detect(scraped, existing)
    assert len(events) == 1
    assert events[0].type == ChangeType.REMOVED
