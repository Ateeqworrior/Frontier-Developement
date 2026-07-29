from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Cart Service config. DATABASE_URL defaults to local SQLite for dev/test;
    production points this at MySQL (sarthak_cart_service) via env var."""

    database_url: str = "sqlite:///./cart_service.db"

    catalog_service_url: str = "http://localhost:8002/api/catalog"
    wishlist_service_url: str = "http://localhost:8002/api/v1/wishlist"
    logistics_feasibility_url: str = "http://localhost:8007/api/logistics/feasibility"

    tax_rate_percent: float = 5.0
    delivery_flat_charge: float = 49.0
    free_delivery_threshold: float = 499.0

    model_config = {"env_prefix": "CART_SERVICE_"}


settings = Settings()
