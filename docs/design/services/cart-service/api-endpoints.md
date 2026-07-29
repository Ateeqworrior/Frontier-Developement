# Cart Service — API Endpoints (US-004 contribution)

> Machine-readable OpenAPI 3.1 fragment (new/changed endpoints only): [`specs/cart-wishlist-management/api-schema.yaml`](../../../../specs/cart-wishlist-management/api-schema.yaml).

## New / changed endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/cart` | Bearer | **Extended.** Returns active + saved-for-later items, each enriched with live price/title/image from Catalog Service, plus a computed `totals` block (`subtotal`, `tax`, `delivery_charge`, `grand_total`) |
| GET | `/api/cart/delivery-feasibility` | Bearer | **New.** Query param `pin_code`; returns `feasible` \| `not_feasible` \| `unknown` |
| POST | `/api/cart/wishlist/{wishlist_id}/move-to-cart` | Bearer | **New.** Orchestrates: read wishlist item (Catalog Service) → upsert `cart_items` → delete wishlist item (Catalog Service) |

## Unchanged endpoints (existing, reused)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/cart/items` | Add product variant with quantity (HLD/LLD §5.3 `CartItemCreate`) |
| PUT | `/api/cart/items/{id}` | Update quantity (`CartItemUpdate`) |
| DELETE | `/api/cart/items/{id}` | Remove item |
| PUT | `/api/cart/items/{id}/save-for-later` | Toggle `is_saved_for_later` |

## Cross-service dependency (new — implemented by Catalog Service)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/catalog/products/prices?ids=1,2,3` | Batch price/title/image lookup for cart-total enrichment |

## Query/response reference (`GET /api/cart`)

| Field | Type | Notes |
|---|---|---|
| `data.items[].price` | decimal, nullable | `null` if Catalog Service's batch-price call fails (degraded mode) |
| `data.totals.subtotal` \| `.tax` \| `.delivery_charge` \| `.grand_total` | decimal, nullable | Entire `totals` object is `null` if price enrichment failed |

## Query parameter reference (`GET /api/cart/delivery-feasibility`)

| Param | Type | Notes |
|---|---|---|
| `pin_code` | string | Required, max length 10 |
