# TC-002 — Registered user logs in via CARS callback

**Automated by:** `services/auth-service/tests/test_auth.py::test_registered_user_logs_in`,
`tests/test_router_endpoints.py::test_login_endpoint_success`,
`tests/test_router_endpoints.py::test_cars_callback_rejects_unrecognized_code`

## Steps
1. Register a user.
2. GET `/api/auth/cars/callback?code=dev-code:<email>:<password>:true`.
3. (Variant) POST `/api/auth/login` directly with the same principal.
4. (Negative variant) GET the callback with a code not prefixed `dev-code:`.

## Expected result
- Steps 2/3: `200 OK`, `data.role == "user"`, `data.access_token` present and non-empty.
- Step 4: `401`, `message_code == "cars_auth_failed"`.

## Pass/fail criteria
Pass if all three variants match the expected result above.
