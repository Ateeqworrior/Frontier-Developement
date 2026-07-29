"""Integration tests for the wishlist CRUD (HLD/LLD §4.3.5) and the batch-price
endpoint (new upstream dependency for US-004's Cart Service), added on top of the
existing per-test SQLite DB seeded with products 1 (Published) and 2 (Draft)."""


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_get_product_prices_returns_only_published(client, auth_token):
    resp = client.get("/api/catalog/products/prices?ids=1,2,999")
    assert resp.status_code == 200
    data = resp.json()["data"]
    ids = [item["id"] for item in data]
    assert ids == [1]  # product 2 is Draft, 999 doesn't exist
    assert data[0]["price"] == 8999.00


def test_get_product_prices_empty_ids_returns_empty_list(client):
    resp = client.get("/api/catalog/products/prices?ids=")
    assert resp.status_code == 200
    assert resp.json()["data"] == []


def test_wishlist_requires_auth(client):
    resp = client.get("/api/v1/wishlist")
    assert resp.status_code == 401  # HTTPBearer(auto_error=True) rejects missing credentials


def test_add_list_get_delete_wishlist_item(client, auth_token):
    add_resp = client.post("/api/v1/wishlist", json={"product_id": 1}, headers=_auth_header(auth_token))
    assert add_resp.status_code == 200
    item = add_resp.json()["data"]
    assert item["product_id"] == 1
    assert item["title"] == "Foldable Lightweight Wheelchair"
    wishlist_id = item["id"]

    list_resp = client.get("/api/v1/wishlist", headers=_auth_header(auth_token))
    assert list_resp.status_code == 200
    assert len(list_resp.json()["data"]) == 1

    get_resp = client.get(f"/api/v1/wishlist/{wishlist_id}", headers=_auth_header(auth_token))
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["id"] == wishlist_id

    delete_resp = client.delete(f"/api/v1/wishlist/{wishlist_id}", headers=_auth_header(auth_token))
    assert delete_resp.status_code == 200

    list_after = client.get("/api/v1/wishlist", headers=_auth_header(auth_token))
    assert list_after.json()["data"] == []


def test_add_duplicate_wishlist_item_is_rejected(client, auth_token):
    client.post("/api/v1/wishlist", json={"product_id": 1}, headers=_auth_header(auth_token))
    dup_resp = client.post("/api/v1/wishlist", json={"product_id": 1}, headers=_auth_header(auth_token))
    assert dup_resp.status_code == 409
    assert dup_resp.json()["message_code"] == "duplicate_wishlist_item"


def test_add_wishlist_item_for_missing_product_404s(client, auth_token):
    resp = client.post("/api/v1/wishlist", json={"product_id": 999}, headers=_auth_header(auth_token))
    assert resp.status_code == 404
    assert resp.json()["message_code"] == "product_not_found"


def test_get_wishlist_item_owned_by_another_user_404s(client, auth_token, other_user_token):
    add_resp = client.post("/api/v1/wishlist", json={"product_id": 1}, headers=_auth_header(auth_token))
    wishlist_id = add_resp.json()["data"]["id"]

    resp = client.get(f"/api/v1/wishlist/{wishlist_id}", headers=_auth_header(other_user_token))
    assert resp.status_code == 404
    assert resp.json()["message_code"] == "wishlist_item_not_found"


def test_delete_missing_wishlist_item_404s(client, auth_token):
    resp = client.delete("/api/v1/wishlist/999999", headers=_auth_header(auth_token))
    assert resp.status_code == 404
