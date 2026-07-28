# TC-006 — Router edge cases: auth-required endpoints, duplicate/invalid registration

**Automated by:** `test_router_endpoints.py` (`test_cars_authorize_redirect_returns_url`,
`test_me_endpoint_returns_current_user`, `test_me_endpoint_without_token_is_rejected`,
`test_register_duplicate_email_returns_409`, `test_register_with_invalid_role_returns_422`,
`test_register_with_missing_field_returns_422`), `test_repository.py` (duplicate detection on
mobile/seller/sponsor code), `test_services.py::test_register_user_with_role_missing_from_db_raises_duplicate_resource_error`,
`test_ecom_core.py` (RBAC checkers, `UserPayload`, `SoftDeleteMixin`, exception handlers, shared HTTP client)

## Steps (representative)
1. GET `/api/auth/cars/authorize` with no auth → returns a redirect URL.
2. GET `/api/auth/me` with a valid token → returns the current user; without a token → rejected.
3. Register the same email twice → `409 duplicate_resource`.
4. Register with a role name absent from the DB's `roles` table (bypassing schema validation
   at the service layer) → `DuplicateResourceError` with `message_code=invalid_role`.
5. Register with an unrecognized role string → `422` at the schema-validation layer (the
   `Role` Literal type rejects it before `AuthService` is reached).
6. `role_required()` / `make_require_permission()` checkers allow/deny per `ROLE_PERMISSIONS`,
   including the `category:*`-style wildcard match.

## Expected result
Each call returns the status/code named above; RBAC checkers raise `HTTPException(403)` exactly
when the role/permission doesn't match.

## Pass/fail criteria
Pass if every representative case above matches; fail on any unexpected status or a checker that
allows/denies incorrectly.
