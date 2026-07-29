from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Vendor Service config. DATABASE_URL defaults to local SQLite for dev/test;
    production points this at MySQL (sarthak_vendor_service) via env var."""

    database_url: str = "sqlite:///./vendor_service.db"

    s3_presign_base_url: str = "https://vendor-documents.s3.amazonaws.com"
    s3_presign_expiry_seconds: int = 3600

    model_config = {"env_prefix": "VENDOR_SERVICE_"}


settings = Settings()
