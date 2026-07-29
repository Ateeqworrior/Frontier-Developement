import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ecom_core.utils.exception_handler import register_exception_handlers

from app.database import Base, SessionLocal, engine
from app.models import Category, Product, ProductVariant
from app.router import router

app = FastAPI(title="MartSarathi Catalog Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    _seed_demo_catalogue()


def _seed_demo_catalogue() -> None:
    """Dev-only sample data so US-003's listing/search/detail endpoints return real
    results without depending on US-011's (not-yet-built) vendor CRUD write path."""
    db = SessionLocal()
    try:
        if db.query(Category).count() > 0:
            return

        mobility = Category(name="Mobility Aids", slug="mobility-aids")
        db.add(mobility)
        db.flush()

        wheelchair = Product(
            vendor_id=1,
            brand_id=1,
            title="Foldable Lightweight Wheelchair",
            description="Aluminium-frame foldable wheelchair with padded armrests.",
            tags="wheelchair,mobility,foldable",
            category_id=mobility.id,
            status="Published",
            sponsored="yes",
            avg_rating=4.5,
            rating_count=12,
            purchase_count=34,
        )
        cane = Product(
            vendor_id=1,
            brand_id=2,
            title="Adjustable Walking Cane",
            description="Height-adjustable walking cane with ergonomic grip.",
            tags="cane,walking,mobility",
            category_id=mobility.id,
            status="Published",
            sponsored="no",
            avg_rating=4.1,
            rating_count=5,
            purchase_count=10,
        )
        db.add_all([wheelchair, cane])
        db.flush()

        db.add_all(
            [
                ProductVariant(
                    product_id=wheelchair.id,
                    sku="WHC-001",
                    price=8999.00,
                    quantity=15,
                    images=json.dumps(["https://example-cdn/wheelchair-1.jpg"]),
                ),
                ProductVariant(
                    product_id=cane.id,
                    sku="CANE-001",
                    price=699.00,
                    quantity=50,
                    images=json.dumps(["https://example-cdn/cane-1.jpg"]),
                ),
            ]
        )
        db.commit()
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok", "service": "catalog-service"}
