from typing import Optional

from sqlalchemy import func, or_, text
from sqlalchemy.orm import Session

from .models import Product, ProductVariant
from .schemas import SortOption


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def _min_price_subquery(self):
        return (
            self.db.query(ProductVariant.product_id, func.min(ProductVariant.price).label("min_price"))
            .filter(ProductVariant.is_active.is_(True))
            .group_by(ProductVariant.product_id)
            .subquery()
        )

    def _base_query(self, subq):
        return (
            self.db.query(Product, subq.c.min_price)
            .join(subq, subq.c.product_id == Product.id)
            .filter(Product.status == "Published", Product.is_deleted.is_(False))
        )

    def _apply_filters(self, query, subq, category_id, price_min, price_max, brand_id, min_rating):
        if category_id is not None:
            query = query.filter(Product.category_id == category_id)
        if brand_id is not None:
            query = query.filter(Product.brand_id == brand_id)
        if min_rating is not None:
            query = query.filter(Product.avg_rating >= min_rating)
        if price_min is not None:
            query = query.filter(subq.c.min_price >= price_min)
        if price_max is not None:
            query = query.filter(subq.c.min_price <= price_max)
        return query

    def _apply_sort(self, query, subq, sort: SortOption):
        if sort == "price_asc":
            return query.order_by(subq.c.min_price.asc())
        if sort == "price_desc":
            return query.order_by(subq.c.min_price.desc())
        if sort == "popularity":
            return query.order_by(Product.purchase_count.desc())
        return query.order_by(Product.created_at.desc())  # "recency" (default)

    def list_products(
        self,
        category_id: Optional[int] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        brand_id: Optional[int] = None,
        min_rating: Optional[float] = None,
        sort: SortOption = "recency",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[tuple[Product, float]], int]:
        subq = self._min_price_subquery()
        query = self._base_query(subq)
        query = self._apply_filters(query, subq, category_id, price_min, price_max, brand_id, min_rating)
        total = query.count()
        query = self._apply_sort(query, subq, sort)
        rows = query.offset((page - 1) * page_size).limit(page_size).all()
        return rows, total

    def search(
        self,
        q: str,
        category_id: Optional[int] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        brand_id: Optional[int] = None,
        min_rating: Optional[float] = None,
        sort: Optional[SortOption] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[tuple[Product, float]], int]:
        """Relevance-ranked keyword search (ADR-0002): MySQL FULLTEXT in production,
        LIKE-based fallback on SQLite for local dev/test (no FULLTEXT equivalent there)."""
        subq = self._min_price_subquery()
        query = self._base_query(subq)
        query = self._apply_filters(query, subq, category_id, price_min, price_max, brand_id, min_rating)

        dialect = self.db.bind.dialect.name
        if dialect == "mysql":
            match_clause = text(
                "MATCH(products.title, products.description, products.tags) "
                "AGAINST (:q IN NATURAL LANGUAGE MODE)"
            ).bindparams(q=q)
            query = query.filter(match_clause)
            if sort:
                query = self._apply_sort(query, subq, sort)
            else:
                relevance = text(
                    "MATCH(products.title, products.description, products.tags) "
                    "AGAINST (:q IN NATURAL LANGUAGE MODE) DESC"
                ).bindparams(q=q)
                query = query.order_by(relevance)
        else:
            like = f"%{q}%"
            query = query.filter(
                or_(Product.title.ilike(like), Product.description.ilike(like), Product.tags.ilike(like))
            )
            query = self._apply_sort(query, subq, sort or "recency")

        total = query.count()
        rows = query.offset((page - 1) * page_size).limit(page_size).all()
        return rows, total

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return (
            self.db.query(Product)
            .filter(Product.id == product_id, Product.status == "Published", Product.is_deleted.is_(False))
            .first()
        )
