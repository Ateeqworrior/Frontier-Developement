import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "libs" / "ecom-core" / "src"))

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ecom_core.auth_common.config import auth_common_settings

from app import database as database_module
from app import services as services_module
from app.database import Base
from main import app


@pytest.fixture()
def auth_token():
    """A validly-signed JWT for the "user" role — has `cart:*` and `wishlist:*`
    permissions per `ecom_core.auth_common.constants.ROLE_PERMISSIONS`."""
    now = int(time.time())
    claims = {
        "sub": "1",
        "email": "buyer@example.com",
        "role": "user",
        "iat": now,
        "exp": now + 3600,
        "iss": auth_common_settings.jwt_issuer,
    }
    return jwt.encode(claims, auth_common_settings.secret_key, algorithm=auth_common_settings.jwt_algorithm)


@pytest.fixture()
def other_user_token():
    now = int(time.time())
    claims = {
        "sub": "2",
        "email": "other-buyer@example.com",
        "role": "user",
        "iat": now,
        "exp": now + 3600,
        "iss": auth_common_settings.jwt_issuer,
    }
    return jwt.encode(claims, auth_common_settings.secret_key, algorithm=auth_common_settings.jwt_algorithm)


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test_cart.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    monkeypatch.setattr(database_module, "engine", engine)
    monkeypatch.setattr(database_module, "SessionLocal", TestingSessionLocal)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[database_module.get_db] = override_get_db
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def fake_prices(monkeypatch):
    """Stubs Catalog Service's batch-price dependency so cart totals tests don't
    need a real Catalog Service running. Returns the dict handed to callers so
    tests can mutate it (e.g. to simulate a product going missing/degraded)."""
    catalog = {
        1: {"id": 1, "title": "Wheelchair", "image_url": "https://cdn/wheelchair.jpg", "price": 8999.0},
        2: {"id": 2, "title": "Walking Cane", "image_url": None, "price": 699.0},
    }

    async def _fake_get_batch_prices(product_ids):
        return {pid: catalog[pid] for pid in product_ids if pid in catalog}

    monkeypatch.setattr(services_module.catalog_client, "get_batch_prices", _fake_get_batch_prices)
    return catalog


@pytest.fixture()
def fake_feasibility(monkeypatch):
    """Stubs the Logistics feasibility client; default always "feasible"."""

    async def _fake_check(pin_code):
        return "feasible"

    monkeypatch.setattr(services_module, "check_delivery_feasibility", _fake_check)


@pytest.fixture()
def fake_wishlist(monkeypatch):
    """Stubs Catalog Service's wishlist read/delete for move-to-cart tests."""
    state = {"items": {101: {"id": 101, "product_id": 1, "title": "Wheelchair", "image_url": None, "price": 8999.0}}}

    async def _fake_get_wishlist_item(wishlist_id, token):
        return state["items"].get(wishlist_id)

    async def _fake_delete_wishlist_item(wishlist_id, token):
        return state["items"].pop(wishlist_id, None) is not None

    monkeypatch.setattr(services_module.catalog_client, "get_wishlist_item", _fake_get_wishlist_item)
    monkeypatch.setattr(services_module.catalog_client, "delete_wishlist_item", _fake_delete_wishlist_item)
    return state
