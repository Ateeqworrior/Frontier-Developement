from typing import Optional

from sqlalchemy.orm import Session

from .models import CartItem


class CartItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user(self, user_id: int) -> list[CartItem]:
        return (
            self.db.query(CartItem)
            .filter(CartItem.user_id == user_id)
            .order_by(CartItem.created_at.desc())
            .all()
        )

    def get_by_id(self, item_id: int) -> Optional[CartItem]:
        return self.db.query(CartItem).filter(CartItem.id == item_id).first()

    def get_active_by_user_and_product(self, user_id: int, product_id: int) -> Optional[CartItem]:
        return (
            self.db.query(CartItem)
            .filter(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id,
                CartItem.is_saved_for_later.is_(False),
            )
            .first()
        )

    def create(self, user_id: int, product_id: int, quantity: int) -> CartItem:
        item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_quantity(self, item: CartItem, quantity: int) -> CartItem:
        item.quantity = quantity
        self.db.commit()
        self.db.refresh(item)
        return item

    def set_saved_for_later(self, item: CartItem, is_saved_for_later: bool) -> CartItem:
        item.is_saved_for_later = is_saved_for_later
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: CartItem) -> None:
        self.db.delete(item)
        self.db.commit()
