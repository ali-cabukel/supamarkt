"""yfinance fallback for OHLCV when Finnhub has no data."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import yfinance as yf

from supamarkt.providers.base import OhlcvBar, ProviderError
from supamarkt.settings import get_settings

YFINANCE_INTERVAL = {
    "5m": "5m",
    "15m": "15m",
    "1m": "1m",
}


def fetch_candles_sync(
    symbol: str,
    *,
    interval: str = "5m",
    lookback_days: int | None = None,
) -> list[OhlcvBar]:
    yf_interval = YFINANCE_INTERVAL.get(interval)
    if yf_interval is None:
        raise ProviderError(f"Unsupported interval for yfinance: {interval}")

    settings = get_settings()
    days = lookback_days or settings.collect_lookback_days
    # yfinance intraday history is limited; cap lookback for reliability
    period_days = min(days, 60 if interval == "5m" else 7)

    ticker = yf.Ticker(symbol)
    frame = ticker.history(period=f"{period_days}d", interval=yf_interval, auto_adjust=True)
    if frame.empty:
        return []

    bars: list[OhlcvBar] = []
    for ts, row in frame.iterrows():
        bar_ts = ts.replace(tzinfo=UTC) if ts.tzinfo is None else ts.astimezone(UTC)
        bars.append(
            OhlcvBar(
                ts=bar_ts,
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                volume=float(row["Volume"]),
            )
        )
    return bars


async def fetch_candles(
    symbol: str,
    *,
    interval: str = "5m",
    lookback_days: int | None = None,
) -> list[OhlcvBar]:
    import asyncio

    return await asyncio.to_thread(
        fetch_candles_sync,
        symbol,
        interval=interval,
        lookback_days=lookback_days,
    )


def filter_bars_since(bars: list[OhlcvBar], since: datetime) -> list[OhlcvBar]:
    return [bar for bar in bars if bar.ts >= since]


def default_since(lookback_days: int) -> datetime:
    return datetime.now(UTC) - timedelta(days=lookback_days)
