# Vendor Service — Error Handling (US-009 contribution)

Uses the platform-wide `StandardResponse` envelope and global exception handler chain (`ecom_core.utils.exception_handler`) — no new handler types introduced. Error codes for this story (first for this service):

| Endpoint | Condition | HTTP Code | `message_code` |
|---|---|---|---|
| `PUT /api/vendor/onboarding/forms/{step}` | `If-Match` version does not match current `vendor_onboarding_status.version` | 409 | `onboarding_version_conflict` |
| `POST /api/admin/vendor-onboarding/{vendor_id}/approve` \| `/reject` \| `/request-correction` | Version conflict on the same row (concurrent admin/vendor write) | 409 | `onboarding_version_conflict` |
| `PUT /api/vendor/onboarding/forms/{step}` | Field fails validation rule for that step (real-time validation, NFR-04) | 422 | `field_validation_failed` (per-field error list in `error.detail`) |
| `POST /api/vendor/onboarding/submit` | One or more mandatory fields/documents missing across the 6 forms | 422 | `onboarding_incomplete` (per-field/document list in `error.detail`) |
| `POST /api/vendor/onboarding/documents/presign` | `document_field` not valid for the vendor's current step | 422 | `invalid_document_field` |
| `POST /api/admin/vendor-onboarding/{vendor_id}/reject` | Missing or empty `remarks` | 422 | `remarks_required` |
| `POST /api/admin/vendor-onboarding/{vendor_id}/request-correction` | Missing `comments` | 422 | `comments_required` |
| `GET /api/vendor/onboarding/forms/{step}` \| `PUT ...` | Vendor's onboarding record already `Approved`/`Rejected` (no further edits without an explicit correction/edit-request state) | 409 | `onboarding_locked` |
| `GET\|POST /api/admin/vendor-onboarding/{vendor_id}` | `vendor_id` has no onboarding record | 404 | `vendor_onboarding_not_found` |
| Any Vendor-scoped endpoint | JWT `vendor_id` claim does not match the resource being accessed | 403 | `forbidden_not_owner` |

No retry policy needed — all operations are synchronous single-service writes with no external dependency in the request path (S3 presigned upload happens client-side, after the presign call returns).
