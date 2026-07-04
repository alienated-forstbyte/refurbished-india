import pytest
from app.services.normalizer import ProductNormalizer
from app.scrapers.base import ProductSchema


@pytest.fixture
def normalizer():
    return ProductNormalizer()


def test_normalize_brand(normalizer):
    assert normalizer._normalize_brand("lenovo") == "Lenovo"
    assert normalizer._normalize_brand("thinkpad") == "Lenovo"
    assert normalizer._normalize_brand("asus") == "Asus"
    assert normalizer._normalize_brand("dell") == "Dell"
    assert normalizer._normalize_brand("hp") == "HP"
    assert normalizer._normalize_brand(None) is None


def test_compute_discount(normalizer):
    assert normalizer._compute_discount(40000, 50000) == 20.0
    assert normalizer._compute_discount(50000, 50000) == 0.0
    assert normalizer._compute_discount(None, 50000) is None
    assert normalizer._compute_discount(40000, None) is None


def test_extract_cpu_generation(normalizer):
    assert normalizer._extract_cpu_generation("Intel Core i5-1240P") is not None
    assert normalizer._extract_cpu_generation("Intel Core i7 12th Gen") is not None
    assert normalizer._extract_cpu_generation(None) is None


def test_full_normalize(normalizer):
    raw = ProductSchema(
        store_id=1,
        brand="lenovo",
        product_name="ThinkPad T14",
        price=45000.0,
        original_price=60000.0,
        cpu="Intel Core i5-1240P",
    )
    result = normalizer.normalize(raw)
    assert result.brand == "Lenovo"
    assert result.discount == 25.0
    assert result.cpu_generation is not None
