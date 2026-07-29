# TC-005 — Invalid credentials / password-reset entry point

**Automated by:** `test_auth.py::test_password_reset_entry_point_and_invalid_login`

## Steps
1. Register a user.
2. POST `/api/auth/login` with the correct email but a wrong password.

## Expected result
`401`, `message_code == "invalid_credentials"`.

## Note
Password reset itself is CARS-hosted (out of this service's UI scope per ADR-0001) — this test
covers the invalid-credentials branch that `/login`'s principal exchange guards, which is the
entry point a user hits before being redirected to CARS-hosted reset.

## Pass/fail criteria
Pass if the login attempt returns exactly the status/code above.
