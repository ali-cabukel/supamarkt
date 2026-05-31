"""Built-in watchlists for US, UK, and EU."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WatchlistEntry:
    symbol: str
    mic: str
    name: str
    region: str
    finnhub_symbol: str
    yfinance_symbol: str
    currency: str


DEFAULT_WATCHLIST: tuple[WatchlistEntry, ...] = (
    WatchlistEntry("AAPL", "XNAS", "Apple Inc.", "US", "AAPL", "AAPL", "USD"),
    WatchlistEntry("MSFT", "XNAS", "Microsoft Corp.", "US", "MSFT", "MSFT", "USD"),
    WatchlistEntry("VOD", "XLON", "Vodafone Group", "UK", "VOD.L", "VOD.L", "GBP"),
    WatchlistEntry("BP", "XLON", "BP plc", "UK", "BP.L", "BP.L", "GBP"),
    WatchlistEntry("SAP", "XETR", "SAP SE", "EU", "SAP.DE", "SAP.DE", "EUR"),
    WatchlistEntry("ASML", "XAMS", "ASML Holding", "EU", "ASML.AS", "ASML.AS", "EUR"),
)

WATCHLISTS: dict[str, tuple[WatchlistEntry, ...]] = {
    "default": DEFAULT_WATCHLIST,
}


def get_watchlist(name: str) -> tuple[WatchlistEntry, ...]:
    entries = WATCHLISTS.get(name)
    if entries is None:
        known = ", ".join(sorted(WATCHLISTS))
        raise ValueError(f"Unknown watchlist {name!r}. Choose from: {known}")
    return entries
