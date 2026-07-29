# Cart Service — Error Handling (US-004 contribution)

Uses the platform-wide `StandardResponse` envelope and global exception handler chain (`ecom_core.utils.exception_handler`) — no new handler types introduced. New error codes for this story:

| Endpoint | Condition | HTTP Code | `message_code` |
|---|---|---|---|
| `GET /api/cart/delivery-feasibility` | `pin_code` missing or malformed | 422 | `invalid_pin_code` |
| `POST /api/cart/wishlist/{wishlist_id}/move-to-cart` | Wishlist item not found, or belongs to another user | 404 | `wishlist_item_not_found` |
| `POST /api/cart/wishlist/{wishlist_id}/move-to-cart` | Cart insert succeeds but the Catalog Service wishlist-delete call fails | 200 (partial) | `wishlist_remove_failed` — response includes `wishlist_removed: false`; the item **is** in the cart, not rolled back (see [ADR-0004](../../../architecture/adrs/0004-wishlist-ownership-cart-orchestration.md)) |
| `GET /api/cart` | Catalog Service batch-price call times out or errors | 200 (degraded) | n/a — response returns items with `price: null` and `totals: null`, not an error |
| `GET /api/cart/delivery-feasibility` | Logistics feasibility call (US-013) times out or errors | 200 (degraded) | n/a — response returns `feasibility: "unknown"`, not an error |

No retry policy for either the delivery-feasibility call or the batch-price call — the shared `async_request()` client's 10s timeout applies once; on failure, both endpoints return `200` in a degraded shape rather than surfacing an error, per the platform's degraded-mode NFR (a partial-failure dependency must not fail the whole request).
