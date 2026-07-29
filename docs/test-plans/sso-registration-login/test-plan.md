# Test Plan — SSO Registration, Login & UDID Verification (US-001 / CP-16)

Mirrors `specs/sso-registration-login/`. See `../../architecture/adrs/0001-cars-sso-principal-exchange.md`
for the CARS OIDC decision this feature depends on (Status: Proposed).

## Scope

Backend (`services/auth-service`, `libs/ecom-core`) and frontend (`frontend/src/features/auth/*`,
`frontend/src/api/authClient.js`) code delivered in Step 5 for the 6 wireframe screens and their
supporting endpoints: `/api/auth/register`, `/cars/authorize`, `/cars/callback`, `/login`,
`/verify-udid`, `/me`.

## Approach

Unit tests isolate repository/service/RBAC logic; integration tests exercise full HTTP request/response
cycles against a real per-test SQLite database (see `test-strategy.md`). Frontend tests exercise each
screen component with the network boundary (`authClient`) mocked, plus direct unit tests of
`authClient` itself against a mocked `fetch`.

## Entry criteria

- Step 5 (full-stack implementation) complete: PR #2 open, all 5 Gherkin-scenario smoke tests
  from `test_auth.py` passing.

## Exit criteria

- ≥ 80% statement coverage, backend and frontend, measured independently.
- All tests green (no skipped/xfail tests hiding a real gap).
- Every uncovered line/branch is named and justified in `coverage-report.html` — no silent gaps.

## Test tooling & environment

See `../test-strategy.md`. No environment variables required beyond the defaults in
`app/config.py` (SQLite dev DB) and `frontend/.env` (defaults to `http://localhost:8001/api/auth`).

## Test cases

| ID | Title | Layer |
|---|---|---|
| [TC-001](test-cases/TC-001-new-user-registers-via-cars-sso.md) | New user registers via CARS SSO | Backend integration |
| [TC-002](test-cases/TC-002-registered-user-logs-in.md) | Registered user logs in via CARS callback | Backend integration |
| [TC-003](test-cases/TC-003-udid-verification-success-and-failure.md) | Post-login UDID verification (success + failure) | Backend integration |
| [TC-004](test-cases/TC-004-blocked-user-cannot-log-in.md) | Blocked user cannot log in | Backend integration |
| [TC-005](test-cases/TC-005-invalid-credentials-and-password-reset-entry.md) | Invalid credentials / password-reset entry point | Backend integration |
| [TC-006](test-cases/TC-006-router-and-rbac-edge-cases.md) | Router edge cases: auth-required endpoints, duplicate/invalid registration | Backend integration + unit |
| [TC-007](test-cases/TC-007-frontend-auth-screens.md) | Frontend Screens 1–5 render and interaction behavior | Frontend component |

## Results

**All 49 tests passing** (32 backend, 17 frontend) as of this run. Coverage: backend 97%,
frontend 88.3% — both above the 80% exit-gate threshold. Summary: `coverage-report.html`
(per-line HTML reports are regenerable locally per that file's instructions — not committed
as they're generated artifacts).

## Known gaps (accepted, not silently dropped)

- CARS OIDC and Sarthak Foundation UDID integrations are dev-mode stubs (ADR-0001 is
  `Proposed`, not `Accepted`) — a few defensive branches in `app/cars_client.py` around
  malformed/empty inputs to those stubs are untested since they guard conditions that can't
  occur through the tested code paths yet.
- Browser-based E2E walkthroughs of the 5 wireframe screens are explicitly deferred to Step 7
  (`/end-to-end-testing-and-bug-resolution-for-this-story`) — this step covers component-level
  frontend tests only, not a real browser session.
