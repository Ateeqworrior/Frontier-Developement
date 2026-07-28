from typing import Optional

from pydantic import BaseModel, field_validator

# Role -> permission-code matrix. Runtime source of truth for RBAC across all services
# (per .frontier/docs/architecture-documents/MartSarathi_HLD_LLD__1_.md #2.3.2).
ROLE_PERMISSIONS: dict[str, set[str]] = {
    "super_admin": {
        "user:create_admin", "user:delete", "role:create", "role:delete",
        "payment:refund", "sponsorship:manage", "category:*", "attribute:*", "platform:*",
    },
    "admin": {
        "user:read", "user:create", "user:update", "user:delete",
        "product:approval", "vendor:manage", "vendor:aggrement", "ad:manage",
        "category:*", "attribute:*", "platform:*",
    },
    "vendor": {
        "product:vendor_read", "product:create", "product:update_by_vendor",
        "product:submit_for_review", "vendor:onboard", "vendor:aggrement", "category:read",
    },
    "sponsor": {
        "product:read", "order:create", "cart:*", "payment:*",
        "sponsorship:read", "sponsorship:create",
    },
    "user": {
        "product:read", "order:read", "order:create", "cart:*",
        "payment:read", "payment:process",
    },
}


class UserPayload(BaseModel):
    """JWT token model — mirrors the shared claim shape every service verifies locally."""

    sub: str
    exp: int
    email: Optional[str] = None
    username: Optional[str] = None
    iat: Optional[int] = None
    type: Optional[str] = None
    role: Optional[str] = None
    iss: Optional[str] = None

    @field_validator("sub")
    @classmethod
    def sub_not_empty(cls, v: str) -> str:
        if not v:
            raise ValueError("sub must not be empty")
        return v

    @property
    def id(self) -> int:
        return int(self.sub)

    def has_permission(self, permission_code: str) -> bool:
        role_perms = ROLE_PERMISSIONS.get(self.role or "", set())
        if permission_code in role_perms:
            return True
        namespace = permission_code.split(":")[0] + ":*"
        return namespace in role_perms
