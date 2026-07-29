# TC-005 — Optional-bearer auth: sponsored pricing shown only when authenticated

**Automated by:** `test_router_integration.py` (`test_authenticated_request_sees_sponsored_discount`,
`test_invalid_bearer_token_is_treated_as_anonymous`), `test_services_unit.py::test_get_product_detail_applies_sponsored_discount_only_when_authenticated`

## Steps
1. GET `/api/catalog/products/{id}` for a `sponsored="yes"` product with a valid `Bearer` JWT.
2. GET the same endpoint with no `Authorization` header.
3. GET the same endpoint with a malformed/invalid `Bearer` token.

## Expected result
- Valid token → `price_breakdown.discounted_price` is populated (10% off the base price by default,
  per `settings.sponsored_discount_percent`).
- No token or an invalid token → `discounted_price: null` — the endpoint degrades to anonymous
  behavior rather than rejecting the request (these are public reads; the `HTTPBearer(auto_error=False)`
  dependency never raises).

## Pass/fail criteria
Pass if discounted pricing appears only for the valid-token case and the invalid-token case behaves
identically to the anonymous case (no 401); fail otherwise.
