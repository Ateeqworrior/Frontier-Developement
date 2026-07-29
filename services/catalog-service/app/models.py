from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DECIMAL, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ecom_core.utils.soft_delete_mixin import SoftDeleteMixin

from .database import Base


class Category(Base, SoftDeleteMixin):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True)


class Product(Base, SoftDeleteMixin):
    """Minimal slice of the HLD/LLD #4.3.4 `products` schema needed for US-003 discovery.
    Vendor CRUD / approval-lifecycle writes are owned by US-011 and out of scope here."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vendor_id: Mapped[int] = mapped_column(Integer, index=True)
    brand_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(30), default="In Complete")
    sponsored: Mapped[str] = mapped_column(String(10), default="no")

    # New for US-003: denormalized, event-populated ranking columns (see ADR-0002 / data-model.md).
    avg_rating: Mapped[Optional[float]] = mapped_column(DECIMAL(3, 2), nullable=True)
    rating_count: Mapped[int] = mapped_column(Integer, default=0)
    purchase_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    category: Mapped[Optional["Category"]] = relationship("Category")
    variants: Mapped[list["ProductVariant"]] = relationship("ProductVariant", back_populates="product")

    __table_args__ = (
        Index("idx_products_category_status", "category_id", "status"),
        Index("idx_products_rating", "avg_rating"),
        Index("idx_products_popularity", "purchase_count"),
        # Native MySQL FULLTEXT (title, description, tags) is added via the migration in
        # docs/design/services/catalog-service/data-model.md — SQLite (dev/test) has no
        # FULLTEXT equivalent, so ProductRepository.search() falls back to LIKE there.
    )


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    images: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON-encoded array of S3 keys/URLs
    is_active: Mapped[bool] = mapped_column(default=True)

    product: Mapped["Product"] = relationship("Product", back_populates="variants")
