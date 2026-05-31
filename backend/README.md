# backend

Python package for supamarkt — async persistence, JWT auth, and FastAPI.

## Setup

```bash
cd backend
cp .env.template .env
uv sync
uv run supamarkt init-db
```

Configuration: `src/supamarkt/settings.py` (pydantic-settings).

## CLI (`supamarkt`)

```bash
uv run supamarkt init-db
uv run supamarkt-api
```

## API (`supamarkt-api`)

REST API on `http://127.0.0.1:8000` (see `/docs` for OpenAPI).

| Prefix | Description |
|--------|-------------|
| `/auth` | Register (`POST /auth/register`) |
| `/auth/jwt` | Login (`POST /auth/jwt/login`) |
| `/users` | Current user profile |
| `/health` | Health check |

## Database

SQLite at `backend/data/supamarkt.db` (override with `DB_PATH` in `.env`).

## Development

```bash
uv sync --group dev
uv run pytest
uv run ruff check src tests
uv run ruff format src tests
```

Run from the `backend/` directory.
