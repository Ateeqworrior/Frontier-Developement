# Cart Service — Design (US-004 contribution)

> Port 8003 · DB `sarthak_cart_service` · Prefix `/api/cart/` · Owns: `services/cart-service/` per [US-004](../../../user-stories/stories/domain-cart-wishlist/US-004-cart-wishlist-management.md).

## Layer architecture (existing `cart` module, extended)

```
API Layer (router.py)        → existing /items (add/update/remove, HLD/LLD §5.3)
                                [+ /cart (list + totals) — extended
                                 + /cart/delivery-feasibility — new
                                 + /cart/wishlist/{id}/move-to-cart — new]
Service Layer                 → CartService (existing CRUD)
                                [+ CartTotalsService — new
                                 + WishlistMoveService — new]
Repository Layer              → CartItemRepository (existing, unchanged)
MySQL (sarthak_cart_service)
```

## New for US-004

1. **`GET /api/cart`** — extends the existing cart-list read. For each `cart_items` row, `CartTotalsService` batch-fetches live price/title/image from Catalog Service (`GET /api/catalog/products/prices?ids=`, new — see below), then computes:
   - `subtotal` = Σ (`price × quantity`) over non-saved-for-later items.
   - `tax` = `subtotal × TAX_RATE` (flat platform-config constant, default 5%).
   - `delivery_charge` = flat `DELIVERY_FLAT_CHARGE` constant (default ₹49), waived when `subtotal >= FREE_DELIVERY_THRESHOLD` (default ₹499). Not PIN-dependent — the feasibility check (below) is a separate yes/no gate, not a variable freight-rate calculator; the HLD/LLD and story ACs do not specify PIN-based rate tiers.
   - `grand_total` = `subtotal + tax + delivery_charge`.
   - Totals are computed fresh on every request/mutation response — nothing is persisted or cached, so "recalculates immediately" (AC) is satisfied by construction.
2. **`GET /api/cart/delivery-feasibility?pin_code=`** — `CartTotalsService.get_delivery_feasibility(pin_code)` calls the same Logistics feasibility contract US-003 established (`GET /logistics/feasibility?pin=`) via `ecom_core.utils.http_client.async_request()` (10s timeout), reusing the identical degraded-mode fallback: on timeout/unavailable, returns `feasibility: "unknown"` (200), never a hard failure.
3. **`POST /api/cart/wishlist/{wishlist_id}/move-to-cart`** — `WishlistMoveService`:
   1. `GET /api/v1/wishlist/{wishlist_id}` (Catalog Service) to resolve `product_id` and confirm ownership (`user_id` must match the caller).
   2. Upsert `cart_items` (increment `quantity` if the product is already in the cart, else insert with `quantity=1`).
   3. `DELETE /api/v1/wishlist/{wishlist_id}` (Catalog Service).
   - See [ADR-0004](../../../architecture/adrs/0004-wishlist-ownership-cart-orchestration.md) for why wishlist data is not migrated into Cart Service, and the partial-failure handling if step 3 fails after step 2 succeeds.

## Reused as-is (no changes)

- `cart_items` schema and existing `POST /items` (add), `PUT /items/{id}` (quantity update), `DELETE /items/{id}` (remove), and the `is_saved_for_later` save-for-later toggle (HLD/LLD §5.2.1, §5.3) — all unchanged by this story.
- `user_local` sync via `USER_CREATED`/`USER_UPDATED` outbox consumption (existing Strategy 1 pattern, HLD/LLD §8.3).
- Catalog Service's `wishlists` table and existing `/api/v1/wishlist/*` CRUD (HLD/LLD §4.3.5) — untouched; only called, not modified.
- `StandardResponse` envelope and global exception handler chain.

## New upstream dependency (owned by Catalog Service team, not this story)

`GET /api/catalog/products/prices?ids=1,2,3` — batch price/title/image lookup, avoiding an N+1 call pattern from Cart Service's totals enrichment. This is the one piece of this story's scope that lands in a different service's codebase; documented here as a required contract, tracked against the Catalog Service team the same way US-003 tracked its Logistics dependency against US-013.

## Known gap flagged (not in this story's scope)

The existing Cart Service endpoints have **zero RBAC permission checks** today (platform status: "Planned for next phase" per the HLD/LLD rollout tracker). The platform's centralized-RBAC decision (system-design.md "Key Architectural Decisions") requires `require_permission()` on every endpoint. This story does not add RBAC to the pre-existing endpoints — that is out of scope for an architecture-only story and is called out here as a carried-forward risk for whoever implements Step 5 (Full-Stack Implementation) to decide whether to close it opportunistically while the service is being touched.

## Persona/integration mapping

| Persona | Touchpoint |
|---|---|
| Buyer | Add/update/remove cart items, view cart with totals, check PIN feasibility, move wishlist items to cart |
| Catalog Service | Provides batch price lookup (new) and wishlist CRUD (existing, called not changed) |
| Logistics Partner (US-013) | Feasibility endpoint consumed read-only by this story, same contract as US-003 |
