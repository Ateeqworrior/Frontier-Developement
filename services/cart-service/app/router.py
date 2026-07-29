from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ecom_core.auth_common.constants import UserPayload
from ecom_core.auth_common.dependencies import make_require_permission
from ecom_core.auth_common.security import bearer_scheme
from ecom_core.utils.standard_response import StandardResponse

from .database import get_db
from .schemas import CartItemCreate, CartItemUpdate
from .services import CartService

router = APIRouter(prefix="/api/cart", tags=["cart"])


class SaveForLaterUpdate(BaseModel):
    is_saved_for_later: bool


@router.get("", response_model=None)
async def get_cart(
    db: Session = Depends(get_db),
    user: UserPayload = Depends(make_require_permission("cart:read")),
):
    cart = await CartService(db).get_cart(user.id)
    return StandardResponse.ok("cart", data=cart.model_dump()).model_dump(mode="json")


@router.post("/items", response_model=None)
def add_item(
    payload: CartItemCreate,
    db: Session = Depends(get_db),
    user: UserPayload = Depends(make_require_permission("cart:write")),
):
    item = CartService(db).add_item(user.id, payload.product_id, payload.quantity)
    return StandardResponse.ok(
        "added to cart",
        data={"id": item.id, "product_id": item.product_id, "quantity": item.quantity},
    ).model_dump(mode="json")


@router.put("/items/{item_id}", response_model=None)
def update_item(
    item_id: int,
    payload: CartItemUpdate,
    db: Session = Depends(get_db),
    user: UserPayload = Depends(make_require_permission("cart:write")),
):
    item = CartService(db).update_item(user.id, item_id, payload.quantity)
    return StandardResponse.ok(
        "cart item updated",
        data={"id": item.id, "product_id": item.product_id, "quantity": item.quantity},
    ).model_dump(mode="json")


@router.delete("/items/{item_id}", response_model=None)
def remove_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: UserPayload = Depends(make_require_permission("cart:write")),
):
    CartService(db).remove_item(user.id, item_id)
    return StandardResponse.ok("removed from cart").model_dump(mode="json")


@router.put("/items/{item_id}/save-for-later", response_model=None)
def set_saved_for_later(
    item_id: int,
    payload: SaveForLaterUpdate,
    db: Session = Depends(get_db),
    user: UserPayload = Depends(make_require_permission("cart:write")),
):
    item = CartService(db).set_saved_for_later(user.id, item_id, payload.is_saved_for_later)
    return StandardResponse.ok(
        "cart item updated",
        data={"id": item.id, "product_id": item.product_id, "is_saved_for_later": item.is_saved_for_later},
    ).model_dump(mode="json")


@router.get("/delivery-feasibility", response_model=None)
async def get_delivery_feasibility(
    pin_code: Optional[str] = None,
    db: Session = Depends(get_db),
    user: UserPayload = Depends(make_require_permission("cart:read")),
):
    result = await CartService(db).get_delivery_feasibility(pin_code)
    return StandardResponse.ok("delivery feasibility", data=result.model_dump()).model_dump(mode="json")


@router.post("/wishlist/{wishlist_id}/move-to-cart", response_model=None)
async def move_wishlist_item_to_cart(
    wishlist_id: int,
    db: Session = Depends(get_db),
    user: UserPayload = Depends(make_require_permission("cart:write")),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    result = await CartService(db).move_wishlist_item_to_cart(user.id, wishlist_id, credentials.credentials)
    return StandardResponse.ok("moved to cart", data=result.model_dump()).model_dump(mode="json")
