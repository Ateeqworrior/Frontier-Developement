from typing import Literal, Optional

from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    is_saved_for_later: bool
    title: Optional[str] = None
    image_url: Optional[str] = None
    price: Optional[float] = None


class CartTotals(BaseModel):
    subtotal: float
    tax: float
    delivery_charge: float
    grand_total: float


class CartOut(BaseModel):
    items: list[CartItemOut]
    totals: Optional[CartTotals] = None


class FeasibilityOut(BaseModel):
    pin_code: str
    feasibility: Literal["feasible", "not_feasible", "unknown"]


class MoveToCartOut(BaseModel):
    cart_item: CartItemOut
    wishlist_removed: bool
