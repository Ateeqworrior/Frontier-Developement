from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Catalog Service config. DATABASE_URL defaults to local SQLite for dev/test;
    production points this at MySQL (sarthak_catalog_service) via env var."""

    database_url: str = "sqlite:///./catalog_service.db"

    logistics_feasibility_url: str = "http://localhost:8007/api/logistics/feasibility"

    tax_rate_percent: float = 5.0
    delivery_charge: float = 49.0
    sponsored_discount_percent: float = 10.0

    model_config = {"env_prefix": "CATALOG_SERVICE_"}


settings = Settings()
