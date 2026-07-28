from typing import Any, Optional

import httpx


async def async_request(
    method: str,
    url: str,
    headers: Optional[dict] = None,
    params: Optional[dict] = None,
    json: Optional[dict] = None,
    timeout: float = 10.0,
) -> httpx.Response:
    """Shared inter-service / external HTTP client (per HLD/LLD #2.3.7)."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        return await client.request(method, url, headers=headers, params=params, json=json)
