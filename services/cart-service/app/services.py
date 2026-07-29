from typing import Optional

from sqlalchemy.orm import Session

from ecom_core.utils.errors import CartItemNotFoundError, InvalidPinCodeError, WishlistItemNotFoundError

from . import catalog_client
from .config import settings
from .logistics_client import check_delivery_feasibility
from .models import CartItem
from .repository import CartItemRepository
from .schemas import CartItemOut, CartOut, CartTotals, FeasibilityOut, MoveToCartOut


class CartService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CartItemRepository(db)

    def _get_owned_item(self, item_id: int, user_id: int) -> CartItem:
        item = self.repo.get_by_id(item_id)
        if item is None or item.user_id != user_id:
            raise CartItemNotFoundError()
        return item

    def add_item(self, user_id: int, product_id: int, quantity: int) -> CartItem:
        """Adds a product to the active cart, or increments quantity if it's
        already there (the unique (user_id, product_id, is_saved_for_later)
        constraint means a second insert for the same product would conflict)."""
        existing = self.repo.get_active_by_user_and_product(user_id, product_id)
        if existing is not None:
            return self.repo.update_quantity(existing, existing.quantity + quantity)
        return self.repo.create(user_id, product_id, quantity)

    def update_item(self, user_id: int, item_id: int, quantity: int) -> CartItem:
        item = self._get_owned_item(item_id, user_id)
        return self.repo.update_quantity(item, quantity)

    def remove_item(self, user_id: int, item_id: int) -> None:
        item = self._get_owned_item(item_id, user_id)
        self.repo.delete(item)

    def set_saved_for_later(self, user_id: int, item_id: int, is_saved_for_later: bool) -> CartItem:
        item = self._get_owned_item(item_id, user_id)
        return self.repo.set_saved_for_later(item, is_saved_for_later)

    @staticmethod
    def _compute_totals(items: list[CartItemOut]) -> Optional[CartTotals]:
        """Recomputed fresh on every call — nothing is cached, so "recalculates
        immediately" (US-004 AC) is satisfied by construction. Returns None if any
        active item's price is unknown (Catalog Service degraded — see
        docs/design/services/cart-service/error-handling.md)."""
        active_items = [item for item in items if not item.is_saved_for_later]
        if any(item.price is None for item in active_items):
            return None

        subtotal = sum(item.price * item.quantity for item in active_items)
        tax = round(subtotal * settings.tax_rate_percent / 100, 2)
        delivery_charge = 0.0 if subtotal >= settings.free_delivery_threshold else settings.delivery_flat_charge
        grand_total = round(subtotal + tax + delivery_charge, 2)
        return CartTotals(subtotal=round(subtotal, 2), tax=tax, delivery_charge=delivery_charge, grand_total=grand_total)

    async def get_cart(self, user_id: int) -> CartOut:
        rows = self.repo.get_by_user(user_id)
        prices = await catalog_client.get_batch_prices([row.product_id for row in rows])

        items = []
        for row in rows:
            price_info = prices.get(row.product_id)
            items.append(
                CartItemOut(
                    id=row.id,
                    product_id=row.product_id,
                    quantity=row.quantity,
                    is_saved_for_later=row.is_saved_for_later,
                    title=price_info["title"] if price_info else None,
                    image_url=price_info.get("image_url") if price_info else None,
                    price=price_info["price"] if price_info else None,
                )
            )
        return CartOut(items=items, totals=self._compute_totals(items))

    async def get_delivery_feasibility(self, pin_code: Optional[str]) -> FeasibilityOut:
        if not pin_code or not pin_code.strip() or len(pin_code) > 10:
            raise InvalidPinCodeError()
        feasibility = await check_delivery_feasibility(pin_code)
        return FeasibilityOut(pin_code=pin_code, feasibility=feasibility)

    async def move_wishlist_item_to_cart(self, user_id: int, wishlist_id: int, token: str) -> MoveToCartOut:
        """Orchestrates: read wishlist item (Catalog Service) -> upsert cart_items
        -> delete wishlist item (Catalog Service). See ADR-0004 — a failed delete
        after a successful cart insert is a partial-success outcome, not rolled
        back (duplicating into the cart is safe/correctable; losing it from both
        places is not)."""
        wishlist_item = await catalog_client.get_wishlist_item(wishlist_id, token)
        if wishlist_item is None:
            raise WishlistItemNotFoundError()

        product_id = wishlist_item["product_id"]
        cart_item = self.add_item(user_id, product_id, quantity=1)
        wishlist_removed = await catalog_client.delete_wishlist_item(wishlist_id, token)

        return MoveToCartOut(
            cart_item=CartItemOut(
                id=cart_item.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                is_saved_for_later=cart_item.is_saved_for_later,
                title=wishlist_item.get("title"),
                image_url=wishlist_item.get("image_url"),
                price=wishlist_item.get("price"),
            ),
            wishlist_removed=wishlist_removed,
        )
