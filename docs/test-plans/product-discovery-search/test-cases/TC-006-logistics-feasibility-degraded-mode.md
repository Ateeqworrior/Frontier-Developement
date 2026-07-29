# TC-006 — Logistics feasibility client degraded-mode behavior

**Automated by:** `test_logistics_client_unit.py` (`test_no_pin_code_returns_unknown_without_calling_out`,
`test_feasible_response`, `test_not_feasible_response`, `test_non_200_response_is_unknown`,
`test_unreachable_service_degrades_to_unknown`)

## Steps
1. Call `check_delivery_feasibility(None)` (no PIN code supplied).
2. Call with a mocked `async_request` returning `{"data": {"feasible": true}}` / `{"feasible": false}`.
3. Call with a mocked `async_request` returning a non-200 status.
4. Call with a mocked `async_request` raising an `httpx` connection/timeout error.

## Expected result
- No PIN code → `"unknown"`, and the Logistics endpoint is never called (short-circuit).
- `feasible: true`/`false` → `"feasible"`/`"not_feasible"`.
- Non-200 response or a connection/timeout error → `"unknown"` — this never propagates as an
  exception up to the product-detail endpoint (see TC-003), per the platform's degraded-mode NFR.

## Pass/fail criteria
Pass if every branch returns the expected string and no exception escapes `check_delivery_feasibility`;
fail otherwise.
