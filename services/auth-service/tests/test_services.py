"""Direct AuthService unit tests for branches unreachable through the HTTP layer:
registration against a role name that doesn't exist in the DB (RegisterRequest's
Literal type only blocks unknown role *strings*, not roles absent from the roles
table), and UDID verification for a user id that no longer exists."""

import asyncio

import pytest

from app.schemas import RegisterRequest
from app.services import AuthService
from ecom_core.utils.errors import DuplicateResourceError, InvalidCredentialsError


def _db_session(client):
    from app import database as database_module

    return database_module.SessionLocal()


def test_register_user_with_role_missing_from_db_raises_duplicate_resource_error(client):
    db = _db_session(client)
    # "donor" passes RegisterRequest's Literal validation but was deliberately not
    # seeded in this test's DB to exercise AuthService's own role-existence guard.
    db.execute(__import__("sqlalchemy").text("DELETE FROM roles WHERE name = 'donor'"))
    db.commit()

    payload = RegisterRequest(
        email="norole@example.com",
        username="norole",
        password="S3cure!Pass",
        role="donor",
    )
    with pytest.raises(DuplicateResourceError) as exc_info:
        AuthService(db).register_user(payload)
    assert exc_info.value.message_code == "invalid_role"
    db.close()


def test_verify_udid_raises_invalid_credentials_for_unknown_user(client):
    db = _db_session(client)
    with pytest.raises(InvalidCredentialsError):
        asyncio.run(AuthService(db).verify_udid(user_id=999999, udid_number="SF-1"))
    db.close()
