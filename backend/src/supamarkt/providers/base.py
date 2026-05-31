"""Shared types for market data providers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class OhlcvBar:
    """Single OHLCV candle."""

    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    @classmethod
    def from_unix(
        cls,
        ts: int,
        open_: float,
        high: float,
        low: float,
        close: float,
        volume: float,
    ) -> OhlcvBar:
        return cls(
            ts=datetime.fromtimestamp(ts, tz=UTC),
            open=open_,
            high=high,
            low=low,
            close=close,
            volume=volume,
        )


class ProviderError(Exception):
    """Raised when a market data provider fails."""
