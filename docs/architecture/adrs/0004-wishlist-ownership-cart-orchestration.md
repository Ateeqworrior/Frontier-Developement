# ADR-0004 — Wishlist stays owned by Catalog Service; Cart Service orchestrates move-to-cart

Status: Accepted

## Context

[US-004](../../user-stories/stories/domain-cart-wishlist/US-004-cart-wishlist-management.md) (Jira [CP-19](https://ateequrrahaman2004.atlassian.net/browse/CP-19)) requires "Wishlist to cart" (AC: *Given a Buyer has items in their wishlist, When they move an item to the cart, Then it is removed from the wishlist and added to the cart*) and a general wishlist CRUD capability. The story's `Owns:` header names `services/cart-service/`, which could be read as "wishlist data belongs to Cart Service."

However, the existing HLD/LLD (§4.3.2, §15) already defines a `wishlists` table (`user_id`, `product_id`, unique constraint on the pair) owned by the **Catalog Service** (`sarthak_catalog_service` DB), with a live `/api/v1/wishlist/*` route prefix (§9 API Gateway Routing Table). Wishlist CRUD is therefore already built and in production use before this story starts.

The platform's non-negotiable database-per-service rule (project context "Known Constraints"; system-design.md "Key Architectural Decisions") forbids cross-service DB access and cross-service joins. Moving `wishlists` into `sarthak_cart_service` would require a data migration, a breaking change to the existing `/api/v1/wishlist/*` contract, and duplicate the product-existence validation Catalog Service already performs on write.

## Decision

Keep `wishlists` in the Catalog Service database, unchanged. US-004 does not touch Catalog Service's wishlist schema or its existing CRUD endpoints (`GET/POST/DELETE /api/v1/wishlist/*`) — those are reused as-is.

Cart Service owns one new orchestration endpoint, `POST /api/cart/wishlist/{wishlist_id}/move-to-cart`, that:
1. Calls Catalog Service's existing `GET /api/v1/wishlist/{wishlist_id}` to resolve `product_id` (ownership/ existence check).
2. Inserts (or increments) the corresponding row in Cart Service's own `cart_items` table.
3. Calls Catalog Service's existing `DELETE /api/v1/wishlist/{wishlist_id}` to remove it from the wishlist.

Both calls use the shared `ecom_core.utils.http_client.async_request()` client (JWT forwarded), consistent with how US-003 calls the Logistics integration. If step 3 fails after step 2 succeeds, the endpoint returns `207`-style partial success with `wishlist_removed: false` in the payload rather than rolling back the cart insert — duplicating an item into the cart is a safe, user-correctable outcome; silently losing it from both places is not. No SAGA/compensation orchestration is introduced for this — it is a two-call best-effort sequence, not a multi-service business transaction.

## Consequences

- No schema migration, no breaking change to the live `/api/v1/wishlist/*` contract, no cross-service DB access — consistent with the platform's mandatory database-per-service rule.
- Cart Service takes on a synchronous dependency on Catalog Service's availability for the move-to-cart action only; plain cart CRUD (add/update/remove/list/totals) has no such dependency.
- "Owns: services/cart-service/" in the story header is scoped to the new orchestration and totals/feasibility endpoints, not to wishlist data ownership.

## Alternatives considered

- **Migrate `wishlists` to `sarthak_cart_service`:** rejected — requires a data migration and a breaking contract change to a live endpoint, for no functional gain; violates "no speculative or ad-hoc schema changes."
- **Synchronous two-phase-commit-style rollback on step 3 failure:** rejected — the platform explicitly avoids distributed 2PC (system-design.md), and a duplicate-safe partial-success response is simpler and matches the platform's degraded-mode NFR philosophy (US-003 precedent).
