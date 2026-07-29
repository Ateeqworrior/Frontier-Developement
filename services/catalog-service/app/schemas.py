from typing import Literal, Optional

from pydantic import BaseModel, Field

SortOption = Literal["price_asc", "price_desc", "recency", "popularity"]


class ProductSummary(BaseModel):
    id: int
    title: str
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    base_price: float
    avg_rating: Optional[float] = None
    rating_count: int
    image_url: Optional[str] = None


class ProductListQuery(BaseModel):
    category_id: Optional[int] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    brand_id: Optional[int] = None
    min_rating: Optional[float] = Field(default=None, ge=0, le=5)
    sort: SortOption = "recency"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PriceBreakdown(BaseModel):
    basic_price: float
    discounted_price: Optional[float] = None
    tax: float
    delivery_charge: float
    total: float


class ProductDetail(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    specifications: dict = {}
    stock_quantity: int
    images: list[str] = []
    price_breakdown: PriceBreakdown
    delivery_feasibility: Literal["feasible", "not_feasible", "unknown"]
