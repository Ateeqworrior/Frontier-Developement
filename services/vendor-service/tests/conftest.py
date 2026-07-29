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
from app.database import Base
from main import app


def _token(vendor_id: int, role: str) -> str:
    now = int(time.time())
    claims = {
        "sub": str(vendor_id),
        "email": f"{role}{vendor_id}@example.com",
        "role": role,
        "iat": now,
        "exp": now + 3600,
        "iss": auth_common_settings.jwt_issuer,
    }
    return jwt.encode(claims, auth_common_settings.secret_key, algorithm=auth_common_settings.jwt_algorithm)


@pytest.fixture()
def vendor_token():
    return _token(101, "vendor")


@pytest.fixture()
def other_vendor_token():
    return _token(202, "vendor")


@pytest.fixture()
def admin_token():
    return _token(1, "admin")


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test_vendor_service.db"
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
