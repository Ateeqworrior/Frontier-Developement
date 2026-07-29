# Test Strategy — MartSarathi Microservices

## Approach

- **Unit tests**: exercise a single module/class in isolation (repository queries,
  service business logic, RBAC/permission checks, shared `ecom_core` utilities).
- **Integration tests**: exercise a full request through FastAPI's `TestClient`
  against a real (per-test, file-backed) SQLite database — no ORM/DB mocking.
  Each service substitutes SQLite for the MySQL used in staging/production;
  schema and query behavior are compatible at the level these tests exercise.
- **Frontend**: component/unit tests via Vitest + React Testing Library, run
  against the real DOM (jsdom) with the network layer (`fetch`) mocked at the
  boundary — component logic, not the browser, is under test here. Full
  browser-based E2E is covered in Step 7 (`/end-to-end-testing-and-bug-resolution-for-this-story`).

## Tooling

| Layer | Tooling |
|---|---|
| Backend unit/integration | `pytest`, `pytest-cov`, `coverage.py`, FastAPI `TestClient`, SQLAlchemy + SQLite |
| Frontend unit/component | `vitest`, `@testing-library/react`, `@testing-library/user-event`, `jsdom`, `@vitest/coverage-v8` |

## Environments

- Backend tests run against an ephemeral SQLite file per test (via the `client`
  pytest fixture) — no shared state between tests, no external network calls
  (CARS OIDC / Sarthak Foundation UDID calls hit the in-repo dev-mode stubs
  described in `app/cars_client.py`, not real external endpoints).
- Frontend tests run in jsdom with `fetch` mocked per test — no real backend
  process required.

## Coverage targets

- **Minimum**: 80% statement coverage per service/app, enforced per this
  workflow's Step 6 exit gate.
- Gaps below 100% must be attributable to one of: (a) genuinely out-of-scope
  stub/bootstrap code, (b) a branch requiring a real external dependency not
  available in this environment, (c) framework wiring with no branching logic.
  Each such gap must be named explicitly in the feature's `test-plan.md` —
  coverage numbers are never inflated with low-value tests written purely to
  hit a percentage.

## Out of scope for this phase

- Full browser-driven E2E walkthroughs of each screen (Step 7).
- Load/performance testing.
- Security penetration testing (see BFSI knowledge pack for the eventual
  compliance/audit checklist this will need to satisfy before production).
