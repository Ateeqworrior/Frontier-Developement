# Architecture Decision Records — Registry

| ID | Title | Status | Date | Decision summary |
|---|---|---|---|---|
| [ADR-0001](0001-cars-sso-principal-exchange.md) | CARS SSO principal-exchange model for `/api/auth/login` | Proposed | 2026-07-28 | Backend-mediated OIDC code exchange with CARS; frontend never handles CARS tokens directly. Motivated by US-001. |
| [ADR-0002](0002-mysql-fulltext-for-product-search.md) | MySQL FULLTEXT indexes for product keyword search | Accepted | 2026-07-29 | Use native MySQL 8.0+ FULLTEXT/relevance ranking instead of adding Elasticsearch. Motivated by US-003. |
| [ADR-0003](0003-optimistic-locking-vendor-onboarding-concurrency.md) | Optimistic locking for concurrent vendor onboarding saves | Accepted | 2026-07-29 | Additive `version` column + conditional update on `vendor_onboarding_status`; `409` on conflict instead of DB row locking. Motivated by US-009 (NFR-04). |
| [ADR-0004](0004-wishlist-ownership-cart-orchestration.md) | Wishlist stays owned by Catalog Service; Cart Service orchestrates move-to-cart | Accepted | 2026-07-29 | No wishlist schema migration; Cart Service calls Catalog Service's existing `/api/v1/wishlist/*` endpoints for the new move-to-cart action. Motivated by US-004. |
