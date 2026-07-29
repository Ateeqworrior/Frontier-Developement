"""Smoke tests mirroring US-003's Gherkin acceptance criteria
(docs/user-stories/stories/domain-product-discovery/US-003-product-discovery-search.md).
Full unit/integration coverage is added in Step 6."""


def test_browse_by_category(client):
    resp = client.get("/api/catalog/products?category_id=1")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]) == 1  # only the Published product, not the Draft one
    assert body["data"][0]["title"] == "Foldable Lightweight Wheelchair"
    assert body["pagination"]["total"] == 1


def test_keyword_search(client):
    resp = client.get("/api/catalog/products/search?q=wheelchair")
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"][0]["title"] == "Foldable Lightweight Wheelchair"


def test_search_query_too_short_is_rejected(client):
    resp = client.get("/api/catalog/products/search?q=w")
    assert resp.status_code == 422
    assert resp.json()["message_code"] == "invalid_search_query"


def test_filter_and_sort_by_price(client):
    resp = client.get("/api/catalog/products?sort=price_asc&price_min=1&price_max=100000")
    assert resp.status_code == 200
    assert resp.json()["data"][0]["base_price"] == 8999.00


def test_invalid_price_range_is_rejected(client):
    resp = client.get("/api/catalog/products?price_min=100&price_max=10")
    assert resp.status_code == 422
    assert resp.json()["message_code"] == "invalid_price_range"


def test_product_detail_view(client):
    resp = client.get("/api/catalog/products/1?pin_code=560001")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["stock_quantity"] == 15
    assert data["price_breakdown"]["basic_price"] == 8999.00
    assert data["price_breakdown"]["discounted_price"] is None  # not authenticated -> no sponsored discount
    assert data["delivery_feasibility"] == "unknown"  # no Logistics service running locally (US-013 not built)


def test_unpublished_product_is_not_discoverable(client):
    resp = client.get("/api/catalog/products/2")
    assert resp.status_code == 404
    assert resp.json()["message_code"] == "product_not_found"
