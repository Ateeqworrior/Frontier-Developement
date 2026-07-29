import json
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy.orm import Session

from ecom_core.utils.errors import (
    AccountBlockedError,
    DuplicateResourceError,
    InvalidCredentialsError,
)

from .cars_client import verify_udid_with_sarthak_foundation
from .config import settings
from .models import OutboxEvent, User
from .repository import UserRepository
from .schemas import LoginData, Principal, RegisterRequest, VerifyUdidData


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def register_user(self, data: RegisterRequest) -> User:
        existing = self.repo.check_duplicates(
            email=data.email,
            mobile_number=data.mobile_number,
            seller_code=data.seller_code,
            sponsor_code=data.sponsor_code,
            udid_number=data.udid_number,
        )
        if existing:
            raise DuplicateResourceError("a user with these details already exists")

        role = self.repo.get_role_by_name(data.role)
        if role is None:
            raise DuplicateResourceError(f"role '{data.role}' does not exist", message_code="invalid_role")

        user = User(
            email=data.email,
            username=data.username,
            mobile_number=data.mobile_number,
            country=data.country,
            udid_number=data.udid_number,
            seller_code=data.seller_code,
            sponsor_code=data.sponsor_code,
            hashed_password=_hash_password(data.password),
            role_id=role.id,
            is_active=True,
        )
        self.repo.create_user(user)

        outbox = OutboxEvent(
            event_type="USER_CREATED",
            payload=json.dumps(
                {
                    "user_id": None,  # filled after flush below
                    "email": user.email,
                    "username": user.username,
                    "role_name": data.role,
                    "is_active": user.is_active,
                }
            ),
            status="PENDING",
        )
        self.db.add(outbox)
        self.db.commit()
        self.db.refresh(user)
        return user

    def exchange_principal(self, principal: Principal) -> LoginData:
        """Existing LLD contract (#3.4): validate principal, mint internal JWT.
        Extended by US-001 with an explicit blocked-account check."""
        user = self.repo.get_user_by_email(principal.email)
        if user is None or not _verify_password(principal.password, user.hashed_password):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise AccountBlockedError()

        return self._create_internal_jwt(user)

    def _create_internal_jwt(self, user: User) -> LoginData:
        now = datetime.now(timezone.utc)
        expiry = now + timedelta(minutes=settings.jwt_expiry_minutes)
        claims = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.name,
            "exp": int(expiry.timestamp()),
            "iat": int(now.timestamp()),
            "iss": settings.jwt_issuer,
        }
        token = jwt.encode(claims, settings.secret_key, algorithm=settings.jwt_algorithm)
        return LoginData(
            access_token=token,
            token_expiry=expiry,
            user_id=user.id,
            role=user.role.name,
        )

    async def verify_udid(self, user_id: int, udid_number: str) -> VerifyUdidData:
        """New for US-001: post-login UDID verification via the Sarthak Foundation endpoint."""
        user = self.repo.get_user_by_id(user_id)
        if user is None:
            raise InvalidCredentialsError("user not found")

        verified = await verify_udid_with_sarthak_foundation(udid_number)

        if verified:
            user.udid_number = udid_number
            user.udid_verified = True
            user.udid_verified_at = datetime.now(timezone.utc)
            self.db.add(
                OutboxEvent(
                    event_type="USER_UPDATED",
                    payload=json.dumps({"user_id": user.id, "udid_verified": True}),
                    status="PENDING",
                )
            )
            self.db.commit()
            self.db.refresh(user)

        return VerifyUdidData(udid_verified=user.udid_verified, udid_verified_at=user.udid_verified_at)
