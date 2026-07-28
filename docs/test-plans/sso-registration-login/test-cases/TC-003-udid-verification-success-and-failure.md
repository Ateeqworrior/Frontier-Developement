# TC-003 — Post-login UDID verification (success + failure)

**Automated by:** `test_auth.py::test_post_login_udid_verification_success_and_failure`,
`test_router_endpoints.py::test_verify_udid_service_unavailable_returns_502`,
`test_router_endpoints.py::test_verify_udid_rejects_invalid_token`,
`test_services.py::test_verify_udid_raises_invalid_credentials_for_unknown_user`

## Steps
1. Register and log in a user to obtain a bearer token.
2. POST `/api/auth/verify-udid` with a UDID starting `SF-` (success path).
3. POST with a UDID that doesn't match Sarthak Foundation records.
4. POST with UDID `TIMEOUT` (simulated service-unavailable).
5. Call with an invalid/garbage bearer token.
6. (Unit) Call `AuthService.verify_udid()` directly for a user id that doesn't exist.

## Expected result
- Step 2: `200`, `data.udid_verified == true`.
- Step 3: `422`, `success: false`.
- Step 4: `502`, `message_code == "udid_service_unavailable"`.
- Step 5: `401`, FastAPI default `{"detail": "invalid or expired token"}` (not the StandardResponse
  envelope, since this is raised before reaching the app's custom exception handlers).
- Step 6: raises `InvalidCredentialsError`.

## Pass/fail criteria
Pass if every variant above matches; fail on any status/body mismatch or unhandled exception.
