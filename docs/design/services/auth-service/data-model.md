# Auth Service — Data Model (US-001 contribution)

> Cross-cutting entity overview: [`docs/architecture/data-model.md`](../../../architecture/data-model.md). This file is the Auth Service team's owned detail.

## `users` table — additive columns (this story)

| Column | Type | Constraints | Description |
|---|---|---|---|
| `udid_verified` | BOOL | Default `False` | Set `True` once the Sarthak Foundation endpoint confirms `udid_number` |
| `udid_verified_at` | DATETIME(tz) | Nullable | Verification timestamp |

Existing columns reused (no change): `id`, `email`, `username`, `mobile_number`, `country`, `udid_number`, `seller_code`, `sponsor_code`, `gst_number`, `hashed_password`, `first_name`, `last_name`, `role_id` (FK → `roles.id`), `is_active` (reused as the block flag this story's login check reads), `is_verified`, `is_deleted`/`deleted_at` (SoftDeleteMixin), `created_at`/`updated_at`.

`roles`, `permissions`, `role_permissions` — unchanged.

## Migration note

Additive, nullable-safe migration: `ALTER TABLE users ADD COLUMN udid_verified BOOL NOT NULL DEFAULT FALSE, ADD COLUMN udid_verified_at DATETIME NULL;` — no backfill required (existing rows default to unverified, matching current real-world state since no verification endpoint existed before).
