# C4 Level 2 — Containers (US-001 slice)

> Editable version: [`us-001-sso-registration-login.drawio.xml`](us-001-sso-registration-login.drawio.xml) (Draw.io). This mermaid version is the git-diffable source of truth for review; keep both in sync.

```mermaid
flowchart TD
    subgraph Client["Client"]
        Browser["React 19 SPA<br/>(registration/login screens)"]
    end

    subgraph MartSarathi["MartSarathi Platform"]
        AuthSvc["Auth Service<br/>FastAPI :8001<br/>sarthak_auth_service DB"]
        OtherSvc["Cart / Order / Payment /<br/>Vendor / ... services"]
        Outbox["Outbox Worker"]
    end

    subgraph External["External Systems"]
        CARS["Sarthak CARS<br/>(OIDC Identity Provider)"]
        Sarthak["Sarthak Foundation<br/>UDID Verification API"]
    end

    Browser -- "1. Register/Login redirect" --> CARS
    CARS -- "2. Redirect back with principal" --> Browser
    Browser -- "3. POST /api/auth/login (principal)" --> AuthSvc
    AuthSvc -- "4. Mint internal JWT (HS256)" --> Browser
    Browser -- "5. Bearer JWT on all API calls" --> OtherSvc
    OtherSvc -- "verify locally via SECRET_KEY (auth_common)" --> OtherSvc
    Browser -- "6. POST /api/auth/verify-udid (Bearer)" --> AuthSvc
    AuthSvc -- "7. Verify UDID" --> Sarthak
    AuthSvc -- "8. USER_CREATED / USER_UPDATED events" --> Outbox
    Outbox -- "publish" --> OtherSvc
```
