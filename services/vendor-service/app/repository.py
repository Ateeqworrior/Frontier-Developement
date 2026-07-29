from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from .models import (
    VendorDocuments,
    VendorLegalCompliance,
    VendorOnboardingBasic,
    VendorOnboardingStatus,
    VendorOnboardingStatusHistory,
    VendorPaymentCompliance,
    VendorProductService,
    VendorProfileInclusion,
)

STEP_MODELS = {
    1: VendorOnboardingBasic,
    2: VendorProductService,
    3: VendorProfileInclusion,
    4: VendorPaymentCompliance,
    5: VendorDocuments,
    6: VendorLegalCompliance,
}


class OnboardingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_status(self, vendor_id: int) -> Optional[VendorOnboardingStatus]:
        return self.db.get(VendorOnboardingStatus, vendor_id)

    def get_or_create_status(self, vendor_id: int) -> VendorOnboardingStatus:
        status = self.get_status(vendor_id)
        if status is None:
            status = VendorOnboardingStatus(vendor_id=vendor_id, current_step=1, is_completed=False,
                                             admin_approval_status="Draft", version=0)
            self.db.add(status)
            self.db.commit()
            self.db.refresh(status)
        return status

    def get_form_row(self, step: int, vendor_id: int):
        model = STEP_MODELS[step]
        return self.db.get(model, vendor_id)

    def get_all_form_rows(self, vendor_id: int) -> dict[int, object]:
        return {step: self.get_form_row(step, vendor_id) for step in STEP_MODELS}

    def upsert_form(self, step: int, vendor_id: int, data: dict):
        model = STEP_MODELS[step]
        row = self.db.get(model, vendor_id)
        if row is None:
            row = model(vendor_id=vendor_id)
            self.db.add(row)
        for key, value in data.items():
            setattr(row, key, value)
        self.db.flush()
        return row

    def conditional_update_status(self, vendor_id: int, expected_version: int, **fields) -> Optional[VendorOnboardingStatus]:
        """Optimistic-lock update (ADR-0003): returns None if `expected_version` is stale."""
        status = self.get_status(vendor_id)
        if status is None or status.version != expected_version:
            return None
        for key, value in fields.items():
            setattr(status, key, value)
        status.version += 1
        self.db.flush()
        return status

    def add_history(
        self,
        status: VendorOnboardingStatus,
        from_status: Optional[str],
        to_status: str,
        action: str,
        comment: Optional[str],
        changed_by: int,
    ) -> VendorOnboardingStatusHistory:
        entry = VendorOnboardingStatusHistory(
            vendor_onboarding_status_id=status.vendor_id,
            vendor_id=status.vendor_id,
            from_status=from_status,
            to_status=to_status,
            action=action,
            comment=comment,
            changed_by=changed_by,
            changed_at=datetime.now(timezone.utc),
        )
        self.db.add(entry)
        self.db.flush()
        return entry

    def list_queue(
        self,
        status_filter: Optional[str],
        date_from: Optional[str],
        date_to: Optional[str],
        category: Optional[str],
        page: int,
        page_size: int,
    ) -> tuple[list[VendorOnboardingStatus], int]:
        query = self.db.query(VendorOnboardingStatus).filter(VendorOnboardingStatus.is_completed.is_(True))
        if status_filter:
            query = query.filter(VendorOnboardingStatus.admin_approval_status == status_filter)
        if date_from:
            query = query.filter(VendorOnboardingStatus.updated_at >= date_from)
        if date_to:
            query = query.filter(VendorOnboardingStatus.updated_at <= date_to)
        if category:
            vendor_ids = [
                row.vendor_id
                for row in self.db.query(VendorProductService.vendor_id).filter(
                    VendorProductService.product_category == category
                )
            ]
            query = query.filter(VendorOnboardingStatus.vendor_id.in_(vendor_ids))

        total = query.count()
        rows = (
            query.order_by(VendorOnboardingStatus.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return rows, total
