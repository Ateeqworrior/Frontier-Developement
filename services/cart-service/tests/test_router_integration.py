"""Integration tests exercising the full HTTP request/response cycle (router ->
service -> repository -> real per-test SQLite DB) for cart-service, with Catalog
Service / Logistics dependencies stubbed via the fake_* fixtures in conftest.py."""


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_cart_requires_auth(client):
    resp = client.get("/api/cart")
    assert resp.status_code == 401


def test_add_item_then_get_cart_with_totals(client, auth_token, fake_prices):
    add_resp = client.post(
        "/api/cart/items", json={"product_id": 1, "quantity": 2}, headers=_auth_header(auth_token)
    )
    assert add_resp.status_code == 200
    assert add_resp.json()["data"]["quantity"] == 2

    cart_resp = client.get("/api/cart", headers=_auth_header(auth_token))
    assert cart_resp.status_code == 200
    data = cart_resp.json()["data"]
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert item["title"] == "Wheelchair"
    assert item["price"] == 8999.0

    # subtotal 17998.0 -> below free-delivery threshold (499.0 default is irrelevant
    # here since it's much smaller; use the configured default: threshold 499.0, so
    # this large cart is well above it -> delivery is free.
    totals = data["totals"]
    assert totals["subtotal"] == 17998.0
    assert totals["delivery_charge"] == 0.0
    assert totals["tax"] == round(17998.0 * 0.05, 2)
    assert totals["grand_total"] == round(17998.0 + totals["tax"], 2)


def test_add_same_product_twice_increments_quantity_not_duplicates(client, auth_token, fake_prices):
    client.post("/api/cart/items", json={"product_id": 2, "quantity": 1}, headers=_auth_header(auth_token))
    resp = client.post("/api/cart/items", json={"product_id": 2, "quantity": 3}, headers=_auth_header(auth_token))
    assert resp.status_code == 200
    assert resp.json()["data"]["quantity"] == 4

    cart = client.get("/api/cart", headers=_auth_header(auth_token)).json()["data"]
    assert len(cart["items"]) == 1


def test_update_and_remove_item(client, auth_token, fake_prices):
    add_resp = client.post("/api/cart/items", json={"product_id": 2, "quantity": 1}, headers=_auth_header(auth_token))
    item_id = add_resp.json()["data"]["id"]

    update_resp = client.put(f"/api/cart/items/{item_id}", json={"quantity": 5}, headers=_auth_header(auth_token))
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["quantity"] == 5

    delete_resp = client.delete(f"/api/cart/items/{item_id}", headers=_auth_header(auth_token))
    assert delete_resp.status_code == 200

    cart = client.get("/api/cart", headers=_auth_header(auth_token)).json()["data"]
    assert cart["items"] == []


def test_update_item_owned_by_another_user_404s(client, auth_token, other_user_token, fake_prices):
    add_resp = client.post("/api/cart/items", json={"product_id": 2, "quantity": 1}, headers=_auth_header(auth_token))
    item_id = add_resp.json()["data"]["id"]

    resp = client.put(f"/api/cart/items/{item_id}", json={"quantity": 2}, headers=_auth_header(other_user_token))
    assert resp.status_code == 404
    assert resp.json()["message_code"] == "cart_item_not_found"


def test_save_for_later_toggle_excludes_item_from_totals(client, auth_token, fake_prices):
    add_resp = client.post("/api/cart/items", json={"product_id": 2, "quantity": 1}, headers=_auth_header(auth_token))
    item_id = add_resp.json()["data"]["id"]

    toggle_resp = client.put(
        f"/api/cart/items/{item_id}/save-for-later",
        json={"is_saved_for_later": True},
        headers=_auth_header(auth_token),
    )
    assert toggle_resp.status_code == 200
    assert toggle_resp.json()["data"]["is_saved_for_later"] is True

    cart = client.get("/api/cart", headers=_auth_header(auth_token)).json()["data"]
    assert len(cart["items"]) == 1  # still listed
    assert cart["totals"]["subtotal"] == 0.0  # but excluded from totals


def test_get_cart_degrades_when_catalog_service_unavailable(client, auth_token, monkeypatch):
    import app.services as services_module

    async def _fail(product_ids):
        return {}

    monkeypatch.setattr(services_module.catalog_client, "get_batch_prices", _fail)

    client.post("/api/cart/items", json={"product_id": 1, "quantity": 1}, headers=_auth_header(auth_token))
    cart = client.get("/api/cart", headers=_auth_header(auth_token)).json()["data"]
    assert cart["items"][0]["price"] is None
    assert cart["totals"] is None


def test_delivery_feasibility_happy_path(client, auth_token, fake_feasibility):
    resp = client.get("/api/cart/delivery-feasibility?pin_code=560001", headers=_auth_header(auth_token))
    assert resp.status_code == 200
    assert resp.json()["data"]["feasibility"] == "feasible"


def test_delivery_feasibility_missing_pin_is_422(client, auth_token):
    resp = client.get("/api/cart/delivery-feasibility", headers=_auth_header(auth_token))
    assert resp.status_code == 422
    assert resp.json()["message_code"] == "invalid_pin_code"


def test_delivery_feasibility_degrades_to_unknown_on_logistics_outage(client, auth_token, monkeypatch):
    import app.services as services_module

    async def _fake_check(pin_code):
        return "unknown"

    monkeypatch.setattr(services_module, "check_delivery_feasibility", _fake_check)

    resp = client.get("/api/cart/delivery-feasibility?pin_code=560001", headers=_auth_header(auth_token))
    assert resp.status_code == 200
    assert resp.json()["data"]["feasibility"] == "unknown"


def test_move_wishlist_item_to_cart_success(client, auth_token, fake_wishlist):
    resp = client.post("/api/cart/wishlist/101/move-to-cart", headers=_auth_header(auth_token))
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["cart_item"]["product_id"] == 1
    assert data["wishlist_removed"] is True
    assert 101 not in fake_wishlist["items"]  # actually removed from the (fake) wishlist


def test_move_wishlist_item_to_cart_not_found(client, auth_token, fake_wishlist):
    resp = client.post("/api/cart/wishlist/999999/move-to-cart", headers=_auth_header(auth_token))
    assert resp.status_code == 404
    assert resp.json()["message_code"] == "wishlist_item_not_found"


def test_move_wishlist_item_to_cart_partial_success_when_delete_fails(client, auth_token, monkeypatch):
    import app.services as services_module

    async def _fake_get(wishlist_id, token):
        return {"id": wishlist_id, "product_id": 1, "title": "Wheelchair", "image_url": None, "price": 8999.0}

    async def _fake_delete(wishlist_id, token):
        return False  # Catalog Service delete call failed

    monkeypatch.setattr(services_module.catalog_client, "get_wishlist_item", _fake_get)
    monkeypatch.setattr(services_module.catalog_client, "delete_wishlist_item", _fake_delete)

    resp = client.post("/api/cart/wishlist/101/move-to-cart", headers=_auth_header(auth_token))
    assert resp.status_code == 200  # item IS in the cart — not a hard failure
    data = resp.json()["data"]
    assert data["wishlist_removed"] is False
    assert data["cart_item"]["product_id"] == 1
