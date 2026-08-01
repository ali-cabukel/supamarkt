"""SQLAlchemy ORM models for market data and signals."""

from __future__ import annotations

from sqlalchemy import (
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from supamarkt.db.schema import metadata


class Base(DeclarativeBase):
    metadata = metadata


class Instrument(Base):
    __tablename__ = "instruments"
    __table_args__ = (UniqueConstraint("symbol", "mic", name="uq_instruments_symbol_mic"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String, nullable=False)
    mic: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    region: Mapped[str] = mapped_column(String, nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="USD")

    providers: Mapped[list[InstrumentProvider]] = relationship(
        back_populates="instrument",
        lazy="raise",
    )
    bars: Mapped[list[PriceBar]] = relationship(back_populates="instrument", lazy="raise")
    signals: Mapped[list[Signal]] = relationship(back_populates="instrument", lazy="raise")


class InstrumentProvider(Base):
    __tablename__ = "instrument_providers"
    __table_args__ = (
        UniqueConstraint(
            "instrument_id",
            "provider",
            name="uq_instrument_providers_instrument_provider",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String, nullable=False)
    provider_symbol: Mapped[str] = mapped_column(String, nullable=False)

    instrument: Mapped[Instrument] = relationship(back_populates="providers")


class PriceBar(Base):
    __tablename__ = "price_bars"
    __table_args__ = (
        UniqueConstraint(
            "instrument_id",
            "bar_ts",
            "interval",
            name="uq_price_bars_instrument_ts_interval",
        ),
        Index("idx_price_bars_instrument_interval", "instrument_id", "interval"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), nullable=False)
    bar_ts: Mapped[str] = mapped_column(String, nullable=False)
    interval: Mapped[str] = mapped_column(String, nullable=False)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)

    instrument: Mapped[Instrument] = relationship(back_populates="bars")


class Signal(Base):
    __tablename__ = "signals"
    __table_args__ = (
        UniqueConstraint(
            "instrument_id",
            "strategy",
            name="uq_signals_instrument_strategy",
        ),
        Index("idx_signals_computed_at", "computed_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), nullable=False)
    strategy: Mapped[str] = mapped_column(String, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    bar_ts: Mapped[str] = mapped_column(String, nullable=False)
    reasons: Mapped[str] = mapped_column(Text, nullable=False)
    computed_at: Mapped[str] = mapped_column(
        String, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    instrument: Mapped[Instrument] = relationship(back_populates="signals")


class SyncLog(Base):
    __tablename__ = "sync_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    entity_ref: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    synced_at: Mapped[str] = mapped_column(String, nullable=False)
