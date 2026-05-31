"""Finnhub REST client for intraday OHLCV."""

from __future__ import annotations

from datetime import UTC, datetime

import httpx

from supamarkt.providers.base import OhlcvBar, ProviderError
from supamarkt.settings import get_settings

FINNHUB_BASE = "https://finnhub.io/api/v1"

# Finnhub resolution string -> our interval id
RESOLUTION_MAP = {
    "1m": "1",
    "5m": "5",
    "15m": "15",
    "30m": "30",
    "60m": "60",
}


class FinnhubClient:
    def __init__(
        self,
        api_key: str | None = None,
        *,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        settings = get_settings()
        self._api_key = api_key or settings.finnhub_api_key.get_secret_value()
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self) -> FinnhubClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, *args: object) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None

    async def fetch_candles(
        self,
        symbol: str,
        *,
        interval: str = "5m",
        from_ts: int | None = None,
        to_ts: int | None = None,
    ) -> list[OhlcvBar]:
        if not self._api_key:
            raise ProviderError("FINNHUB_API_KEY is not set")

        resolution = RESOLUTION_MAP.get(interval)
        if resolution is None:
            raise ProviderError(f"Unsupported interval for Finnhub: {interval}")

        settings = get_settings()
        now = datetime.now(UTC)
        to_ts = to_ts or int(now.timestamp())
        from_ts = from_ts or int(
            now.timestamp() - settings.collect_lookback_days * 86400
        )

        assert self._client is not None
        response = await self._client.get(
            f"{FINNHUB_BASE}/stock/candle",
            params={
                "symbol": symbol,
                "resolution": resolution,
                "from": from_ts,
                "to": to_ts,
                "token": self._api_key,
            },
        )
        # Free tier does not include /stock/candle (paid market-data plan).
        if response.status_code in {401, 403}:
            return []
        response.raise_for_status()
        payload = response.json()

        if payload.get("s") != "ok":
            return []

        timestamps = payload.get("t") or []
        opens = payload.get("o") or []
        highs = payload.get("h") or []
        lows = payload.get("l") or []
        closes = payload.get("c") or []
        volumes = payload.get("v") or []

        bars: list[OhlcvBar] = []
        for i, ts in enumerate(timestamps):
            bars.append(
                OhlcvBar.from_unix(
                    int(ts),
                    float(opens[i]),
                    float(highs[i]),
                    float(lows[i]),
                    float(closes[i]),
                    float(volumes[i]),
                )
            )
        return bars
