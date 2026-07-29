from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ecom_core.auth_common.dependencies import get_current_user
from ecom_core.auth_common.constants import UserPayload
from ecom_core.utils.standard_response import StandardResponse

from .cars_client import build_cars_authorize_redirect_url, exchange_cars_code_for_principal
from .database import get_db
from .schemas import (
    LoginData,
    PrincipalLoginRequest,
    RegisterRequest,
    UserResponse,
    VerifyUdidData,
    VerifyUdidRequest,
)
from .services import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/cars/authorize")
def cars_authorize_redirect():
    """Frontend redirect target for Screens 1/2 (register/login) — returns the CARS authorize URL."""
    return StandardResponse.ok("redirect to CARS", data={"redirect_url": build_cars_authorize_redirect_url()})


@router.get("/cars/callback")
async def cars_callback(code: str, db: Session = Depends(get_db)):
    """New for US-001 (ADR-0001): exchange a CARS OIDC code for a principal, then log in via the
    existing exchange_principal() path."""
    principal = await exchange_cars_code_for_principal(code)
    data = AuthService(db).exchange_principal(principal)
    return StandardResponse.ok("Login successful", data=data.model_dump(mode="json"))


def _to_user_response(user) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        role=user.role.name,
        is_active=user.is_active,
        udid_verified=user.udid_verified,
    )


@router.post("/register", response_model=None)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = AuthService(db).register_user(payload)
    return StandardResponse.ok("Registration successful", data=_to_user_response(user).model_dump())


@router.post("/login", response_model=None)
def login(payload: PrincipalLoginRequest, db: Session = Depends(get_db)):
    """Existing endpoint (LLD #3.4). US-001 adds the 403 account_blocked branch inside exchange_principal()."""
    data: LoginData = AuthService(db).exchange_principal(payload.principal)
    return StandardResponse.ok("Login successful", data=data.model_dump(mode="json"))


@router.post("/verify-udid", response_model=None)
async def verify_udid(
    payload: VerifyUdidRequest,
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user),
):
    """New for US-001: Bearer-protected post-login UDID verification."""
    data: VerifyUdidData = await AuthService(db).verify_udid(current_user.id, payload.udid_number)
    return StandardResponse.ok(
        "UDID verified" if data.udid_verified else "UDID not verified",
        data=data.model_dump(mode="json"),
    )


@router.get("/me", response_model=None)
def me(
    db: Session = Depends(get_db),
    current_user: UserPayload = Depends(get_current_user),
):
    from .repository import UserRepository

    user = UserRepository(db).get_user_by_id(current_user.id)
    return StandardResponse.ok("Current user", data=_to_user_response(user).model_dump())
