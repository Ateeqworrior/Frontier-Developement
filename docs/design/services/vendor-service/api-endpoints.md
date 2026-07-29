# Vendor Service — API Endpoints (US-009 contribution)

> Machine-readable OpenAPI 3.1 fragment: [`specs/vendor-onboarding-workflow/api-schema.yaml`](../../../../specs/vendor-onboarding-workflow/api-schema.yaml).

## New endpoints (all new — first story for this service)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/vendor/onboarding/forms/{step}/meta` | Bearer (Vendor) | Field definitions, types, validation rules, file requirements for the given step (1–6) |
| GET | `/api/vendor/onboarding/forms/{step}` | Bearer (Vendor) | Current saved values for the given step (resume draft) |
| PUT | `/api/vendor/onboarding/forms/{step}` | Bearer (Vendor) | Save/update the given step (draft). Requires `If-Match: <version>`; `409` on stale write |
| POST | `/api/vendor/onboarding/documents/presign` | Bearer (Vendor) | Presigned S3 upload URL (1-hour expiry) for a named document field |
| POST | `/api/vendor/onboarding/submit` | Bearer (Vendor) | Submit for review — gated on all mandatory fields/documents across all 6 forms |
| GET | `/api/vendor/onboarding/status` | Bearer (Vendor) | Current status, admin remarks, and own resubmission history |
| GET | `/api/admin/vendor-onboarding` | Bearer (Admin) | Filterable review queue (`status`, `date_from`, `date_to`, `category`) |
| GET | `/api/admin/vendor-onboarding/{vendor_id}` | Bearer (Admin) | Full vendor profile, documents (presigned download URLs), and status history |
| POST | `/api/admin/vendor-onboarding/{vendor_id}/approve` | Bearer (Admin) | Approve — status → `Approved`, notifies vendor |
| POST | `/api/admin/vendor-onboarding/{vendor_id}/reject` | Bearer (Admin) | Reject — requires `remarks`, status → `Rejected`, notifies vendor, blocks vendor transactions |
| POST | `/api/admin/vendor-onboarding/{vendor_id}/request-correction` | Bearer (Admin) | Request correction — requires per-field/document `comments`, status → `Correction Required`, notifies vendor |

`Bearer (Vendor)`: scoped to the calling vendor's own `vendor_id` (from JWT claims) — a vendor cannot read or write another vendor's onboarding record (RBAC, `vendor_onboarding:write`/`vendor_onboarding:read`, own-scope only). `Bearer (Admin)`: requires `vendor_onboarding:review` permission.

## RBAC — new permissions

| Permission | Granted to | Scope |
|---|---|---|
| `vendor_onboarding:write` | Vendor | Own `vendor_id` only |
| `vendor_onboarding:read` | Vendor | Own `vendor_id` only |
| `vendor_onboarding:review` | Admin | All vendors |

Added to the existing role-permission matrix (`ecom_core.auth_common.constants.ROLE_PERMISSIONS`) — no new permission-checking mechanism, reuses `make_require_permission()`.

## Request/response reference

| Field | Notes |
|---|---|
| `step` (path) | Integer 1–6, maps to the six onboarding forms in HLD/LLD §10.2 order |
| `If-Match` header (form save) | The `version` value last read from `GET /forms/{step}` or `GET /status`; omitted/mismatched → `409` |
| `document_field` (presign request) | One of the `*_path` fields defined for the vendor's current step (e.g. `pan_proof_path`, `iso_ce_isi_certificate_path`) |
| `remarks` (reject) | Required, non-empty — mandatory-remarks enforcement (FR-09-09) |
| `comments` (request-correction) | Object keyed by field/document name → comment string |
