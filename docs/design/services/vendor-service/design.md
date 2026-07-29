# Vendor Service — Design (US-009 contribution)

> Port 8008 · DB `sarthak_vendor_service` · Prefix `/api/vendor/` · Owns: `services/vendor-service/onboarding/` per [US-009](../../../user-stories/stories/domain-vendor-onboarding/US-009-vendor-onboarding-workflow.md). First story to stand up this service.

## Layer architecture (new service)

```
API Layer (router.py)        → /onboarding/forms/{step}, /onboarding/documents/presign, /onboarding/submit,
                                /onboarding/status, /admin/vendor-onboarding/*
Service Layer                → OnboardingFormService (draft save/resume, submission gating)
                                OnboardingReviewService (admin queue, approve/reject/correction)
Repository Layer             → OnboardingRepository (per-form upsert by vendor_id, optimistic-lock update)
MySQL (sarthak_vendor_service)
```

## New for US-009

1. **6-step form schema + metadata** — `GET /api/vendor/onboarding/forms/{step}/meta` returns field definitions, types, validation rules, and file requirements for the given step (HLD/LLD §6.3.8 "Metadata APIs"), backing the six existing tables (`vendor_onboarding_basic` … `vendor_legal_compliance`, HLD/LLD §10.2).
2. **Draft save/resume** — `PUT /api/vendor/onboarding/forms/{step}` upserts the vendor's row for that step (unique on `vendor_id`) and updates `vendor_onboarding_status.current_step`/`is_completed`. Server-side validation runs per-field on every save (real-time errors, NFR-04) independent of submission gating.
3. **Document upload** — `POST /api/vendor/onboarding/documents/presign` returns a presigned S3 PUT URL via the existing `S3Service.generate_upload_url()`-equivalent (1-hour expiry, no public access, NFR-02). The client uploads directly to S3, then references the returned key in the relevant form's `*_path` field.
4. **Submission gating** — `POST /api/vendor/onboarding/submit`: `OnboardingFormService.validate_submission()` checks every mandatory field/document across all six forms is present; on success transitions `vendor_onboarding_status.admin_approval_status` `PENDING → Submitted`-equivalent (HLD/LLD state machine, §10.3) and writes a `vendor_onboarding_status_history` row. On failure, returns `422` with per-field/document error codes — no partial submission.
5. **Admin review queue** — `GET /api/admin/vendor-onboarding` (filters: `status`, `date_from`/`date_to`, `product_category` from `vendor_product_service.product_category`) + `GET /api/admin/vendor-onboarding/{vendor_id}` (full profile, documents via presigned download URLs, resubmission history from `vendor_onboarding_status_history`).
6. **Admin actions** — `POST .../approve` (status → `APPROVED`), `POST .../reject` (mandatory `remarks`, status → `REJECTED`, blocks all vendor transactions — enforced by other services checking `admin_approval_status` via the synced `user_local`/status lookup), `POST .../request-correction` (per-field/document `comments`, status → `CORRECTION_REQUESTED`, unlocks only the flagged fields for vendor edit). Each action appends to `vendor_onboarding_status_history` and emits `VENDOR_ONBOARDING_STATUS_CHANGED`.
7. **Concurrency control** — every write to `vendor_onboarding_status` (form save's status-row update, and all three admin actions) is a conditional `UPDATE ... WHERE vendor_id = :vid AND version = :expected_version`; a zero-row result returns `409 onboarding_version_conflict`. See [ADR-0003](../../../architecture/adrs/0003-optimistic-locking-vendor-onboarding-concurrency.md).
8. **Audit trail** — `vendor_onboarding_status_history` is append-only (no update/delete path exposed), soft-delete-compliant by construction (nothing to soft-delete on an immutable log).

## Reused as-is (no changes)

- All six onboarding form table schemas, `vendor_onboarding_status`, `vendor_onboarding_status_history` structure, and the onboarding status state machine — HLD/LLD §10.2–10.3, built fresh for this story but with no deviation from the documented design.
- `StandardResponse` envelope, global exception handler chain, `S3Service` for document storage, `auth_common` RBAC/JWT verification, Transactional Outbox pattern for `VENDOR_ONBOARDING_STATUS_CHANGED`.
- `user_local` sync from Auth Service `USER_CREATED`/`USER_UPDATED` events (Strategy 1, HLD/LLD §8.3) — same pattern every other consuming service already uses.

## Persona/integration mapping

| Persona | Touchpoint |
|---|---|
| Vendor | Fill/save/resume 6-step form, upload documents, submit, view status + admin remarks, edit-and-resubmit on correction |
| Admin | Filterable review queue, full profile/document view, approve/reject/request-correction with audit trail |
| Auth Service | Source of `USER_CREATED`/`USER_UPDATED` events synced into `user_local` |
| Notification Service ([US-008](../../../user-stories/stories/domain-notifications-support/US-008-notifications-and-support.md)) | Consumes `VENDOR_ONBOARDING_STATUS_CHANGED` to notify the vendor |
| Vendor Contract ([US-010](../../../user-stories/stories/domain-vendor-contract/US-010-vendor-contract-signoff.md)) | Reads `admin_approval_status == APPROVED` as the gate before contract sign-off begins (not built by this story) |
