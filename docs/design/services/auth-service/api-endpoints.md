# Auth Service — API Endpoints (US-001 contribution)

> Machine-readable OpenAPI 3.1 fragment (new endpoints only): [`specs/sso-registration-login/api-schema.yaml`](../../../../specs/sso-registration-login/api-schema.yaml).

## New endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/auth/cars/callback` | None | OIDC callback — exchanges CARS auth code, derives principal, mints internal JWT via existing `exchange_principal()` |
| POST | `/api/auth/verify-udid` | Bearer | Buyer submits UDID for post-login sponsored-purchase verification against the Sarthak Foundation endpoint |

## Modified endpoints

| Method | Endpoint | Change |
|---|---|---|
| POST | `/api/auth/login` | `exchange_principal()` now checks `user.is_active`; returns `403 account_blocked` distinctly from `401 invalid_credentials` |

## Unchanged endpoints (existing, reused)

`POST /register`, `POST /reset-password`, `GET /me`, `PUT /update/{user_id}`, `GET /user/{user_id}/details`, `GET /roles/getAll`, `GET /roles/{role_id}`, `GET /roles/name/{role_name}`, `GET /roles/permissions/{role_name}`, `GET /admin/getDetailsByRole`, `DELETE /admin/delete/{user_id}`.
