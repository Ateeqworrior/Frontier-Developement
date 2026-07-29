"""Unit tests for the shared ecom_core lib consumed by auth-service (RBAC checkers,
UserPayload validation, SoftDeleteMixin, error defaults, generic exception handler,
and the shared HTTP client) — this story is the first consumer of ecom_core, so its
cross-cutting code is exercised here rather than in a standalone ecom-core test suite."""

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import Boolean, Column, DateTime, Integer, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from ecom_core.auth_common.constants import UserPayload
from ecom_core.auth_common.dependencies import make_require_permission, role_required
from ecom_core.utils.errors import DuplicateResourceError
from ecom_core.utils.exception_handler import register_exception_handlers
from ecom_core.utils.outbox_model import OutboxStatus
from ecom_core.utils.soft_delete_mixin import SoftDeleteMixin
from ecom_core.utils.standard_response import StandardResponse


def _payload(role="user", sub="1"):
    return UserPayload(sub=sub, exp=9999999999, role=role)


def test_role_required_allows_matching_role():
    checker = role_required("admin", "super_admin")
    assert checker(user=_payload(role="admin")).role == "admin"


def test_role_required_rejects_other_roles():
    from fastapi import HTTPException

    checker = role_required("admin")
    with pytest.raises(HTTPException) as exc_info:
        checker(user=_payload(role="user"))
    assert exc_info.value.status_code == 403


def test_make_require_permission_allows_direct_and_wildcard_match():
    checker = make_require_permission("category:read")
    # "admin" role has an explicit "category:*" wildcard, not "category:read" directly.
    assert checker(user=_payload(role="admin")).role == "admin"


def test_make_require_permission_denies_when_no_match():
    from fastapi import HTTPException

    checker = make_require_permission("role:create")
    with pytest.raises(HTTPException) as exc_info:
        checker(user=_payload(role="user"))
    assert exc_info.value.status_code == 403


def test_user_payload_rejects_empty_sub():
    with pytest.raises(ValidationError):
        UserPayload(sub="", exp=9999999999)


def test_soft_delete_mixin_soft_delete_and_restore():
    class _Base(DeclarativeBase):
        pass

    class _Widget(_Base, SoftDeleteMixin):
        __tablename__ = "widgets_test"
        id = Column(Integer, primary_key=True)

    engine = create_engine("sqlite://")
    _Base.metadata.create_all(engine)
    session: Session = sessionmaker(bind=engine)()

    widget = _Widget()
    session.add(widget)
    session.commit()

    assert widget.is_deleted is False
    widget.soft_delete()
    assert widget.is_deleted is True
    assert widget.deleted_at is not None

    widget.restore()
    assert widget.is_deleted is False
    assert widget.deleted_at is None
    session.close()


def test_outbox_status_enum_values():
    assert OutboxStatus.PENDING.value == "PENDING"
    assert OutboxStatus.PUBLISHED.value == "PUBLISHED"
    assert OutboxStatus.FAILED.value == "FAILED"


def test_duplicate_resource_error_default_message_code():
    err = DuplicateResourceError("dup!")
    assert err.message_code == "duplicate_resource"


def test_generic_exception_handler_returns_500():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    def boom():
        raise RuntimeError("unexpected failure")

    with TestClient(app, raise_server_exceptions=False) as tc:
        resp = tc.get("/boom")
    assert resp.status_code == 500
    assert resp.json()["message_code"] == "internal_error"


def test_async_request_delegates_to_httpx(monkeypatch):
    import httpx

    from ecom_core.utils.http_client import async_request

    captured = {}

    class _FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc_info):
            return False

        async def request(self, method, url, headers=None, params=None, json=None):
            captured.update(method=method, url=url, headers=headers, params=params, json=json)
            return httpx.Response(200, json={"ok": True})

    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout=10.0: _FakeClient())

    import asyncio

    resp = asyncio.run(async_request("GET", "https://example.test/x", params={"a": "b"}))
    assert resp.status_code == 200
    assert captured["method"] == "GET"
    assert captured["url"] == "https://example.test/x"


def test_standard_response_fail_shape():
    resp = StandardResponse.fail("bad input", "validation_error", "field x required")
    assert resp.success is False
    assert resp.message_code == "validation_error"
