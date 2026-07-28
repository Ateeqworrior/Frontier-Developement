# TC-004 — Blocked user cannot log in

**Automated by:** `test_auth.py::test_blocked_user_cannot_log_in`

## Steps
1. Register a user.
2. Directly flip `User.is_active = False` in the DB (simulating a Super Admin block per US-014,
   whose own block endpoint is out of this story's scope).
3. Attempt CARS callback login for that user.

## Expected result
`403`, `message_code == "account_blocked"`.

## Pass/fail criteria
Pass if the login attempt is rejected with the exact status/code above.
