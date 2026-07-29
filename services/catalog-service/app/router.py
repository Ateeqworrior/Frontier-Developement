from typing import Optional

import jwt
from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ecom_core.auth_common.config import auth_common_settings
from ecom_core.auth_common.constants import UserPayload
from ecom_core.auth_common.dependencies import make_require_permission
from ecom_core.utils.standard_response import StandardResponse

from .database import get_db
from .schemas import SortOption, WishlistItemCreate
from .services import ProductDiscoveryService, WishlistService

router = APIRouter(prefix="/api/catalog", tags=["catalog"])
wishlist_router = APIRouter(prefix="/api/v1/wishlist", tags=["wishlist"])

# Optional-bearer variant of ecom_core's bearer_scheme (auto_error=True there): these endpoints
# are public reads that only need to know IF a caller is authenticated, to personalize sponsored
# pricing (docs/design/services/catalog-service/api-endpoints.md).
_optional_bearer = HTTPBearer(auto_error=False)


def _is_authenticated(credentials: Optional[HTTPAuthorizationCredentials] = Depends(_optional_bearer)) -> bool:
    if credentials is None:
        return False
    try:
        jwt.decode(
            credentials.credentials,
            auth_common_settings.secret_key,
            algorithms=[auth_common_settings.jwt_algorithm],
            issuer=auth_common_settings.jwt_issuer,
        )
        return True
    except jwt.PyJWTError:
        return False


@router.get("/products", response_model=None)
def list_products(
    category_id: Optional[int] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    brand_id: Optional[int] = None,
    min_rating: Optional[float] = Query(default=None, ge=0, le=5),
    sort: SortOption = "recency",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = ProductDiscoveryService(db).list_products(
        category_id, price_min, price_max, brand_id, min_rating, sort, page, page_size
    )
    response = StandardResponse.ok("products", data=[item.model_dump() for item in items])
    response.pagination = {"page": page, "page_size": page_size, "total": total}
    return response.model_dump(mode="json")


@router.get("/products/search", response_model=None)
def search_products(
    q: str,
    category_id: Optional[int] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    brand_id: Optional[int] = None,
    min_rating: Optional[float] = Query(default=None, ge=0, le=5),
    sort: Optional[SortOption] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = ProductDiscoveryService(db).search_products(
        q, category_id, price_min, price_max, brand_id, min_rating, sort, page, page_size
    )
    response = StandardResponse.ok("search results", data=[item.model_dump() for item in items])
    response.pagination = {"page": page, "page_size": page_size, "total": total}
    return response.model_dump(mode="json")


@router.get("/products/prices", response_model=None)
def get_product_prices(ids: str, db: Session = Depends(get_db)):
    """Batch price/title/image lookup — new dependency for US-004 (Cart Service)
    cart-total enrichment (docs/design/services/cart-service/design.md).
    Registered ABOVE `/products/{product_id}` — otherwise Starlette would match
    "prices" against the `product_id: int` path converter first and 422 instead
    of reaching this route."""
    product_ids = [int(part) for part in ids.split(",") if part.strip()]
    items = ProductDiscoveryService(db).get_prices(product_ids)
    return StandardResponse.ok("product prices", data=[item.model_dump() for item in items]).model_dump(mode="json")


@router.get("/products/{product_id}", response_model=None)
async def get_product_detail(
    product_id: int,
    pin_code: Optional[str] = None,
    db: Session = Depends(get_db),
    is_authenticated: bool = Depends(_is_authenticated),
):
    detail = await ProductDiscoveryService(db).get_product_detail(product_id, pin_code, is_authenticated)
    return StandardResponse.ok("product detail", data=detail.model_dump()).model_dump(mode="json")


# --- Wishlist (HLD/LLD §4.3.5) — owned by Catalog Service; called (not written) by
# US-004's Cart Service move-to-cart orchestration per ADR-0004. ---


@wishlist_router.get("", response_model=None)
def list_wishlist(
    db: Session = Depends(get_db),
    user: UserPayload = Depends(make_require_permission("wishlist:read")),
):
    items = WishlistService(db).list_items(user.id)
    return StandardResponse.ok("wishlist", data=[item.model_dump() for item in items]).model_dump(mode="json")


@wishlist_router.post("", response_model=None)
def add_wishlist_item(
    payload: WishlistItemCreate,
    db: Session = Depends(get_db),
    user: UserPayload = Depends(make_require_permission("wishlist:write")),
):
    item = WishlistService(db).add_item(user.id, payload.product_id)
    return StandardResponse.ok("added to wishlist", data=item.model_dump()).model_dump(mode="json")


@wishlist_router.get("/{wishlist_id}", response_model=None)
def get_wishlist_item(
    wishlist_id: int,
    db: Session = Depends(get_db),
    user: UserPayload = Depends(make_require_permission("wishlist:read")),
):
    item = WishlistService(db).get_item(wishlist_id, user.id)
    return StandardResponse.ok("wishlist item", data=item.model_dump()).model_dump(mode="json")


@wishlist_router.delete("/{wishlist_id}", response_model=None)
def delete_wishlist_item(
    wishlist_id: int,
    db: Session = Depends(get_db),
    user: UserPayload = Depends(make_require_permission("wishlist:write")),
):
    WishlistService(db).remove_item(wishlist_id, user.id)
    return StandardResponse.ok("removed from wishlist").model_dump(mode="json")
