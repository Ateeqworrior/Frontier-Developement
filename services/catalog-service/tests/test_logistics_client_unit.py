"""Unit tests for the Logistics feasibility client (US-013 integration point).
Mocks the shared `async_request` boundary — no real Logistics service exists yet
(US-013 is Wave 3), so these tests verify this story's degraded-mode handling."""

import asyncio

import httpx

from app import logistics_client


class _FakeResponse:
    def __init__(self, status_code, body):
        self.status_code = status_code
        self._body = body

    def json(self):
        return self._body


def test_no_pin_code_returns_unknown_without_calling_out(monkeypatch):
    called = False

    async def _fail_if_called(*args, **kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(logistics_client, "async_request", _fail_if_called)
    result = asyncio.run(logistics_client.check_delivery_feasibility(None))
    assert result == "unknown"
    assert called is False


def test_feasible_response(monkeypatch):
    async def _fake_request(*args, **kwargs):
        return _FakeResponse(200, {"data": {"feasible": True}})

    monkeypatch.setattr(logistics_client, "async_request", _fake_request)
    assert asyncio.run(logistics_client.check_delivery_feasibility("560001")) == "feasible"


def test_not_feasible_response(monkeypatch):
    async def _fake_request(*args, **kwargs):
        return _FakeResponse(200, {"data": {"feasible": False}})

    monkeypatch.setattr(logistics_client, "async_request", _fake_request)
    assert asyncio.run(logistics_client.check_delivery_feasibility("560001")) == "not_feasible"


def test_non_200_response_is_unknown(monkeypatch):
    async def _fake_request(*args, **kwargs):
        return _FakeResponse(500, {})

    monkeypatch.setattr(logistics_client, "async_request", _fake_request)
    assert asyncio.run(logistics_client.check_delivery_feasibility("560001")) == "unknown"


def test_unreachable_service_degrades_to_unknown(monkeypatch):
    async def _raise_timeout(*args, **kwargs):
        raise httpx.ConnectTimeout("timed out")

    monkeypatch.setattr(logistics_client, "async_request", _raise_timeout)
    assert asyncio.run(logistics_client.check_delivery_feasibility("560001")) == "unknown"
