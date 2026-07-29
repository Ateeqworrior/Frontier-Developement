"""Integration tests exercising the full HTTP request/response cycle (router →
service → repository → real per-test SQLite DB) for behavior not already
covered by test_discovery.py's Gherkin-scenario smoke tests."""


def test_authenticated_request_sees_sponsored_discount(client, auth_token):
    resp = client.get(
        "/api/catalog/products/1",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert resp.status_code == 200
    price = resp.json()["data"]["price_breakdown"]
    assert price["discounted_price"] == 8099.10  # product 1 is sponsored="yes"


def test_invalid_bearer_token_is_treated_as_anonymous(client):
    resp = client.get(
        "/api/catalog/products/1",
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["price_breakdown"]["discounted_price"] is None


def test_sort_by_popularity(client):
    resp = client.get("/api/catalog/products?sort=popularity")
    assert resp.status_code == 200
    assert resp.json()["data"][0]["title"] == "Foldable Lightweight Wheelchair"


def test_sort_by_price_desc(client):
    resp = client.get("/api/catalog/products?sort=price_desc")
    assert resp.status_code == 200
    assert resp.json()["data"][0]["title"] == "Foldable Lightweight Wheelchair"


def test_brand_filter_excludes_non_matching_products(client):
    resp = client.get("/api/catalog/products?brand_id=999")
    assert resp.status_code == 200
    assert resp.json()["data"] == []


def test_min_rating_filter(client):
    resp = client.get("/api/catalog/products?min_rating=4.9")
    assert resp.status_code == 200
    assert resp.json()["data"] == []  # seeded product's avg_rating (4.5) is below the bar


def test_pagination_page_size_is_honored(client):
    resp = client.get("/api/catalog/products?page=1&page_size=1")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["data"]) == 1
    assert body["pagination"]["page_size"] == 1


def test_search_price_range_validation(client):
    resp = client.get("/api/catalog/products/search?q=wheelchair&price_min=100&price_max=10")
    assert resp.status_code == 422
    assert resp.json()["message_code"] == "invalid_price_range"


def test_min_rating_out_of_bounds_is_rejected(client):
    resp = client.get("/api/catalog/products?min_rating=6")
    assert resp.status_code == 422
