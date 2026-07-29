# ADR-0003 — Optimistic locking for concurrent vendor onboarding saves

Status: Accepted

## Context

US-009's Gherkin AC and NFR-04 (`docs/requirements/requirements-summary.md`) require the vendor onboarding workflow to "support real-time validation errors and concurrent vendor submissions." The platform's existing HLD/LLD schema (`.frontier/docs/architecture-documents/MartSarathi_HLD_LLD__1_.md` §10.2–10.3) keys every onboarding form table and `vendor_onboarding_status` on a unique `vendor_id`, so two *different* vendors never contend for the same row — the database-per-vendor uniqueness constraint already isolates them. The real risk is a single vendor editing the same onboarding record from two sessions at once (e.g. two browser tabs, or a slow network retry racing a second save) and one save silently overwriting the other's fields, corrupting `is_completed`/`current_step` state or losing a just-uploaded document reference. Admin actions (approve/reject/correction) reading a `vendor_onboarding_status` row while the vendor concurrently edits it have the same lost-update risk.

## Decision

Add an integer `version` column to `vendor_onboarding_status` (start at `0`, incremented on every write). Every form-step save (`PUT /api/vendor/onboarding/forms/{step}`) and every admin status transition (`approve`/`reject`/`request-correction`) must pass the `version` it last read; the write is `UPDATE ... WHERE vendor_id = :vid AND version = :expected_version`. A zero-row update means the record changed since it was read — the API returns `409 Conflict` (`onboarding_version_conflict`) with the current server state, and the client must re-fetch and reapply before retrying. No database-level row locking (`SELECT ... FOR UPDATE`) is introduced — optimistic concurrency is sufficient because contention is expected to be rare (same vendor, near-simultaneous multi-tab edits) rather than routine.

## Consequences

- No new infrastructure — a single additive column and a `WHERE version =` clause on existing update statements, consistent with the platform's "no speculative or ad-hoc schema changes, all migrations via Alembic" rule.
- The frontend onboarding form must surface `409` as a "this form was updated elsewhere, reloading latest values" state rather than a generic error (NFR-04's "real-time validation errors" requirement).
- Does not protect against concurrent edits to the *same field* by *two different admins* reviewing in parallel — out of scope for this story; the single-admin-reviewer assumption in the Gherkin AC ("Admin reviews a submitted vendor") holds for Wave 1.
- Per-vendor uniqueness (`vendor_id` unique key) already means no cross-vendor row contention exists; this ADR only addresses same-vendor, multi-session races.

## Alternatives considered

- **Pessimistic row locking (`SELECT ... FOR UPDATE`):** rejected — holds a DB transaction/connection open for the duration of a user's form-editing session or admin review, which does not fit a stateless request/response API and risks connection-pool exhaustion under the concurrent-submission NFR this ADR is meant to satisfy.
- **Last-write-wins (no concurrency control):** rejected — directly violates NFR-03 ("data integrity must be maintained during edit and resubmit flows") and NFR-04.
- **Distributed lock (Redis/etc.):** rejected — introduces a new stateful infrastructure component not in the platform's approved stack (HLD/LLD §15, project context "Known Constraints"), disproportionate to a single-row, single-service concurrency problem.
