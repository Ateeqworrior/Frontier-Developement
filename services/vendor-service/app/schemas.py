from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class FieldMeta(BaseModel):
    name: str
    type: str
    required: bool


class FormMeta(BaseModel):
    step: int
    fields: list[FieldMeta]


class PresignRequest(BaseModel):
    document_field: str


class PresignResponse(BaseModel):
    upload_url: str
    s3_key: str
    expires_in: int


class OnboardingStatusHistoryEntry(BaseModel):
    from_status: Optional[str]
    to_status: str
    action: str
    comment: Optional[str]
    changed_by: int
    changed_at: datetime

    model_config = {"from_attributes": True}


class OnboardingStatusResponse(BaseModel):
    vendor_id: int
    current_step: int
    is_completed: bool
    status: str
    admin_comment: Optional[str]
    version: int
    history: list[OnboardingStatusHistoryEntry] = []

    model_config = {"from_attributes": True}


class VendorQueueEntry(BaseModel):
    vendor_id: int
    business_name: Optional[str]
    status: str
    submitted_at: Optional[datetime]
    category: Optional[str]


class RejectRequest(BaseModel):
    remarks: str
    version: Optional[int] = None


class RequestCorrectionRequest(BaseModel):
    comments: dict[str, str]
    version: Optional[int] = None


class ApproveRequest(BaseModel):
    version: Optional[int] = None


class FormDataResponse(BaseModel):
    step: int
    data: dict[str, Any]
