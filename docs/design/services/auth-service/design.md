# Auth Service — Design (US-001 contribution)

> Port 8001 · DB `sarthak_auth_service` · Prefix `/api/auth/` · Owns: `services/auth-service/` per [US-001](../../../user-stories/stories/domain-registration-auth/US-001-sso-registration-login.md).

## Layer architecture (existing, unchanged)

```
API Layer (router.py)        → /login /register /me /update/{id} /roles/* /admin/*  [+ /cars/callback, /verify-udid — new]
Service Layer                → AuthService (register, login, exchange) · UserService · RoleService
Repository Layer             → UserRepository (check_duplicates, create_user, get_user_by_email, ...)
MySQL (sarthak_auth_service)
```

## New for US-001

1. **`GET /api/auth/cars/callback`** — OIDC callback handler. Exchanges CARS authorization code for a CARS ID token, validates it, derives a `principal` object, then calls the existing `AuthService.exchange_principal()` path. See [ADR-0001](../../../architecture/adrs/0001-cars-sso-principal-exchange.md).
2. **Blocked-account check in `AuthService.exchange_principal()`** — before minting a JWT, check `user.is_active`. If `False`, return `403` with a distinct `account_blocked` error code (not the generic `401 invalid_credentials`), so the frontend can render Screen 5 (`docs/design/ui-ux/wireframes/us-001-sso-registration-login.md`).
3. **`POST /api/auth/verify-udid`** (Bearer-protected) — new service method `AuthService.verify_udid(user_id, udid_number)`:
   - Calls the Sarthak Foundation UDID endpoint via `ecom_core.utils.http_client.async_request()` (existing shared client, 10s timeout).
   - On match: sets `users.udid_verified = True`, `udid_verified_at = now()`, commits, emits `USER_UPDATED` outbox event.
   - On no-match/error: returns `422` with the verification failure reason; no DB write.

## Reused as-is (no changes)

- JWT issuance (`create_internal_jwt`): claims `sub`, `email`, `role`, `exp`, `iat`, `iss`, HS256, shared `SECRET_KEY`.
- `auth_common` RBAC middleware (`require_permission()`, `role_required()`) — every other service already verifies tokens locally; no propagation changes needed.
- `/register`, `/reset-password`, `/me`, `/update/{user_id}`, `/roles/*`, `/admin/*` — unchanged by this story.
- Transactional Outbox pattern for `USER_CREATED` / `USER_UPDATED`.

## Persona/integration mapping

| Persona | Touchpoint |
|---|---|
| Buyer, Vendor, Sponsor, Donor | Registration + login via CARS SSO |
| Buyer | UDID verification (sponsored-purchase gate, consumed by US-005 checkout) |
| Super Admin | Sets `is_active = False` to block (US-014) — enforced here at login |
