from typing import Optional

import httpx

from ecom_core.utils.http_client import async_request

from .config import settings


async def get_batch_prices(product_ids: list[int]) -> dict[int, dict]:
    """Batch price/title/image lookup (docs/design/services/cart-service/design.md).
    Degraded-mode behaviour: on timeout/unreachable/non-200, return {} so the caller
    can fall back to `price: null` / `totals: null` rather than failing the whole
    cart read — Catalog Service being briefly unavailable must not block viewing
    the cart (platform NFR: partial-failure dependencies degrade, not fail)."""
    if not product_ids:
        return {}

    ids_param = ",".join(str(pid) for pid in product_ids)
    try:
        response = await async_request(
            "GET",
            f"{settings.catalog_service_url}/products/prices",
            params={"ids": ids_param},
            timeout=10.0,
        )
    except httpx.HTTPError:
        return {}

    if response.status_code != 200:
        return {}

    body = response.json()
    return {item["id"]: item for item in body.get("data", [])}


async def get_wishlist_item(wishlist_id: int, token: str) -> Optional[dict]:
    """Reads a wishlist item via Catalog Service's `/api/v1/wishlist/{id}` (ADR-0004).
    Returns None on 404 *or* any transport/server error — the move-to-cart AC does
    not distinguish "doesn't exist" from "temporarily unreachable"; both mean the
    move cannot proceed right now."""
    try:
        response = await async_request(
            "GET",
            f"{settings.wishlist_service_url}/{wishlist_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0,
        )
    except httpx.HTTPError:
        return None

    if response.status_code != 200:
        return None

    return response.json().get("data")


async def delete_wishlist_item(wishlist_id: int, token: str) -> bool:
    """Deletes a wishlist item via Catalog Service. Returns False (not an exception)
    on failure — per ADR-0004, a failed wishlist-delete after a successful cart
    insert is a partial-success outcome (`wishlist_removed: false`), not a hard
    error; the item is already safely in the cart."""
    try:
        response = await async_request(
            "DELETE",
            f"{settings.wishlist_service_url}/{wishlist_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0,
        )
    except httpx.HTTPError:
        return False

    return response.status_code == 200
