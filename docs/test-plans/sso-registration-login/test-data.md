# Test Data — SSO Registration, Login & UDID Verification (US-001 / CP-16)

## Seed data (backend)

Every test run seeds the standard role set via the `client` pytest fixture
(`services/auth-service/tests/conftest.py`): `user`, `vendor`, `sponsor`, `donor`, `admin`, `super_admin`.

## CARS OIDC dev-mode codes (`app/cars_client.py`)

The stub decodes `dev-code:<email>:<password>:<isEnabled>` — used in place of a real CARS
authorization code until ADR-0001 is Accepted:

- `dev-code:<email>:<password>:true` → valid principal, `isEnabled=true`
- Any other string not prefixed `dev-code:` → `cars_auth_failed` (401)

## Sarthak Foundation UDID dev-mode values (`app/cars_client.py`)

- `SF-*` (any UDID starting with `SF-`) → verified
- `TIMEOUT` → simulates the endpoint being unreachable (502 `udid_service_unavailable`)
- anything else → `udid_not_matched` (422)

## Representative test users used across test cases

| Email | Role | Purpose |
|---|---|---|
| `buyer@example.com` | user | Registration happy path |
| `login@example.com` | user | Login via CARS callback |
| `udid@example.com` / `udid2@example.com` | user | UDID verify success / failure |
| `blocked@example.com` | user | Manually flipped `is_active=False` to simulate a Super Admin block (US-014) |
| `reset@example.com` | user | Invalid-credentials / password-reset entry point |

No real credentials, tokens, or external service accounts are used anywhere in this suite.
