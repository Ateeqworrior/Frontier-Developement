# Auth Service — Error Handling (US-001 contribution)

Uses the platform-wide `StandardResponse` envelope and global exception handler chain (`ecom_core.utils.exception_handler`) — no new handler types introduced. New error codes for this story:

| Endpoint | Condition | HTTP Code | `message_code` |
|---|---|---|---|
| `POST /api/auth/login` (via `cars/callback` → `exchange_principal`) | `user.is_active == False` | 403 | `account_blocked` |
| `POST /api/auth/login` | Invalid principal / user not found | 401 | `invalid_credentials` (existing) |
| `GET /api/auth/cars/callback` | CARS code exchange fails / invalid ID token | 401 | `cars_auth_failed` |
| `POST /api/auth/verify-udid` | Sarthak Foundation endpoint returns no-match | 422 | `udid_not_matched` |
| `POST /api/auth/verify-udid` | Sarthak Foundation endpoint unreachable/timeout (>10s) | 502 | `udid_service_unavailable` |

No retry policy for `verify-udid` — the shared `async_request()` client's 10s timeout applies; the frontend's "Skip" action (Screen 4, `docs/design/ui-ux/wireframes/us-001-sso-registration-login.md`) is the user-facing fallback rather than automatic retry.
