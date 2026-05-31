"""Database query and upsert helpers."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from supamarkt.db.models import Instrument, InstrumentProvider, PriceBar, Signal, SyncLog
from supamarkt.providers.base import OhlcvBar
from supamarkt.watchlists.default import WatchlistEntry


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")


def _bar_ts_iso(ts: datetime) -> str:
    return ts.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S")


async def fetch_provider_symbols(session: AsyncSession, instrument_id: int) -> dict[str, str]:
    """Load provider tickers without touching ORM relationships (async-safe)."""
    result = await session.execute(
        select(InstrumentProvider.provider, InstrumentProvider.provider_symbol).where(
            InstrumentProvider.instrument_id == instrument_id
        )
    )
    return dict(result.all())


async def upsert_instrument_from_entry(
    session: AsyncSession,
    entry: WatchlistEntry,
) -> Instrument:
    result = await session.execute(
        select(Instrument).where(Instrument.symbol == entry.symbol, Instrument.mic == entry.mic)
    )
    instrument = result.scalar_one_or_none()
    if instrument is None:
        instrument = Instrument(
            symbol=entry.symbol,
            mic=entry.mic,
            name=entry.name,
            region=entry.region,
            currency=entry.currency,
        )
        session.add(instrument)
        await session.flush()

    for provider, symbol in (
        ("finnhub", entry.finnhub_symbol),
        ("yfinance", entry.yfinance_symbol),
    ):
        row = await session.execute(
            select(InstrumentProvider).where(
                InstrumentProvider.instrument_id == instrument.id,
                InstrumentProvider.provider == provider,
            )
        )
        existing = row.scalar_one_or_none()
        if existing is None:
            session.add(
                InstrumentProvider(
                    instrument_id=instrument.id,
                    provider=provider,
                    provider_symbol=symbol,
                )
            )
        elif existing.provider_symbol != symbol:
            existing.provider_symbol = symbol

    await session.flush()
    return instrument


async def get_instrument_by_id(session: AsyncSession, instrument_id: int) -> Instrument | None:
    result = await session.execute(select(Instrument).where(Instrument.id == instrument_id))
    return result.scalar_one_or_none()


async def list_instruments(
    session: AsyncSession,
    *,
    region: str | None = None,
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Instrument]:
    stmt = (
        select(Instrument)
        .order_by(Instrument.region, Instrument.symbol)
        .limit(limit)
        .offset(offset)
    )
    if region:
        stmt = stmt.where(Instrument.region == region.upper())
    if q:
        pattern = f"%{q.strip()}%"
        stmt = stmt.where(
            Instrument.symbol.ilike(pattern)
            | Instrument.name.ilike(pattern)
            | Instrument.mic.ilike(pattern)
        )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def upsert_price_bars(
    session: AsyncSession,
    instrument_id: int,
    interval: str,
    bars: list[OhlcvBar],
) -> int:
    if not bars:
        return 0

    bar_keys = {_bar_ts_iso(bar.ts) for bar in bars}
    await session.execute(
        delete(PriceBar).where(
            PriceBar.instrument_id == instrument_id,
            PriceBar.interval == interval,
            PriceBar.bar_ts.in_(bar_keys),
        )
    )

    for bar in bars:
        session.add(
            PriceBar(
                instrument_id=instrument_id,
                bar_ts=_bar_ts_iso(bar.ts),
                interval=interval,
                open=bar.open,
                high=bar.high,
                low=bar.low,
                close=bar.close,
                volume=bar.volume,
            )
        )
    await session.flush()
    return len(bars)


async def fetch_price_bars(
    session: AsyncSession,
    instrument_id: int,
    *,
    interval: str,
    limit: int = 200,
) -> list[PriceBar]:
    result = await session.execute(
        select(PriceBar)
        .where(PriceBar.instrument_id == instrument_id, PriceBar.interval == interval)
        .order_by(PriceBar.bar_ts.desc())
        .limit(limit)
    )
    rows = list(result.scalars().all())
    rows.reverse()
    return rows


async def upsert_signal(
    session: AsyncSession,
    *,
    instrument_id: int,
    strategy: str,
    action: str,
    confidence: float,
    bar_ts: str,
    reasons: list[str],
) -> Signal:
    result = await session.execute(
        select(Signal).where(
            Signal.instrument_id == instrument_id,
            Signal.strategy == strategy,
        )
    )
    signal = result.scalar_one_or_none()
    payload = json.dumps(reasons)
    if signal is None:
        signal = Signal(
            instrument_id=instrument_id,
            strategy=strategy,
            action=action,
            confidence=confidence,
            bar_ts=bar_ts,
            reasons=payload,
            computed_at=_now(),
        )
        session.add(signal)
    else:
        signal.action = action
        signal.confidence = confidence
        signal.bar_ts = bar_ts
        signal.reasons = payload
        signal.computed_at = _now()
    await session.flush()
    return signal


async def list_signals(
    session: AsyncSession,
    *,
    watchlist_symbols: set[tuple[str, str]] | None = None,
    strategy: str | None = None,
    limit: int = 50,
) -> list[tuple[Signal, Instrument]]:
    stmt = (
        select(Signal, Instrument)
        .join(Instrument, Signal.instrument_id == Instrument.id)
        .order_by(Signal.computed_at.desc())
        .limit(limit)
    )
    if strategy:
        stmt = stmt.where(Signal.strategy == strategy)
    result = await session.execute(stmt)
    rows: list[tuple[Signal, Instrument]] = list(result.all())
    if watchlist_symbols:
        rows = [
            (signal, instrument)
            for signal, instrument in rows
            if (instrument.symbol, instrument.mic) in watchlist_symbols
        ]
    return rows


async def log_sync(
    session: AsyncSession,
    *,
    entity_type: str,
    entity_ref: str,
    status: str,
    message: str,
) -> None:
    session.add(
        SyncLog(
            entity_type=entity_type,
            entity_ref=entity_ref,
            status=status,
            message=message,
            synced_at=_now(),
        )
    )


