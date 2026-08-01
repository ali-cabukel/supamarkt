# backend

Python package for supamarkt — global intraday market data (US, UK, EU), rule-based signals, and FastAPI.

**Not investment advice.** Free-tier data may be delayed or incomplete.

## Setup

```bash
cd backend
cp .env.template .env   # set FINNHUB_API_KEY
uv sync
uv run supamarkt init-db
```

Register a free key at [Finnhub](https://finnhub.io/register).

## CLI

```bash
# Default watchlist: AAPL, MSFT (US), VOD, BP (UK), SAP, ASML (EU)
uv run supamarkt collect-intraday
uv run supamarkt collect-intraday --watchlist default

# Single symbol
uv run supamarkt collect-intraday --symbol AAPL --mic XNAS

# Signals from stored 5m bars
uv run supamarkt analyze --watchlist default --strategy ema_trend_5m
uv run supamarkt list-strategies
```

## API (`supamarkt-api`)

```bash
uv run supamarkt-api
# http://127.0.0.1:8000/docs
```

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/instruments` | List/search instruments (`?region=US`) |
| GET | `/api/instruments/{id}/bars` | 5m OHLCV history |
| GET | `/api/signals` | Latest signals (`?watchlist=default&strategy=ema_trend_5m`) |

All market routes require JWT (`/api/auth/register`, `/api/auth/jwt/login`).

## Database

SQLite by default, or Postgres / Supabase via `DATABASE_URL` and `DATABASE_SCHEMA=supamarkt`. See root [README.md](../README.md) for Docker and Cloud Run.

## Default watchlist

| Symbol | MIC | Region |
|--------|-----|--------|
| AAPL | XNAS | US |
| MSFT | XNAS | US |
| VOD | XLON | UK |
| BP | XLON | UK |
| SAP | XETR | EU |
| ASML | XAMS | EU |

**yfinance** is the default for 5m OHLCV (free). Finnhub `/stock/candle` requires a
[paid market-data plan](https://finnhub.io/pricing-stock-api-market-data) — free keys
get 403. Set `DATA_PROVIDER_PRIMARY=finnhub` only if you subscribe.

## Development

```bash
uv sync --group dev
uv run pytest
uv run ruff check src tests
```

## Settings

| Variable | Default |
|----------|---------|
| `FINNHUB_API_KEY` | *(required for collection)* |
| `INTRADAY_INTERVAL` | `5m` |
| `COLLECT_LOOKBACK_DAYS` | `5` |
| `COLLECT_SYMBOL_DELAY_SECONDS` | `1` (rate-limit friendly) |
| `DB_PATH` | `backend/data/supamarkt.db` |
