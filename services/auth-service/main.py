from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ecom_core.utils.exception_handler import register_exception_handlers

from app.database import Base, SessionLocal, engine
from app.models import Role  # noqa: F401 (import registers the model with Base.metadata)
from app.router import router

app = FastAPI(title="MartSarathi Auth Service", version="1.0.0")

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
    _seed_roles()


def _seed_roles() -> None:
    db = SessionLocal()
    try:
        existing = {r.name for r in db.query(Role).all()}
        for name in ("user", "vendor", "sponsor", "donor", "admin", "super_admin"):
            if name not in existing:
                db.add(Role(name=name, description=f"{name} role"))
        db.commit()
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok", "service": "auth-service"}
