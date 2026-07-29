# TC-004 — Validation errors and unpublished/not-found products

**Automated by:** `test_discovery.py` (`test_invalid_price_range_is_rejected`,
`test_unpublished_product_is_not_discoverable`), `test_router_integration.py`
(`test_search_price_range_validation`, `test_min_rating_out_of_bounds_is_rejected`),
`test_services_unit.py` (`test_validate_price_range_allows_equal_bounds`,
`test_validate_price_range_rejects_inverted_bounds`), `test_repository_unit.py::test_get_by_id_returns_none_for_unpublished`

## Steps
1. GET `/products` or `/products/search` with `price_min > price_max`.
2. GET `/products` with `price_min == price_max` (boundary case).
3. GET `/products?min_rating=` outside the `0–5` range.
4. GET `/products/{id}` for a `Draft` (unpublished) or nonexistent product ID.

## Expected result
- `price_min > price_max` → `422 invalid_price_range` on both endpoints.
- `price_min == price_max` → allowed (not an error).
- `min_rating` outside `[0, 5]` → `422` (FastAPI query-validation, before reaching the service layer).
- Unpublished/nonexistent product → `404 product_not_found`.

## Pass/fail criteria
Pass if every case returns the exact status/error code above; fail on any mismatch.
