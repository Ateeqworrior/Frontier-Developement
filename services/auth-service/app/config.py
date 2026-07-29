from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Auth Service config. DATABASE_URL defaults to local SQLite for dev/test;
    production points this at MySQL (sarthak_auth_service) via env var."""

    database_url: str = "sqlite:///./auth_service.db"
    secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "auth-service"
    jwt_expiry_minutes: int = 60

    cars_authorize_url: str = "https://cars.sarthak.example/oauth/authorize"
    cars_token_url: str = "https://cars.sarthak.example/oauth/token"
    cars_client_id: str = "martsarathi-dev"
    cars_client_secret: str = "dev-client-secret"
    cars_redirect_uri: str = "http://localhost:8001/api/auth/cars/callback"

    sarthak_udid_verify_url: str = "https://udid.sarthakfoundation.example/api/verify"

    model_config = {"env_prefix": "AUTH_SERVICE_"}


settings = Settings()
