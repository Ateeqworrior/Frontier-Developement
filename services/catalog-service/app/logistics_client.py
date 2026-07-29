import httpx

from ecom_core.utils.http_client import async_request

from .config import settings


async def check_delivery_feasibility(pin_code: str | None) -> str:
    """Calls the Logistics feasibility contract owned by US-013 (`GET /logistics/feasibility?pin=`).
    Degraded-mode behaviour (docs/design/services/catalog-service/error-handling.md): on
    timeout/unreachable, return "unknown" rather than failing the product-detail request —
    US-013 is Wave 3 and may not be deployed yet when US-003 ships."""
    if not pin_code:
        return "unknown"

    try:
        response = await async_request(
            "GET",
            settings.logistics_feasibility_url,
            params={"pin": pin_code},
            timeout=10.0,
        )
    except httpx.HTTPError:
        return "unknown"

    if response.status_code != 200:
        return "unknown"

    body = response.json()
    feasible = body.get("data", {}).get("feasible")
    if feasible is True:
        return "feasible"
    if feasible is False:
        return "not_feasible"
    return "unknown"
