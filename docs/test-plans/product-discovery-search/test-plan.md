# Test Plan — Product Discovery, Search & Filtering (US-003 / CP-18)

Mirrors `specs/product-discovery-search/`. See `../../architecture/adrs/0002-mysql-fulltext-for-product-search.md`
for the MySQL-FULLTEXT-vs-Elasticsearch decision this feature's search endpoint depends on (Status: Accepted).

## Scope

Backend (`services/catalog-service`, `libs/ecom-core` additions) and frontend
(`frontend/src/features/catalog/*`, `frontend/src/api/catalogClient.js`) code delivered in Step 5:
`GET /api/catalog/products`, `GET /api/catalog/products/search`, `GET /api/catalog/products/{id}`.

## Approach

Unit tests isolate `ProductRepository` query logic, `ProductDiscoveryService` pricing/validation
logic, and the `logistics_client` degraded-mode branches; integration tests exercise full HTTP
request/response cycles against a real per-test SQLite database (see `../test-strategy.md`).
Frontend tests exercise both catalog page components with the network boundary (`catalogClient`)
mocked, plus direct unit tests of `catalogClient` itself against a mocked `fetch`.

## Entry criteria

- Step 5 (full-stack implementation) complete: PR #3 open, all 7 Gherkin-scenario smoke tests
  from `test_discovery.py` passing.

## Exit criteria

- ≥ 80% statement coverage, backend and frontend, measured independently.
- All tests green (no skipped/xfail tests hiding a real gap).
- Every uncovered line/branch is named and justified in `coverage-report.html` — no silent gaps.

## Test tooling & environment

See `../test-strategy.md`. No environment variables required beyond the defaults in
`app/config.py` (SQLite dev DB) and `frontend/.env` (defaults to `http://localhost:8002/api/catalog`).

## Test cases

| ID | Title | Layer |
|---|---|---|
| [TC-001](test-cases/TC-001-browse-by-category-and-filter-sort.md) | Browse by category, filter, and sort | Backend integration + unit |
| [TC-002](test-cases/TC-002-keyword-search.md) | Keyword search (relevance-ranked) | Backend integration + unit |
| [TC-003](test-cases/TC-003-product-detail-view.md) | Product detail view: price breakdown, stock, delivery feasibility | Backend integration + unit |
| [TC-004](test-cases/TC-004-validation-and-not-found-edge-cases.md) | Validation errors and unpublished/not-found products | Backend integration |
| [TC-005](test-cases/TC-005-optional-auth-sponsored-pricing.md) | Optional-bearer auth: sponsored pricing shown only when authenticated | Backend integration |
| [TC-006](test-cases/TC-006-logistics-feasibility-degraded-mode.md) | Logistics feasibility client degraded-mode behavior | Backend unit |
| [TC-007](test-cases/TC-007-frontend-catalog-screens.md) | Frontend listing + detail page render and interaction behavior | Frontend component |

## Results

**All 69 tests passing** (38 backend, 31 frontend) as of this run. Coverage: backend 96%,
frontend 92.55% — both above the 80% exit-gate threshold. Summary: `coverage-report.html`
(per-line HTML reports are regenerable locally per that file's instructions — not committed
as they're generated artifacts).

## Known gaps (accepted, not silently dropped)

- The MySQL `FULLTEXT MATCH ... AGAINST` branch in `ProductRepository.search()` (ADR-0002) can
  only execute against a real MySQL 8.0+ database — SQLite (used for all local dev/test) has no
  FULLTEXT equivalent, so this branch is exercised by the LIKE-fallback path instead. Untested
  until a MySQL-backed test environment exists.
- `app/database.py`'s `get_db()` generator body — tests override this dependency with a per-test
  SQLite session, so the real generator only runs at app startup, which isn't exercised by
  unit/integration tests (same accepted gap as US-001).
- `app/logistics_client.py` line 35 (final `return "unknown"` fallback when the response body has
  neither `feasible: true` nor `feasible: false`) — a defensive branch for a malformed response
  shape from a Logistics service (US-013) that doesn't exist yet to actually return one.
- Real US-013 Logistics feasibility integration is stubbed/mocked throughout — no live Logistics
  service exists yet (Wave 3). All feasibility branches (feasible/not_feasible/unknown/timeout)
  are covered against a mocked `async_request` boundary, not a real service call.
- Browser-based E2E walkthroughs of the listing/detail screens are explicitly deferred to Step 7
  (`/end-to-end-testing-and-bug-resolution-for-this-story`) — this step covers component-level
  frontend tests only, not a real browser session.
