"""Unit tests for ProductDiscoveryService business logic (price breakdown,
validation), isolated from the repository/DB layer via lightweight fakes."""

import asyncio

import pytest

from ecom_core.utils.errors import InvalidPriceRangeError, ProductNotFoundError
from app.services import ProductDiscoveryService


class _FakeVariant:
    def __init__(self, price=100.0, quantity=5, images="[]"):
        self.price = price
        self.quantity = quantity
        self.images = images


class _FakeProduct:
    def __init__(self, sponsored="no", variants=None, avg_rating=None):
        self.id = 1
        self.title = "Test Product"
        self.description = "desc"
        self.brand_id = 1
        self.category_id = 1
        self.sponsored = sponsored
        self.avg_rating = avg_rating
        self.rating_count = 0
        self.variants = variants or []


class _FakeRepo:
    def __init__(self, product=None):
        self._product = product

    def get_by_id(self, product_id):
        return self._product


def _service_with_product(product):
    service = ProductDiscoveryService.__new__(ProductDiscoveryService)
    service.repo = _FakeRepo(product)
    return service


def test_validate_price_range_allows_equal_bounds():
    ProductDiscoveryService._validate_price_range(100, 100)  # no raise


def test_validate_price_range_rejects_inverted_bounds():
    with pytest.raises(InvalidPriceRangeError):
        ProductDiscoveryService._validate_price_range(100, 10)


def test_to_summary_with_no_variants_has_no_image():
    summary = ProductDiscoveryService._to_summary(_FakeProduct(variants=[]), min_price=0.0)
    assert summary.image_url is None
    assert summary.avg_rating is None


def test_get_product_detail_raises_when_product_missing():
    service = _service_with_product(None)
    with pytest.raises(ProductNotFoundError):
        asyncio.run(service.get_product_detail(999, None, is_authenticated=False))


def test_get_product_detail_applies_sponsored_discount_only_when_authenticated():
    product = _FakeProduct(sponsored="yes", variants=[_FakeVariant(price=1000.0)])
    service = _service_with_product(product)

    anonymous = asyncio.run(service.get_product_detail(1, None, is_authenticated=False))
    assert anonymous.price_breakdown.discounted_price is None

    authenticated = asyncio.run(service.get_product_detail(1, None, is_authenticated=True))
    assert authenticated.price_breakdown.discounted_price == 900.0  # 10% off per config default


def test_get_product_detail_not_sponsored_never_discounts():
    product = _FakeProduct(sponsored="no", variants=[_FakeVariant(price=1000.0)])
    service = _service_with_product(product)
    detail = asyncio.run(service.get_product_detail(1, None, is_authenticated=True))
    assert detail.price_breakdown.discounted_price is None


def test_get_product_detail_handles_product_with_no_variant():
    product = _FakeProduct(sponsored="no", variants=[])
    service = _service_with_product(product)
    detail = asyncio.run(service.get_product_detail(1, None, is_authenticated=False))
    assert detail.stock_quantity == 0
    assert detail.price_breakdown.basic_price == 0.0
