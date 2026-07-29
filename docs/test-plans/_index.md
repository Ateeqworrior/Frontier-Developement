# Test Plans — Index

Mirrors `specs/` — one folder per feature.

| Feature | Story | Unit | Integration | E2E (Step 7) | Coverage | Status |
|---|---|---|---|---|---|---|
| [sso-registration-login](sso-registration-login/test-plan.md) | US-001 / CP-16 | ✅ 49 tests | ✅ (real SQLite via TestClient) | ✅ 14 live HTTP scenarios, 0 bugs (browser E2E blocked, see [e2e-test-report.html](sso-registration-login/e2e-test-report.html)) | Backend 97%, Frontend 88.3% | Steps 6 & 7 complete, Step 8 next |
| [product-discovery-search](product-discovery-search/test-plan.md) | US-003 / CP-18 | ✅ 69 tests | ✅ (real SQLite via TestClient) | ✅ 9 live HTTP + 6 live browser scenarios, 1 bug found & fixed (see [e2e-test-report.html](product-discovery-search/e2e-test-report.html)) | Backend 96%, Frontend 92.55% | Steps 6 & 7 complete, Step 8 next |

See [test-strategy.md](test-strategy.md) for tooling and approach shared across all features.
