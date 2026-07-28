import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel


class StandardResponse(BaseModel):
    """Unified API envelope used by every service (per HLD/LLD #2.3.4)."""

    success: bool
    timestamp: str
    trace_id: str
    api_version: str = "1.0"
    response_format_version: str = "2.0"
    message: str
    message_code: Optional[str] = None
    data: Optional[Any] = None
    error: Optional[dict] = None
    pagination: Optional[dict] = None

    @classmethod
    def ok(cls, message: str, data: Any = None, trace_id: Optional[str] = None) -> "StandardResponse":
        return cls(
            success=True,
            timestamp=datetime.now(timezone.utc).isoformat(),
            trace_id=trace_id or str(uuid.uuid4()),
            message=message,
            data=data,
        )

    @classmethod
    def fail(
        cls,
        message: str,
        message_code: str,
        detail: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> "StandardResponse":
        return cls(
            success=False,
            timestamp=datetime.now(timezone.utc).isoformat(),
            trace_id=trace_id or str(uuid.uuid4()),
            message=message,
            message_code=message_code,
            error={"code": message_code, "detail": detail or message},
        )
