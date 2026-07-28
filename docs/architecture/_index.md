# Architecture — Status Index

## ADR registry

See [`adrs/_index.md`](adrs/_index.md).

## Architecture status per story

| Story | Jira | Status | Docs |
|---|---|---|---|
| [US-001](../user-stories/stories/domain-registration-auth/US-001-sso-registration-login.md) | [CP-16](https://ateequrrahaman2004.atlassian.net/browse/CP-16) | Complete | [system-design.md](system-design.md) · [data-model.md](data-model.md) · [ADR-0001](adrs/0001-cars-sso-principal-exchange.md) · [diagram (mermaid)](diagrams/c4-level-2-containers.md) · [diagram (drawio)](diagrams/us-001-sso-registration-login.drawio.xml) · [sequence](diagrams/sequence/seq-sso-login-udid-verification.md) |

## Diagram inventory

- `diagrams/c4-level-2-containers.md` — C4 L2 containers view (mermaid), US-001 slice.
- `diagrams/us-001-sso-registration-login.drawio.xml` — editable Draw.io diagram, same scope.
- `diagrams/sequence/seq-sso-login-udid-verification.md` — sequence diagrams for login, registration, and UDID verification flows.
