"""Tests for Finnhub candle parsing."""

from __future__ import annotations

import httpx
import pytest

from supamarkt.providers.finnhub import FinnhubClient


@pytest.mark.asyncio
async def test_fetch_candles_parses_ok_response():
    payload = {
        "s": "ok",
        "t": [1_700_000_000, 1_700_000_300],
        "o": [100.0, 101.0],
        "h": [101.0, 102.0],
        "l": [99.0, 100.5],
        "c": [100.5, 101.5],
        "v": [1000.0, 1200.0],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["symbol"] == "AAPL"
        assert request.url.params["resolution"] == "5"
        return httpx.Response(200, json=payload)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client, FinnhubClient(
        api_key="test-key", client=client
    ) as fh:
        bars = await fh.fetch_candles("AAPL", interval="5m", from_ts=1, to_ts=2)

    assert len(bars) == 2
    assert bars[0].close == 100.5
    assert bars[1].volume == 1200.0


@pytest.mark.asyncio
async def test_fetch_candles_returns_empty_on_no_data():
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json={"s": "no_data"})
    )
    async with httpx.AsyncClient(transport=transport) as client, FinnhubClient(
        api_key="test-key", client=client
    ) as fh:
        bars = await fh.fetch_candles("UNKNOWN", interval="5m", from_ts=1, to_ts=2)
    assert bars == []


@pytest.mark.asyncio
async def test_fetch_candles_returns_empty_on_403():
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            403,
            json={"error": "You don't have access to this resource."},
        )
    )
    async with httpx.AsyncClient(transport=transport) as client, FinnhubClient(
        api_key="test-key", client=client
    ) as fh:
        bars = await fh.fetch_candles("AAPL", interval="5m", from_ts=1, to_ts=2)
    assert bars == []
