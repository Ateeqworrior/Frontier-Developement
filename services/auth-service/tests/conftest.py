import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "libs" / "ecom-core" / "src"))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import database as database_module
from app.database import Base
from app.models import Role  # noqa: F401
from main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test_auth.db"
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
    seed_db = TestingSessionLocal()
    for name in ("user", "vendor", "sponsor", "donor", "admin", "super_admin"):
        seed_db.add(Role(name=name, description=f"{name} role"))
    seed_db.commit()
    seed_db.close()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
