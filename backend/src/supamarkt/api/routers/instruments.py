"""Instrument and price bar routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from supamarkt.api.schemas import PaginatedBars, PaginatedInstruments, PriceBarOut
from supamarkt.auth.deps import current_active_user
from supamarkt.auth.models import User
from supamarkt.db.engine import get_async_session
from supamarkt.db.repository import fetch_price_bars, get_instrument_by_id, list_instruments
from supamarkt.settings import get_settings

router = APIRouter(prefix="/instruments", tags=["instruments"])


@router.get("", response_model=PaginatedInstruments)
async def get_instruments(
    q: str | None = Query(None, description="Search symbol, name, or MIC"),
    region: str | None = Query(None, description="Filter by region: US, UK, EU"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
) -> PaginatedInstruments:
    items = await list_instruments(session, region=region, q=q, limit=limit, offset=offset)
    return PaginatedInstruments(items=items, limit=limit, offset=offset)


@router.get("/{instrument_id}/bars", response_model=PaginatedBars)
async def get_instrument_bars(
    instrument_id: int,
    interval: str | None = Query(None, description="Bar interval (default from settings)"),
    limit: int = Query(200, ge=1, le=500),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
) -> PaginatedBars:
    instrument = await get_instrument_by_id(session, instrument_id)
    if instrument is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instrument not found")

    settings = get_settings()
    resolved_interval = interval or settings.intraday_interval
    bars = await fetch_price_bars(
        session,
        instrument_id,
        interval=resolved_interval,
        limit=limit,
    )
    return PaginatedBars(
        instrument_id=instrument.id,
        symbol=instrument.symbol,
        mic=instrument.mic,
        interval=resolved_interval,
        items=[PriceBarOut.model_validate(row) for row in bars],
    )
