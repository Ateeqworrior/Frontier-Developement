"""External integrations for US-001: CARS OIDC and the Sarthak Foundation UDID endpoint.

Both are stubbed against the ADR-0001 / HLD contract shape rather than calling a real
external service — MartSarathi's CARS/Sarthak Foundation endpoints are not reachable
from this environment. Swap `httpx` calls in for the marked TODOs once those endpoints
are available; the surrounding service logic (exchange_principal, verify_udid) does not
need to change.
"""

from typing import Optional

from ecom_core.utils.errors import CarsAuthFailedError, UdidNotMatchedError, UdidServiceUnavailableError

from .config import settings
from .schemas import Principal


async def exchange_cars_code_for_principal(code: str) -> Principal:
    """ADR-0001: exchange a CARS OIDC authorization code for a validated principal.

    TODO(real CARS integration): POST to settings.cars_token_url with `code`,
    `client_id`/`client_secret`, validate the returned ID token's signature and
    issuer, then map its claims to a Principal.
    """
    if not code:
        raise CarsAuthFailedError("missing authorization code")
    # Deterministic stub used until the real CARS token endpoint is wired up:
    # decodes a `dev-code:<email>:<password>:<isEnabled>` test code so the callback
    # route is exercisable end-to-end in local/dev/test without a live CARS instance.
    if code.startswith("dev-code:"):
        try:
            _, email, password, is_enabled = code.split(":", 3)
        except ValueError as exc:
            raise CarsAuthFailedError("malformed dev authorization code") from exc
        return Principal(email=email, password=password, isEnabled=is_enabled.lower() == "true")
    raise CarsAuthFailedError("unrecognized authorization code")


async def verify_udid_with_sarthak_foundation(udid_number: str) -> bool:
    """Calls the Sarthak Foundation UDID verification endpoint.

    TODO(real integration): replace the stub below with
    `await async_request("GET", settings.sarthak_udid_verify_url, params={"udid": udid_number})`
    and interpret its response body/status per the Foundation's API contract.
    """
    if not udid_number:
        raise UdidNotMatchedError("empty UDID")
    # Stub matcher: any UDID starting with "SF-" is treated as a verified Sarthak
    # Foundation record; "TIMEOUT" simulates the endpoint being unreachable.
    if udid_number == "TIMEOUT":
        raise UdidServiceUnavailableError()
    if udid_number.startswith("SF-"):
        return True
    raise UdidNotMatchedError()


def build_cars_authorize_redirect_url(state: Optional[str] = None) -> str:
    query = f"?client_id={settings.cars_client_id}&redirect_uri={settings.cars_redirect_uri}&response_type=code"
    if state:
        query += f"&state={state}"
    return settings.cars_authorize_url + query
