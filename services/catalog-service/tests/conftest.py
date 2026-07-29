import json
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
from app.models import Category, Product, ProductVariant
from main import app


@pytest.fixture()
def auth_token():
    """A validly-signed JWT for the "Optional Bearer" endpoints — mirrors the claim
    shape `ecom_core.auth_common.dependencies.get_current_user` expects."""
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
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test_catalog.db"
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
    category = Category(name="Mobility Aids", slug="mobility-aids")
    seed_db.add(category)
    seed_db.flush()

    published = Product(
        vendor_id=1,
        brand_id=1,
        title="Foldable Lightweight Wheelchair",
        description="Aluminium-frame foldable wheelchair.",
        tags="wheelchair,mobility",
        category_id=category.id,
        status="Published",
        sponsored="yes",
        avg_rating=4.5,
        rating_count=12,
        purchase_count=34,
    )
    draft = Product(
        vendor_id=1,
        brand_id=1,
        title="Unpublished Draft Product",
        description="Not yet published.",
        tags="draft",
        category_id=category.id,
        status="Draft",
    )
    seed_db.add_all([published, draft])
    seed_db.flush()

    seed_db.add_all(
        [
            ProductVariant(
                product_id=published.id,
                sku="WHC-001",
                price=8999.00,
                quantity=15,
                images=json.dumps(["https://example-cdn/wheelchair-1.jpg"]),
            ),
            ProductVariant(
                product_id=draft.id,
                sku="DRAFT-001",
                price=100.00,
                quantity=5,
                images=json.dumps([]),
            ),
        ]
    )
    seed_db.commit()
    seed_db.close()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
