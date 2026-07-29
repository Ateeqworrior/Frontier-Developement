from typing import Optional

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from ecom_core.auth_common.constants import UserPayload
from ecom_core.auth_common.dependencies import make_require_permission
from ecom_core.utils.errors import OnboardingVersionConflictError
from ecom_core.utils.standard_response import StandardResponse

from .database import get_db
from .form_definitions import TOTAL_STEPS
from .schemas import ApproveRequest, PresignRequest, RejectRequest, RequestCorrectionRequest
from .services import OnboardingService

router = APIRouter(tags=["vendor-onboarding"])

_require_write = make_require_permission("vendor_onboarding:write")
_require_read = make_require_permission("vendor_onboarding:read")
_require_review = make_require_permission("vendor_onboarding:review")


def _status_to_dict(status) -> dict:
    return {
        "vendor_id": status.vendor_id,
        "current_step": status.current_step,
        "is_completed": status.is_completed,
        "status": status.admin_approval_status,
        "admin_comment": status.admin_comment,
        "version": status.version,
        "history": [
            {
                "from_status": h.from_status,
                "to_status": h.to_status,
                "action": h.action,
                "comment": h.comment,
                "changed_by": h.changed_by,
                "changed_at": h.changed_at.isoformat(),
            }
            for h in status.history
        ],
    }


@router.get("/api/vendor/onboarding/forms/{step}/meta", response_model=None)
def get_form_meta(step: int, current_user: UserPayload = Depends(_require_read)):
    return StandardResponse.ok("form metadata", data=OnboardingService.get_form_meta(step)).model_dump(mode="json")


@router.get("/api/vendor/onboarding/forms/{step}", response_model=None)
def get_form(step: int, db: Session = Depends(get_db), current_user: UserPayload = Depends(_require_read)):
    data = OnboardingService(db).get_form(current_user.id, step)
    return StandardResponse.ok("form data", data=data).model_dump(mode="json")


@router.put("/api/vendor/onboarding/forms/{step}", response_model=None)
def save_form(
    step: int,
    payload: dict,
    if_match: int = Header(..., alias="If-Match"),
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(_require_write),
):
    data, version = OnboardingService(db).save_form(current_user.id, step, payload, if_match)
    response = StandardResponse.ok("form saved", data=data)
    response.data = {**data, "version": version}
    return response.model_dump(mode="json")


@router.post("/api/vendor/onboarding/documents/presign", response_model=None)
def presign_document(
    payload: PresignRequest,
    step: int = Query(..., ge=1, le=TOTAL_STEPS),
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(_require_write),
):
    data = OnboardingService(db).presign_document(current_user.id, step, payload.document_field)
    return StandardResponse.ok("presigned upload URL", data=data).model_dump(mode="json")


@router.post("/api/vendor/onboarding/submit", response_model=None)
def submit(db: Session = Depends(get_db), current_user: UserPayload = Depends(_require_write)):
    status = OnboardingService(db).submit(current_user.id, current_user.id)
    return StandardResponse.ok("onboarding submitted", data=_status_to_dict(status)).model_dump(mode="json")


@router.get("/api/vendor/onboarding/status", response_model=None)
def get_status(db: Session = Depends(get_db), current_user: UserPayload = Depends(_require_read)):
    status = OnboardingService(db).get_or_create_own_status(current_user.id)
    return StandardResponse.ok("onboarding status", data=_status_to_dict(status)).model_dump(mode="json")


@router.get("/api/admin/vendor-onboarding", response_model=None)
def list_queue(
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    category: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(_require_review),
):
    entries, total = OnboardingService(db).admin_list_queue(status, date_from, date_to, category, page, page_size)
    response = StandardResponse.ok("vendor onboarding queue", data=entries)
    response.pagination = {"page": page, "page_size": page_size, "total": total}
    return response.model_dump(mode="json")


@router.get("/api/admin/vendor-onboarding/{vendor_id}", response_model=None)
def get_detail(vendor_id: int, db: Session = Depends(get_db), current_user: UserPayload = Depends(_require_review)):
    detail = OnboardingService(db).admin_get_detail(vendor_id)
    return StandardResponse.ok(
        "vendor onboarding detail",
        data={
            "vendor_id": detail["vendor_id"],
            "status": _status_to_dict(detail["status"]),
            "forms": detail["forms"],
            "documents": detail["documents"],
        },
    ).model_dump(mode="json")


@router.post("/api/admin/vendor-onboarding/{vendor_id}/approve", response_model=None)
def approve(
    vendor_id: int,
    payload: ApproveRequest = ApproveRequest(),
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(_require_review),
):
    status = OnboardingService(db).admin_approve(vendor_id, current_user.id, payload.version)
    return StandardResponse.ok("vendor approved", data=_status_to_dict(status)).model_dump(mode="json")


@router.post("/api/admin/vendor-onboarding/{vendor_id}/reject", response_model=None)
def reject(
    vendor_id: int,
    payload: RejectRequest,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(_require_review),
):
    status = OnboardingService(db).admin_reject(vendor_id, current_user.id, payload.remarks, payload.version)
    return StandardResponse.ok("vendor rejected", data=_status_to_dict(status)).model_dump(mode="json")


@router.post("/api/admin/vendor-onboarding/{vendor_id}/request-correction", response_model=None)
def request_correction(
    vendor_id: int,
    payload: RequestCorrectionRequest,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(_require_review),
):
    status = OnboardingService(db).admin_request_correction(vendor_id, current_user.id, payload.comments, payload.version)
    return StandardResponse.ok("correction requested", data=_status_to_dict(status)).model_dump(mode="json")
