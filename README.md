# supamarkt

Global intraday market data and rule-based trading signals (US, UK, EU).

## Quick start

```bash
cd backend
cp .env.template .env
uv sync
uv run supamarkt init-db
uv run supamarkt collect-intraday --watchlist default
uv run supamarkt analyze --watchlist default --strategy ema_trend_5m
uv run supamarkt-api
```

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

Research tool only — not investment advice.

## Database

SQLite (`backend/data/supamarkt.db`) by default, or **Postgres / Supabase** when `DATABASE_URL` is set:

```bash
DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
DATABASE_SCHEMA=supamarkt
```

## Docker

| Mode | Command | URLs |
| ---- | ------- | ---- |
| **Split** (default) | `docker compose up --build` | API `:8000`, UI `:3000` |
| **Split + Postgres** | `docker compose -f docker-compose.yml -f docker-compose.supabase.yml up --build` | API `:8000`, UI `:3000`, Studio `:54323` |
| **Bundled** (Cloud Run-style) | `docker compose -f docker-compose.bundled.yml up --build` | App `:8000` |
| **Bundled + Postgres** | `docker compose -f docker-compose.bundled.yml -f docker-compose.supabase.yml up --build` | App `:8000`, Studio `:54323` |

## Cloud Run

Push to `main` triggers `.github/workflows/deploy.yml` (bundled root `Dockerfile`).

| Workflow | Trigger | Purpose |
| -------- | ------- | ------- |
| `ci.yml` | PR / push to `main` | Ruff + pytest |
| `deploy.yml` | Push to `main` | Deploy Cloud Run service + `supamarkt-collect-analyze` job |
| `collect-intraday.yml` | Every 15m (US market hours), manual | Execute collect + analyze job |

Before first deploy:

1. Add `kurtc3b3/supamarkt` to GitHub WIF provider
2. Create GCP secrets: `SECRET` (maps to `SECRET_KEY`), `OPENAI_API_KEY`, `DATABASE_URL`
3. Deploy uses `DATABASE_SCHEMA=supamarkt`, `LLM_PROVIDER=openai`, `STATIC_DIR=/app/static`

The collection job runs:

```bash
supamarkt init-db
supamarkt collect-intraday --watchlist default
supamarkt analyze --watchlist default --strategy ema_trend_5m
```

## LLM (future-ready)

| `LLM_PROVIDER` | Behaviour |
|----------------|-----------|
| `auto` (default) | OpenAI when `OPENAI_API_KEY` is set, otherwise LM Studio |
| `openai` | Requires `OPENAI_API_KEY` |
| `lmstudio` | Local OpenAI-compatible server |
| `ollama` | Local Ollama server |

No LLM features ship yet; settings are wired for future AI summaries or signal explanations.

## Layout

- [`backend/`](backend/) — Python CLI + FastAPI API
- [`frontend/`](frontend/) — Next.js UI
