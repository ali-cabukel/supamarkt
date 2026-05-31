"""Trading signal routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from supamarkt.api.schemas import PaginatedSignals, SignalOut
from supamarkt.auth.deps import current_active_user
from supamarkt.auth.models import User
from supamarkt.db.engine import get_async_session
from supamarkt.db.repository import list_signals
from supamarkt.settings import get_settings
from supamarkt.watchlists.default import get_watchlist

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("", response_model=PaginatedSignals)
async def get_signals(
    watchlist: str | None = Query(None, description="Filter to a built-in watchlist name"),
    strategy: str | None = Query(None, description="Filter by strategy id"),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
) -> PaginatedSignals:
    settings = get_settings()
    watchlist_symbols: set[tuple[str, str]] | None = None
    if watchlist:
        entries = get_watchlist(watchlist)
        watchlist_symbols = {(entry.symbol, entry.mic) for entry in entries}

    rows = await list_signals(
        session,
        watchlist_symbols=watchlist_symbols,
        strategy=strategy,
        limit=limit,
    )

    items = [
        SignalOut(
            id=signal.id,
            instrument_id=instrument.id,
            symbol=instrument.symbol,
            mic=instrument.mic,
            name=instrument.name,
            region=instrument.region,
            strategy=signal.strategy,
            action=signal.action,
            confidence=signal.confidence,
            bar_ts=signal.bar_ts,
            reasons=signal.reasons,
            computed_at=signal.computed_at,
            disclaimer=settings.data_disclaimer,
        )
        for signal, instrument in rows
    ]

    return PaginatedSignals(
        items=items,
        limit=limit,
        watchlist=watchlist,
        strategy=strategy,
    )
