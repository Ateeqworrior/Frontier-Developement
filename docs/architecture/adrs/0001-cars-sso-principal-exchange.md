# ADR-0001 — CARS SSO principal-exchange model for `/api/auth/login`

Status: Proposed

## Context

US-001 requires registration/login via Sarthak's CARS platform using OIDC (`docs/requirements/prd.md` §7). The existing Auth Service LLD (`.frontier/docs/architecture-documents/MartSarathi_HLD_LLD__1_.md` §3.4) already defines `POST /api/auth/login` as accepting a `principal` object (`{ email, password, isEnabled }`) and calling `AuthService.exchange_principal()` to mint MartSarathi's own internal JWT (HS256, claims: `sub`, `email`, `role`, `exp`, `iat`, `iss`).

This implies CARS's OIDC handshake happens *before* MartSarathi's backend is invoked — the frontend redirects to CARS, CARS authenticates the user, and something hands MartSarathi a "principal" to exchange for an internal session. The LLD does not specify **where** the OIDC authorization-code/token exchange with CARS happens (frontend-only via PKCE, or a thin backend callback that talks to CARS's token endpoint and derives the `principal`).

## Decision

Adopt a **backend-mediated exchange**: the React frontend redirects to CARS's OIDC `authorize` endpoint; CARS redirects back to a MartSarathi callback route with an authorization code; a backend callback handler (Auth Service) performs the code→token exchange directly with CARS, validates the CARS-issued ID token, derives the `principal` (`email`, `isEnabled` from CARS's `active`/`blocked` claim, plus role if CARS provides one), and only then calls the existing internal `exchange_principal()` path to mint MartSarathi's own JWT.

Rationale: keeps the CARS client secret server-side (never exposed to the SPA), and lets `exchange_principal()` remain the single choke point for issuing MartSarathi JWTs regardless of whether a user came through CARS SSO or (per the BRD's fallback risk mitigation) the interim email/password path for vendors.

## Consequences

- Auth Service gains a new `GET /api/auth/cars/callback` route (OIDC callback) in addition to the existing `/login` route — `/login` remains usable directly for the fallback path.
- Auth Service needs a CARS OIDC client registration (client ID/secret, redirect URI) as a new configuration dependency.
- No changes required to JWT claim shape or `auth_common` — downstream services are unaffected.

## Alternatives considered

- **Frontend-only OIDC (PKCE), backend never sees CARS tokens:** rejected — would require the SPA to independently derive a trustworthy `principal` and call `/login` directly, which conflicts with the LLD's existing `exchange_principal()` contract expecting a principal MartSarathi's backend already trusts, and pushes token validation logic into the browser.
- **Reuse `/login`'s existing `{email, password}` shape for CARS users too:** rejected — CARS-authenticated users should never hand MartSarathi a password; the `principal` object must be sourced from a validated CARS token, not user-entered credentials.

## Confirm before implementation

This ADR is `Proposed`, not `Accepted` — the source HLD/LLD does not explicitly describe the CARS callback mechanics. Confirm with the CARS/CARS-integration owner before Step 5 implementation begins.
