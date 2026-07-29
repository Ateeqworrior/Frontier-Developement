from pydantic_settings import BaseSettings


class AuthCommonSettings(BaseSettings):
    """Shared JWT settings used by every service to verify tokens locally (no call to Auth Service)."""

    secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "auth-service"

    model_config = {"env_prefix": "ECOM_"}


auth_common_settings = AuthCommonSettings()
