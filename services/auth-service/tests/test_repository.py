"""Direct UserRepository unit tests covering duplicate-detection branches
(mobile_number/seller_code/sponsor_code) that the HTTP-level tests don't exercise
since RegisterRequest's default registration path only sets email/udid_number."""

from app.models import Role, User
from app.repository import UserRepository


def _seed_role(db, name="user"):
    # `client` fixture already seeds the standard roles; reuse rather than re-insert
    # to avoid a UNIQUE constraint violation on roles.name.
    role = db.query(Role).filter(Role.name == name).first()
    if role is None:
        role = Role(name=name, description=f"{name} role")
        db.add(role)
        db.commit()
        db.refresh(role)
    return role


def _make_user(db, role, **overrides):
    defaults = dict(
        email="base@example.com",
        username="baseuser",
        hashed_password="x",
        role_id=role.id,
        is_active=True,
    )
    defaults.update(overrides)
    user = User(**defaults)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _db_session(client):
    from app import database as database_module

    return database_module.SessionLocal()


def test_check_duplicates_matches_on_mobile_number(client):
    db = _db_session(client)
    role = _seed_role(db)
    _make_user(db, role, email="a@example.com", username="usera", mobile_number="9999999999")

    repo = UserRepository(db)
    found = repo.check_duplicates(email="different@example.com", mobile_number="9999999999")
    assert found is not None
    db.close()


def test_check_duplicates_matches_on_seller_code(client):
    db = _db_session(client)
    role = _seed_role(db)
    _make_user(db, role, email="b@example.com", username="userb", seller_code="SELLER-1")

    repo = UserRepository(db)
    found = repo.check_duplicates(email="different2@example.com", seller_code="SELLER-1")
    assert found is not None
    db.close()


def test_check_duplicates_matches_on_sponsor_code(client):
    db = _db_session(client)
    role = _seed_role(db)
    _make_user(db, role, email="c@example.com", username="userc", sponsor_code="SPONSOR-1")

    repo = UserRepository(db)
    found = repo.check_duplicates(email="different3@example.com", sponsor_code="SPONSOR-1")
    assert found is not None
    db.close()


def test_check_duplicates_returns_none_when_no_match(client):
    db = _db_session(client)
    _seed_role(db)

    repo = UserRepository(db)
    found = repo.check_duplicates(email="nobody@example.com")
    assert found is None
    db.close()
