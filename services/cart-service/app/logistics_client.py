import httpx

from ecom_core.utils.http_client import async_request

from .config import settings


async def check_delivery_feasibility(pin_code: str | None) -> str:
    """Calls the same Logistics feasibility contract owned by US-013
    (`GET /logistics/feasibility?pin=`) that catalog-service's product-detail
    endpoint already calls — same degraded-mode fallback: on timeout/unreachable,
    return "unknown" rather than failing the request."""
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
