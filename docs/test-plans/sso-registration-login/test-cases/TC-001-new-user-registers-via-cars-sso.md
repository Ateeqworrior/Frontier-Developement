# TC-001 — New user registers via CARS SSO

**Automated by:** `services/auth-service/tests/test_auth.py::test_new_user_registers_via_cars_sso`

## Steps
1. POST `/api/auth/register` with email, username, password, `role=user`.

## Expected result
- `200 OK`, `success: true`.
- `data.role == "user"`, `data.udid_verified == false` (UDID not required to complete registration).

## Pass/fail criteria
Pass if the response matches the above; fail on any other status code or missing/incorrect field.
