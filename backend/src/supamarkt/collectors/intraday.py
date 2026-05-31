"""Collect intraday OHLCV for watchlist instruments."""

from __future__ import annotations

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from supamarkt.console import done, info, warn
from supamarkt.db.models import Instrument
from supamarkt.db.repository import (
    fetch_provider_symbols,
    log_sync,
    upsert_instrument_from_entry,
    upsert_price_bars,
)
from supamarkt.providers.finnhub import FinnhubClient
from supamarkt.providers.yfinance_provider import (
    default_since,
    filter_bars_since,
)
from supamarkt.providers.yfinance_provider import (
    fetch_candles as yfinance_fetch,
)
from supamarkt.settings import get_settings
from supamarkt.watchlists.default import WatchlistEntry, get_watchlist


async def _fetch_bars_for_instrument(
    session: AsyncSession,
    instrument: Instrument,
    *,
    interval: str,
    finnhub: FinnhubClient,
) -> tuple[list, str]:
    settings = get_settings()
    since = default_since(settings.collect_lookback_days)
    symbols = await fetch_provider_symbols(session, instrument.id)
    fh_symbol = symbols.get("finnhub")
    yf_symbol = symbols.get("yfinance")

    bars = []
    source = "none"
    finnhub_denied = False

    use_finnhub = settings.data_provider_primary.lower() == "finnhub" and fh_symbol
    if use_finnhub:
        bars = await finnhub.fetch_candles(fh_symbol, interval=interval)
        if bars:
            source = "finnhub"
            bars = filter_bars_since(bars, since)
        else:
            finnhub_denied = True

    if not bars and yf_symbol:
        if finnhub_denied:
            warn(
                f"Finnhub candle API not available on free tier for {instrument.symbol}; "
                f"using yfinance ({yf_symbol})"
            )
        else:
            warn(f"No Finnhub data for {instrument.symbol}; trying yfinance ({yf_symbol})")
        bars = await yfinance_fetch(yf_symbol, interval=interval)
        bars = filter_bars_since(bars, since)
        if bars:
            source = "yfinance"

    return bars, source


async def collect_instrument(
    session: AsyncSession,
    instrument: Instrument,
    *,
    finnhub: FinnhubClient,
) -> int:
    settings = get_settings()
    interval = settings.intraday_interval
    ref = f"{instrument.symbol}:{instrument.mic}"

    try:
        bars, source = await _fetch_bars_for_instrument(
            session,
            instrument,
            interval=interval,
            finnhub=finnhub,
        )
        if not bars:
            await log_sync(
                session,
                entity_type="price_bars",
                entity_ref=ref,
                status="empty",
                message=f"No {interval} bars from Finnhub or yfinance",
            )
            warn(f"No bars collected for {ref}")
            return 0

        count = await upsert_price_bars(session, instrument.id, interval, bars)
        await log_sync(
            session,
            entity_type="price_bars",
            entity_ref=ref,
            status="ok",
            message=f"Upserted {count} {interval} bars via {source}",
        )
        info(f"{ref}: {count} bars ({source})")
        return count
    except Exception as exc:
        await log_sync(
            session,
            entity_type="price_bars",
            entity_ref=ref,
            status="error",
            message=str(exc),
        )
        raise


async def seed_watchlist_entries(
    session: AsyncSession,
    entries: tuple[WatchlistEntry, ...],
) -> list[Instrument]:
    instruments: list[Instrument] = []
    for entry in entries:
        instruments.append(await upsert_instrument_from_entry(session, entry))
    return instruments


async def collect_watchlist(
    session: AsyncSession,
    watchlist_name: str,
) -> int:
    entries = get_watchlist(watchlist_name)
    instruments = await seed_watchlist_entries(session, entries)
    settings = get_settings()
    delay = settings.collect_symbol_delay_seconds

    total = 0
    async with FinnhubClient() as finnhub:
        for i, instrument in enumerate(instruments):
            if i > 0 and delay > 0:
                await asyncio.sleep(delay)
            total += await collect_instrument(session, instrument, finnhub=finnhub)

    await session.commit()
    done(f"Collected {total} bars across {len(instruments)} instruments")
    return total


async def collect_entries(
    session: AsyncSession,
    entries: tuple[WatchlistEntry, ...],
) -> int:
    instruments = await seed_watchlist_entries(session, entries)
    settings = get_settings()
    delay = settings.collect_symbol_delay_seconds
    total = 0
    async with FinnhubClient() as finnhub:
        for i, instrument in enumerate(instruments):
            if i > 0 and delay > 0:
                await asyncio.sleep(delay)
            total += await collect_instrument(session, instrument, finnhub=finnhub)
    await session.commit()
    return total
