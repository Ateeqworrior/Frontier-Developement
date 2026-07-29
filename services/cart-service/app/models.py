from datetime import datetime, timezone

from sqlalchemy import Boolean, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class CartItem(Base):
    """`cart_items` (HLD/LLD §5.2.1) — owned exclusively by Cart Service. No
    denormalized price is stored (docs/design/services/cart-service/data-model.md):
    price/title/image are enriched at read time via Catalog Service's batch-price
    endpoint, avoiding staleness against discounts/sponsorship changes."""

    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_saved_for_later: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index("idx_cart_user_saved", "user_id", "is_saved_for_later"),
        UniqueConstraint("user_id", "product_id", "is_saved_for_later", name="uq_cart_user_product"),
    )
