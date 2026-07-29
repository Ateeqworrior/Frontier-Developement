import json
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session

from ecom_core.utils.errors import (
    CommentsRequiredError,
    InvalidDocumentFieldError,
    OnboardingIncompleteError,
    OnboardingLockedError,
    OnboardingValidationError,
    OnboardingVersionConflictError,
    RemarksRequiredError,
    VendorOnboardingNotFoundError,
)

from .form_definitions import FieldDef, TOTAL_STEPS, fields_for_step, is_document_field
from .models import OutboxEvent, VendorOnboardingStatus
from .repository import OnboardingRepository
from .s3_client import presign_upload

_LOCKED_STATUSES = {"Approved", "Rejected"}
_TYPE_CHECKS = {
    "string": lambda v: isinstance(v, str),
    "text": lambda v: isinstance(v, str),
    "document": lambda v: isinstance(v, str),
    "bool": lambda v: isinstance(v, bool),
    "int": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "float": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "json": lambda v: isinstance(v, (list, dict)),
}


def _validate_field(field: FieldDef, value: Any) -> None:
    if value is None:
        if field.required:
            raise OnboardingValidationError(f"'{field.name}' is required")
        return
    check = _TYPE_CHECKS[field.type]
    if not check(value):
        raise OnboardingValidationError(f"'{field.name}' must be of type {field.type}")


def _row_to_dict(row, fields: list[FieldDef]) -> dict[str, Any]:
    if row is None:
        return {f.name: None for f in fields}
    return {f.name: getattr(row, f.name) for f in fields}


class OnboardingService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = OnboardingRepository(db)

    # ---- Vendor-facing ----------------------------------------------------

    @staticmethod
    def get_form_meta(step: int) -> dict:
        return {
            "step": step,
            "fields": [{"name": f.name, "type": f.type, "required": f.required} for f in fields_for_step(step)],
        }

    def get_form(self, vendor_id: int, step: int) -> dict[str, Any]:
        row = self.repo.get_form_row(step, vendor_id)
        return _row_to_dict(row, fields_for_step(step))

    def save_form(self, vendor_id: int, step: int, data: dict[str, Any], if_match_version: int) -> tuple[dict, int]:
        status = self.repo.get_or_create_status(vendor_id)
        if status.admin_approval_status in _LOCKED_STATUSES:
            raise OnboardingLockedError()
        if status.version != if_match_version:
            raise OnboardingVersionConflictError()

        fields = fields_for_step(step)
        field_names = {f.name for f in fields}
        for key, value in data.items():
            if key not in field_names:
                raise OnboardingValidationError(f"unknown field '{key}' for step {step}")
        for field in fields:
            if field.name in data:
                _validate_field(field, data[field.name])

        self.repo.upsert_form(step, vendor_id, data)

        row_fields = _row_to_dict(self.repo.get_form_row(step, vendor_id), fields)
        is_step_complete = all(row_fields[f.name] is not None for f in fields if f.required)
        self.repo.upsert_form(step, vendor_id, {"is_completed": is_step_complete})

        updated = self.repo.conditional_update_status(
            vendor_id, if_match_version, current_step=max(status.current_step, step)
        )
        if updated is None:
            raise OnboardingVersionConflictError()
        self.db.commit()
        return _row_to_dict(self.repo.get_form_row(step, vendor_id), fields), updated.version

    def presign_document(self, vendor_id: int, step: int, document_field: str) -> dict:
        if not is_document_field(step, document_field):
            raise InvalidDocumentFieldError()
        return presign_upload(vendor_id, document_field)

    def _missing_mandatory(self, vendor_id: int) -> tuple[list[str], list[str]]:
        missing_fields: list[str] = []
        missing_documents: list[str] = []
        for step, fields in ((s, fields_for_step(s)) for s in range(1, TOTAL_STEPS + 1)):
            row_fields = self.get_form(vendor_id, step)
            for field in fields:
                if field.required and row_fields.get(field.name) is None:
                    target = missing_documents if field.type == "document" else missing_fields
                    target.append(f"step{step}.{field.name}")
        return missing_fields, missing_documents

    def submit(self, vendor_id: int, actor_id: int) -> VendorOnboardingStatus:
        status = self.repo.get_or_create_status(vendor_id)
        if status.admin_approval_status in _LOCKED_STATUSES:
            raise OnboardingLockedError()

        missing_fields, missing_documents = self._missing_mandatory(vendor_id)
        if missing_fields or missing_documents:
            detail_parts = []
            if missing_fields:
                detail_parts.append(f"missing required fields: {', '.join(missing_fields)}")
            if missing_documents:
                detail_parts.append(f"missing required documents: {', '.join(missing_documents)}")
            raise OnboardingIncompleteError("; ".join(detail_parts))

        from_status = status.admin_approval_status
        updated = self.repo.conditional_update_status(
            vendor_id, status.version, admin_approval_status="Submitted", is_completed=True
        )
        if updated is None:
            raise OnboardingVersionConflictError()
        self.repo.add_history(updated, from_status, "Submitted", "Vendor submitted onboarding for review", None, actor_id)
        self._emit_status_changed(vendor_id, from_status, "Submitted", None)
        self.db.commit()
        self.db.refresh(updated)
        return updated

    def get_or_create_own_status(self, vendor_id: int) -> VendorOnboardingStatus:
        """Vendor-facing status lookup — lazily initializes the record on first use
        so a vendor starting onboarding always has a version to key their first save on."""
        return self.repo.get_or_create_status(vendor_id)

    def get_status(self, vendor_id: int) -> VendorOnboardingStatus:
        """Admin-facing lookup for a *specific* vendor_id — 404s if that vendor has
        never started onboarding, since admins query existing records, not their own."""
        status = self.repo.get_status(vendor_id)
        if status is None:
            raise VendorOnboardingNotFoundError()
        return status

    # ---- Admin-facing -------------------------------------------------------

    def admin_list_queue(
        self,
        status_filter: Optional[str],
        date_from: Optional[str],
        date_to: Optional[str],
        category: Optional[str],
        page: int,
        page_size: int,
    ):
        rows, total = self.repo.list_queue(status_filter, date_from, date_to, category, page, page_size)
        entries = []
        for row in rows:
            basic = self.repo.get_form_row(1, row.vendor_id)
            product = self.repo.get_form_row(2, row.vendor_id)
            entries.append(
                {
                    "vendor_id": row.vendor_id,
                    "business_name": basic.business_name if basic else None,
                    "status": row.admin_approval_status,
                    "submitted_at": row.updated_at,
                    "category": product.product_category if product else None,
                }
            )
        return entries, total

    def admin_get_detail(self, vendor_id: int) -> dict:
        status = self.get_status(vendor_id)
        forms = {step: self.get_form(vendor_id, step) for step in range(1, TOTAL_STEPS + 1)}
        documents = {}
        for step, fields in ((s, fields_for_step(s)) for s in range(1, TOTAL_STEPS + 1)):
            row_fields = forms[step]
            for field in fields:
                if field.type == "document" and row_fields.get(field.name):
                    documents[field.name] = row_fields[field.name]
        return {"vendor_id": vendor_id, "status": status, "forms": forms, "documents": documents}

    def _admin_transition(
        self, vendor_id: int, actor_id: int, to_status: str, action: str, comment: Optional[str],
        expected_version: Optional[int],
    ) -> VendorOnboardingStatus:
        status = self.get_status(vendor_id)
        version = expected_version if expected_version is not None else status.version
        from_status = status.admin_approval_status
        updated = self.repo.conditional_update_status(
            vendor_id,
            version,
            admin_approval_status=to_status,
            admin_comment=comment,
            reviewed_by_admin_id=actor_id,
            reviewed_at=datetime.now(timezone.utc),
        )
        if updated is None:
            raise OnboardingVersionConflictError()
        self.repo.add_history(updated, from_status, to_status, action, comment, actor_id)
        self._emit_status_changed(vendor_id, from_status, to_status, comment)
        self.db.commit()
        self.db.refresh(updated)
        return updated

    def admin_approve(self, vendor_id: int, actor_id: int, expected_version: Optional[int]) -> VendorOnboardingStatus:
        return self._admin_transition(vendor_id, actor_id, "Approved", "Admin approved vendor onboarding", None, expected_version)

    def admin_reject(
        self, vendor_id: int, actor_id: int, remarks: str, expected_version: Optional[int]
    ) -> VendorOnboardingStatus:
        if not remarks or not remarks.strip():
            raise RemarksRequiredError()
        return self._admin_transition(vendor_id, actor_id, "Rejected", "Admin rejected vendor onboarding", remarks, expected_version)

    def admin_request_correction(
        self, vendor_id: int, actor_id: int, comments: dict[str, str], expected_version: Optional[int]
    ) -> VendorOnboardingStatus:
        if not comments:
            raise CommentsRequiredError()
        comment_text = json.dumps(comments)
        return self._admin_transition(
            vendor_id, actor_id, "Correction Required", "Admin requested correction", comment_text, expected_version
        )

    # ---- Outbox --------------------------------------------------------------

    def _emit_status_changed(self, vendor_id: int, from_status: Optional[str], to_status: str, comment: Optional[str]) -> None:
        self.db.add(
            OutboxEvent(
                event_type="VENDOR_ONBOARDING_STATUS_CHANGED",
                payload=json.dumps(
                    {
                        "vendor_id": vendor_id,
                        "from_status": from_status,
                        "to_status": to_status,
                        "comment": comment,
                        "changed_at": datetime.now(timezone.utc).isoformat(),
                    }
                ),
                status="PENDING",
            )
        )
