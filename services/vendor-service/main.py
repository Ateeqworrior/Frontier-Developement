from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ecom_core.utils.exception_handler import register_exception_handlers

from app.database import Base, engine
from app.models import (  # noqa: F401 (imports register the models with Base.metadata)
    OutboxEvent,
    VendorDocuments,
    VendorLegalCompliance,
    VendorOnboardingBasic,
    VendorOnboardingStatus,
    VendorOnboardingStatusHistory,
    VendorPaymentCompliance,
    VendorProductService,
    VendorProfileInclusion,
)
from app.router import router

app = FastAPI(title="MartSarathi Vendor Service", version="1.0.0")

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


@app.get("/health")
def health():
    return {"status": "ok", "service": "vendor-service"}
