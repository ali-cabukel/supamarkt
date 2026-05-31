"""Pydantic schemas for market data API."""

from __future__ import annotations

import json

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InstrumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    mic: str
    name: str
    region: str
    currency: str


class PriceBarOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bar_ts: str
    interval: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class SignalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    instrument_id: int
    symbol: str
    mic: str
    name: str
    region: str
    strategy: str
    action: str
    confidence: float
    bar_ts: str
    reasons: list[str]
    computed_at: str
    disclaimer: str = Field(description="Research disclaimer")

    @field_validator("reasons", mode="before")
    @classmethod
    def parse_reasons(cls, value: object) -> list[str]:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        return []


class PaginatedInstruments(BaseModel):
    items: list[InstrumentOut]
    limit: int
    offset: int


class PaginatedBars(BaseModel):
    instrument_id: int
    symbol: str
    mic: str
    interval: str
    items: list[PriceBarOut]


class PaginatedSignals(BaseModel):
    items: list[SignalOut]
    limit: int
    watchlist: str | None = None
    strategy: str | None = None
