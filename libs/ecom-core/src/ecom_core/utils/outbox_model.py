import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from ..auth_common.config import auth_common_settings  # noqa: F401  (keeps package import path warm)


class OutboxStatus(str, enum.Enum):
    PENDING = "PENDING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"


class OutboxEventMixin:
    """Transactional Outbox pattern base — one row per domain event, published by an OutboxWorker poller."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[OutboxStatus] = mapped_column(Enum(OutboxStatus), default=OutboxStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
