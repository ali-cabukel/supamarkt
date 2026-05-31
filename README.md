# supamarkt

## Backend

Python API and services live in [`backend/`](backend/). See [backend/README.md](backend/README.md) for setup:

```bash
cd backend
cp .env.template .env   # add FINNHUB_API_KEY
uv sync
uv run supamarkt init-db
uv run supamarkt collect-intraday
uv run supamarkt analyze --strategy ema_trend_5m
uv run supamarkt-api
```

Research tool only — not investment advice. See [backend/README.md](backend/README.md).

## Frontend

Next.js app in [`frontend/`](frontend/):

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

Open http://localhost:3000 (API on http://127.0.0.1:8000).
