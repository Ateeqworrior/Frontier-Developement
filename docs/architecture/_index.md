# Architecture — Status Index

## ADR registry

See [`adrs/_index.md`](adrs/_index.md).

## Architecture status per story

| Story | Jira | Status | Docs |
|---|---|---|---|
| [US-001](../user-stories/stories/domain-registration-auth/US-001-sso-registration-login.md) | [CP-16](https://ateequrrahaman2004.atlassian.net/browse/CP-16) | Complete | [system-design.md](system-design.md) · [data-model.md](data-model.md) · [ADR-0001](adrs/0001-cars-sso-principal-exchange.md) · [diagram (mermaid)](diagrams/c4-level-2-containers.md) · [diagram (drawio)](diagrams/us-001-sso-registration-login.drawio.xml) · [sequence](diagrams/sequence/seq-sso-login-udid-verification.md) |
| [US-003](../user-stories/stories/domain-product-discovery/US-003-product-discovery-search.md) | [CP-18](https://ateequrrahaman2004.atlassian.net/browse/CP-18) | Complete | [system-design.md](system-design.md#scope-for-us-003-jira-cp-18) · [data-model.md](data-model.md#us-003-additive-changes) · [ADR-0002](adrs/0002-mysql-fulltext-for-product-search.md) · [diagram (drawio)](diagrams/us-003-product-discovery-search.drawio.xml) · [service design](../design/services/catalog-service/design.md) |
| [US-009](../user-stories/stories/domain-vendor-onboarding/US-009-vendor-onboarding-workflow.md) | [CP-24](https://ateequrrahaman2004.atlassian.net/browse/CP-24) | Complete | [system-design.md](system-design.md#scope-for-us-009-jira-cp-24) · [data-model.md](data-model.md#us-009-additive-changes) · [ADR-0003](adrs/0003-optimistic-locking-vendor-onboarding-concurrency.md) · [diagram (drawio)](diagrams/us-009-vendor-onboarding-workflow.drawio.xml) · [service design](../design/services/vendor-service/design.md) |
| [US-004](../user-stories/stories/domain-cart-wishlist/US-004-cart-wishlist-management.md) | [CP-19](https://ateequrrahaman2004.atlassian.net/browse/CP-19) | Complete | [system-design.md](system-design.md#scope-for-us-004-jira-cp-19) · [data-model.md](data-model.md#us-004-additive-changes) · [ADR-0004](adrs/0004-wishlist-ownership-cart-orchestration.md) · [diagram (drawio)](diagrams/us-004-cart-wishlist-management.drawio.xml) · [service design](../design/services/cart-service/design.md) |

## Diagram inventory

- `diagrams/c4-level-2-containers.md` — C4 L2 containers view (mermaid), US-001 slice.
- `diagrams/us-001-sso-registration-login.drawio.xml` — editable Draw.io diagram, same scope.
- `diagrams/sequence/seq-sso-login-udid-verification.md` — sequence diagrams for login, registration, and UDID verification flows.
- `diagrams/us-003-product-discovery-search.drawio.xml` — editable Draw.io diagram, US-003 slice (listing/search/detail + Logistics/Review/Order event integration).
- `diagrams/us-009-vendor-onboarding-workflow.drawio.xml` — editable Draw.io diagram, US-009 slice (6-step onboarding, document presign, admin review actions, notify-vendor outbox flow).
- `diagrams/us-004-cart-wishlist-management.drawio.xml` — editable Draw.io diagram, US-004 slice (cart CRUD/totals, delivery feasibility, wishlist move-to-cart orchestration with Catalog Service).
