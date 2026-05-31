"""Run strategies over stored bars and persist signals."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from supamarkt.analytics.strategies import ema_trend_5m
from supamarkt.db.models import Instrument
from supamarkt.db.repository import fetch_price_bars, upsert_signal
from supamarkt.settings import get_settings


async def analyze_instrument(
    session: AsyncSession,
    instrument: Instrument,
    *,
    strategy: str,
) -> ema_trend_5m.StrategyResult | None:
    settings = get_settings()
    interval = settings.intraday_interval
    bars = await fetch_price_bars(session, instrument.id, interval=interval, limit=300)
    if not bars:
        return None

    bar_ts_list = [row.bar_ts for row in bars]
    closes = [row.close for row in bars]

    if strategy == "ema_trend_5m":
        return ema_trend_5m.analyze(bar_ts_list=bar_ts_list, closes=closes)

    raise ValueError(f"Strategy not implemented: {strategy}")


async def run_analysis(
    session: AsyncSession,
    instruments: list[Instrument],
    *,
    strategy: str,
) -> int:
    count = 0
    for instrument in instruments:
        result = await analyze_instrument(session, instrument, strategy=strategy)
        if result is None:
            continue
        await upsert_signal(
            session,
            instrument_id=instrument.id,
            strategy=strategy,
            action=result.action,
            confidence=result.confidence,
            bar_ts=result.bar_ts,
            reasons=result.reasons,
        )
        count += 1
    return count
