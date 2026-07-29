import json
from typing import Optional

from sqlalchemy.orm import Session

from ecom_core.utils.errors import (
    DuplicateResourceError,
    InvalidPriceRangeError,
    InvalidSearchQueryError,
    ProductNotFoundError,
    WishlistItemNotFoundError,
)

from .config import settings
from .logistics_client import check_delivery_feasibility
from .models import Product
from .repository import ProductRepository, WishlistRepository
from .schemas import PriceBreakdown, ProductDetail, ProductPriceSummary, ProductSummary, SortOption, WishlistItemResponse


class ProductDiscoveryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductRepository(db)

    @staticmethod
    def _validate_price_range(price_min: Optional[float], price_max: Optional[float]) -> None:
        if price_min is not None and price_max is not None and price_min > price_max:
            raise InvalidPriceRangeError()

    @staticmethod
    def _to_summary(product: Product, min_price: float) -> ProductSummary:
        images = []
        if product.variants:
            images = json.loads(product.variants[0].images or "[]")
        return ProductSummary(
            id=product.id,
            title=product.title,
            brand_id=product.brand_id,
            category_id=product.category_id,
            base_price=float(min_price),
            avg_rating=float(product.avg_rating) if product.avg_rating is not None else None,
            rating_count=product.rating_count,
            image_url=images[0] if images else None,
        )

    def list_products(
        self,
        category_id: Optional[int],
        price_min: Optional[float],
        price_max: Optional[float],
        brand_id: Optional[int],
        min_rating: Optional[float],
        sort: SortOption,
        page: int,
        page_size: int,
    ) -> tuple[list[ProductSummary], int]:
        self._validate_price_range(price_min, price_max)
        rows, total = self.repo.list_products(
            category_id, price_min, price_max, brand_id, min_rating, sort, page, page_size
        )
        return [self._to_summary(product, min_price) for product, min_price in rows], total

    def search_products(
        self,
        q: str,
        category_id: Optional[int],
        price_min: Optional[float],
        price_max: Optional[float],
        brand_id: Optional[int],
        min_rating: Optional[float],
        sort: Optional[SortOption],
        page: int,
        page_size: int,
    ) -> tuple[list[ProductSummary], int]:
        if not q or len(q) < 2:
            raise InvalidSearchQueryError()
        self._validate_price_range(price_min, price_max)
        rows, total = self.repo.search(
            q, category_id, price_min, price_max, brand_id, min_rating, sort, page, page_size
        )
        return [self._to_summary(product, min_price) for product, min_price in rows], total

    async def get_product_detail(self, product_id: int, pin_code: Optional[str], is_authenticated: bool) -> ProductDetail:
        product = self.repo.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError()

        variant = product.variants[0] if product.variants else None
        base_price = float(variant.price) if variant else 0.0
        stock_quantity = variant.quantity if variant else 0
        images = json.loads(variant.images or "[]") if variant else []

        discounted_price = None
        if product.sponsored == "yes" and is_authenticated:
            discounted_price = round(base_price * (1 - settings.sponsored_discount_percent / 100), 2)

        taxable_amount = discounted_price if discounted_price is not None else base_price
        tax = round(taxable_amount * settings.tax_rate_percent / 100, 2)
        total = round(taxable_amount + tax + settings.delivery_charge, 2)

        feasibility = await check_delivery_feasibility(pin_code)

        return ProductDetail(
            id=product.id,
            title=product.title,
            description=product.description,
            specifications={},
            stock_quantity=stock_quantity,
            images=images,
            price_breakdown=PriceBreakdown(
                basic_price=base_price,
                discounted_price=discounted_price,
                tax=tax,
                delivery_charge=settings.delivery_charge,
                total=total,
            ),
            delivery_feasibility=feasibility,
        )

    def get_prices(self, product_ids: list[int]) -> list[ProductPriceSummary]:
        """Batch price/title/image lookup — new upstream dependency for US-004
        (Cart Service) cart-total enrichment, avoiding an N+1 call pattern."""
        products = self.repo.get_by_ids(product_ids)
        summaries = []
        for product in products:
            variant = product.variants[0] if product.variants else None
            price = float(variant.price) if variant else 0.0
            images = json.loads(variant.images or "[]") if variant else []
            summaries.append(
                ProductPriceSummary(
                    id=product.id,
                    title=product.title,
                    image_url=images[0] if images else None,
                    price=price,
                )
            )
        return summaries


class WishlistService:
    """Wishlist CRUD (HLD/LLD §4.3.5) — owned by Catalog Service. Called by US-004's
    Cart Service move-to-cart orchestration per ADR-0004, never written to directly."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = WishlistRepository(db)
        self.product_repo = ProductRepository(db)

    def _to_response(self, item) -> WishlistItemResponse:
        product = item.product
        variant = product.variants[0] if product and product.variants else None
        price = float(variant.price) if variant else 0.0
        images = json.loads(variant.images or "[]") if variant else []
        return WishlistItemResponse(
            id=item.id,
            product_id=item.product_id,
            title=product.title if product else "",
            image_url=images[0] if images else None,
            price=price,
            created_at=item.created_at.isoformat(),
        )

    def list_items(self, user_id: int) -> list[WishlistItemResponse]:
        return [self._to_response(item) for item in self.repo.get_by_user(user_id)]

    def add_item(self, user_id: int, product_id: int) -> WishlistItemResponse:
        product = self.product_repo.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError()
        existing = self.repo.get_by_user_and_product(user_id, product_id)
        if existing is not None:
            raise DuplicateResourceError("product is already in the wishlist", "duplicate_wishlist_item")
        item = self.repo.add(user_id, product_id)
        return self._to_response(item)

    def get_item(self, wishlist_id: int, user_id: int) -> WishlistItemResponse:
        item = self.repo.get_by_id(wishlist_id)
        if item is None or item.user_id != user_id:
            raise WishlistItemNotFoundError()
        return self._to_response(item)

    def remove_item(self, wishlist_id: int, user_id: int) -> None:
        item = self.repo.get_by_id(wishlist_id)
        if item is None or item.user_id != user_id:
            raise WishlistItemNotFoundError()
        self.repo.delete(item)
