import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from .config import auth_common_settings
from .constants import UserPayload
from .security import bearer_scheme


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> UserPayload:
    """Verify a JWT locally against the shared SECRET_KEY — no call back to Auth Service."""
    token = credentials.credentials
    try:
        claims = jwt.decode(
            token,
            auth_common_settings.secret_key,
            algorithms=[auth_common_settings.jwt_algorithm],
            issuer=auth_common_settings.jwt_issuer,
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or expired token",
        ) from exc
    return UserPayload(**claims)


def role_required(*allowed_roles: str):
    def _checker(user: UserPayload = Depends(get_current_user)) -> UserPayload:
        if user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="role not permitted")
        return user

    return _checker


def make_require_permission(permission_code: str):
    """Factory used as `Depends(make_require_permission("user:read"))` in service routers."""

    def _checker(user: UserPayload = Depends(get_current_user)) -> UserPayload:
        if not user.has_permission(permission_code):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission denied")
        return user

    return _checker
