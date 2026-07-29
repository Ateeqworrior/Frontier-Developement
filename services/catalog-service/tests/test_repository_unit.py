"""Unit tests for ProductRepository — isolated from the HTTP layer, exercised
against a real (ephemeral, file-backed) SQLite session per the project's
test-strategy.md (no ORM/DB mocking)."""

import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Category, Product, ProductVariant
from app.repository import ProductRepository


@pytest.fixture()
def db_session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'repo_unit.db'}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    category = Category(name="Mobility Aids", slug="mobility-aids")
    session.add(category)
    session.flush()

    cheap = Product(
        vendor_id=1,
        brand_id=10,
        title="Cheap Cane",
        description="An affordable cane.",
        tags="cane",
        category_id=category.id,
        status="Published",
        avg_rating=3.0,
        purchase_count=1,
    )
    pricey = Product(
        vendor_id=1,
        brand_id=20,
        title="Premium Wheelchair",
        description="A premium wheelchair.",
        tags="wheelchair",
        category_id=category.id,
        status="Published",
        avg_rating=4.8,
        purchase_count=99,
    )
    unpublished = Product(
        vendor_id=1,
        brand_id=10,
        title="Draft Product",
        description="not yet live",
        tags="draft",
        category_id=category.id,
        status="Draft",
    )
    session.add_all([cheap, pricey, unpublished])
    session.flush()

    session.add_all(
        [
            ProductVariant(product_id=cheap.id, sku="CANE-1", price=100.0, quantity=5, images=json.dumps([])),
            ProductVariant(product_id=pricey.id, sku="WHC-1", price=9000.0, quantity=2, images=json.dumps([])),
            ProductVariant(product_id=unpublished.id, sku="DRAFT-1", price=50.0, quantity=1, images=json.dumps([])),
        ]
    )
    session.commit()

    yield session
    session.close()


def test_list_products_filters_by_brand(db_session):
    repo = ProductRepository(db_session)
    rows, total = repo.list_products(brand_id=20, sort="recency", page=1, page_size=20)
    assert total == 1
    assert rows[0][0].title == "Premium Wheelchair"


def test_list_products_filters_by_min_rating(db_session):
    repo = ProductRepository(db_session)
    rows, total = repo.list_products(min_rating=4.0, sort="recency", page=1, page_size=20)
    assert total == 1
    assert rows[0][0].title == "Premium Wheelchair"


def test_list_products_filters_by_price_max(db_session):
    repo = ProductRepository(db_session)
    rows, total = repo.list_products(price_max=500, sort="recency", page=1, page_size=20)
    assert total == 1
    assert rows[0][0].title == "Cheap Cane"


def test_list_products_sort_price_desc(db_session):
    repo = ProductRepository(db_session)
    rows, _ = repo.list_products(sort="price_desc", page=1, page_size=20)
    assert [r[0].title for r in rows] == ["Premium Wheelchair", "Cheap Cane"]


def test_list_products_sort_popularity(db_session):
    repo = ProductRepository(db_session)
    rows, _ = repo.list_products(sort="popularity", page=1, page_size=20)
    assert [r[0].title for r in rows] == ["Premium Wheelchair", "Cheap Cane"]


def test_list_products_excludes_unpublished(db_session):
    repo = ProductRepository(db_session)
    _, total = repo.list_products(page=1, page_size=20)
    assert total == 2  # Draft Product excluded


def test_search_matches_description_and_respects_filters(db_session):
    repo = ProductRepository(db_session)
    rows, total = repo.search("premium", brand_id=20, page=1, page_size=20)
    assert total == 1
    assert rows[0][0].title == "Premium Wheelchair"


def test_search_with_no_match_returns_empty(db_session):
    repo = ProductRepository(db_session)
    rows, total = repo.search("nonexistent-keyword-xyz", page=1, page_size=20)
    assert rows == []
    assert total == 0


def test_get_by_id_returns_none_for_unpublished(db_session):
    repo = ProductRepository(db_session)
    unpublished = db_session.query(Product).filter(Product.title == "Draft Product").first()
    assert repo.get_by_id(unpublished.id) is None


def test_pagination_limits_page_size(db_session):
    repo = ProductRepository(db_session)
    rows, total = repo.list_products(page=1, page_size=1)
    assert len(rows) == 1
    assert total == 2
