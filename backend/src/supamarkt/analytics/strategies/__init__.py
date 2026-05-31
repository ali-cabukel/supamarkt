"""Registered trading strategies."""

from __future__ import annotations

from collections.abc import Callable

from supamarkt.analytics.strategies import ema_trend_5m

StrategyFn = Callable[..., ema_trend_5m.StrategyResult | None]

STRATEGIES: dict[str, str] = {
    "ema_trend_5m": "EMA 9/21 trend on 5-minute bars",
}


def list_strategies() -> dict[str, str]:
    return dict(STRATEGIES)


def get_strategy(name: str) -> str:
    if name not in STRATEGIES:
        known = ", ".join(sorted(STRATEGIES))
        raise ValueError(f"Unknown strategy {name!r}. Choose from: {known}")
    return name
