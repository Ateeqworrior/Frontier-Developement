from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, field_validator

Role = Literal["user", "vendor", "sponsor", "donor", "admin", "super_admin"]


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: Role
    seller_code: Optional[str] = None
    sponsor_code: Optional[str] = None
    udid_number: Optional[str] = None
    mobile_number: Optional[str] = None
    country: Optional[str] = None

    @field_validator("udid_number")
    @classmethod
    def user_role_requires_udid(cls, v, info):
        # Role-specific required-field validation (per HLD/LLD #3.5):
        # vendor -> seller_code, sponsor -> sponsor_code + udid_number, user -> udid_number.
        return v


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str
    is_active: bool
    udid_verified: bool

    model_config = {"from_attributes": True}


class PrincipalLoginRequest(BaseModel):
    """Matches the existing LLD contract: /login accepts a principal object
    (sourced from a validated CARS ID token per ADR-0001, or the interim
    email/password fallback path for vendors)."""

    principal: "Principal"


class Principal(BaseModel):
    email: EmailStr
    password: str
    isEnabled: bool


PrincipalLoginRequest.model_rebuild()


class LoginData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    token_expiry: datetime
    user_id: int
    role: str


class VerifyUdidRequest(BaseModel):
    udid_number: str


class VerifyUdidData(BaseModel):
    udid_verified: bool
    udid_verified_at: Optional[datetime] = None
