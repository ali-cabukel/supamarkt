"""Click + Rich CLI for supamarkt."""

from __future__ import annotations

import asyncio

import click

from supamarkt.analytics.engine import run_analysis
from supamarkt.analytics.strategies import get_strategy, list_strategies
from supamarkt.collectors.intraday import collect_entries, collect_watchlist, seed_watchlist_entries
from supamarkt.console import done, info
from supamarkt.db.engine import get_session_maker
from supamarkt.db.store import Database
from supamarkt.watchlists.default import WatchlistEntry, get_watchlist


def _run(coro) -> None:
    asyncio.run(coro)


@click.group()
@click.version_option(package_name="supamarkt", prog_name="supamarkt")
def cli() -> None:
    """Supamarkt — global intraday data and trading signals."""


@cli.command("init-db")
def init_db() -> None:
    """Create or migrate the SQLite database schema."""

    async def _init() -> None:
        db = Database()
        try:
            await db.init()
        finally:
            await db.close()

    _run(_init())


@cli.command("collect-intraday")
@click.option(
    "--watchlist",
    "watchlist_name",
    default="default",
    show_default=True,
    help="Built-in watchlist name (US + UK + EU).",
)
@click.option("--symbol", default=None, help="Single symbol (requires --mic).")
@click.option("--mic", default=None, help="Exchange MIC, e.g. XNAS, XLON, XETR.")
@click.option("--finnhub-symbol", default=None, help="Override Finnhub ticker.")
@click.option("--yfinance-symbol", default=None, help="Override yfinance ticker.")
def collect_intraday(
    watchlist_name: str,
    symbol: str | None,
    mic: str | None,
    finnhub_symbol: str | None,
    yfinance_symbol: str | None,
) -> None:
    """Fetch 5m OHLCV from Finnhub (yfinance fallback) into SQLite."""

    async def _collect() -> None:
        db = Database()
        db.ensure_exists()
        maker = get_session_maker()
        async with maker() as session:
            if symbol and mic:
                fh = finnhub_symbol or symbol
                yf = yfinance_symbol or fh
                entry = WatchlistEntry(
                    symbol=symbol.upper(),
                    mic=mic.upper(),
                    name=symbol.upper(),
                    region="CUSTOM",
                    finnhub_symbol=fh,
                    yfinance_symbol=yf,
                    currency="USD",
                )
                total = await collect_entries(session, (entry,))
                done(f"Collected {total} bars for {symbol}:{mic}")
            else:
                await collect_watchlist(session, watchlist_name)

    _run(_collect())


@cli.command("analyze")
@click.option("--watchlist", "watchlist_name", default="default", show_default=True)
@click.option(
    "--strategy",
    "strategy_name",
    default="ema_trend_5m",
    show_default=True,
    help="Strategy to run over stored bars.",
)
def analyze(watchlist_name: str, strategy_name: str) -> None:
    """Compute buy/hold/sell signals from stored intraday bars."""

    async def _analyze() -> None:
        get_strategy(strategy_name)
        db = Database()
        db.ensure_exists()
        entries = get_watchlist(watchlist_name)
        maker = get_session_maker()
        async with maker() as session:
            instruments = await seed_watchlist_entries(session, entries)
            count = await run_analysis(session, instruments, strategy=strategy_name)
            await session.commit()
        done(f"Wrote {count} signals ({strategy_name}) for watchlist {watchlist_name!r}")

    _run(_analyze())


@cli.command("list-strategies")
def list_strategies_cmd() -> None:
    """Show available analysis strategies."""
    for name, description in list_strategies().items():
        info(f"[bold]{name}[/bold] — {description}")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
