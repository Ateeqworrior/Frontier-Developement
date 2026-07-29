# Design — Status Index

> Phase 3 of the Frontier Spec Generation SDLC lifecycle. Populated per-story as Step 3 ("Wireframe and Component Analysis") runs for each user story.

## UI/UX — Wireframe & Component Analysis

| Story | Screen/flow doc | Jira | Status | Design source |
|---|---|---|---|---|
| [US-001](../user-stories/stories/domain-registration-auth/US-001-sso-registration-login.md) | [wireframes/us-001-sso-registration-login.md](ui-ux/wireframes/us-001-sso-registration-login.md) · [user-flows/flow-sso-registration-login.md](ui-ux/user-flows/flow-sso-registration-login.md) | [CP-16](https://ateequrrahaman2004.atlassian.net/browse/CP-16) | Complete | No Figma file linked on CP-16 — analysis derived from Gherkin AC + task breakdown; see gap note in the wireframe doc |

## Services / API / Data design

| Story | Service | Docs | Status |
|---|---|---|---|
| [US-001](../user-stories/stories/domain-registration-auth/US-001-sso-registration-login.md) | auth-service | [design.md](services/auth-service/design.md) · [api-endpoints.md](services/auth-service/api-endpoints.md) · [data-model.md](services/auth-service/data-model.md) · [error-handling.md](services/auth-service/error-handling.md) | Complete |
| [US-003](../user-stories/stories/domain-product-discovery/US-003-product-discovery-search.md) | catalog-service | [design.md](services/catalog-service/design.md) · [api-endpoints.md](services/catalog-service/api-endpoints.md) · [data-model.md](services/catalog-service/data-model.md) · [error-handling.md](services/catalog-service/error-handling.md) | Complete — no wireframe doc yet (Step 3 has not run for this story) |
| [US-009](../user-stories/stories/domain-vendor-onboarding/US-009-vendor-onboarding-workflow.md) | vendor-service | [design.md](services/vendor-service/design.md) · [api-endpoints.md](services/vendor-service/api-endpoints.md) · [data-model.md](services/vendor-service/data-model.md) · [error-handling.md](services/vendor-service/error-handling.md) | Complete — no wireframe doc yet (Step 3 has not run for this story) |

Remaining stories populated as Step 4 runs for each.
