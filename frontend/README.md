# frontend

Next.js dashboard for supamarkt — JWT auth, trading signals, and instrument charts.

## Setup

```bash
cd frontend
cp .env.local.example .env.local
npm install
```

Start the API first (`cd ../backend && uv run supamarkt-api`).

## Development

```bash
npm run dev
```

Open http://localhost:3000

## Pages

| Route | Description |
|-------|-------------|
| `/` | Landing |
| `/login`, `/register` | JWT auth |
| `/signals` | Buy / hold / sell table (default watchlist) |
| `/instruments` | Symbol list with region filter |
| `/instruments/[id]` | 5m price sparkline + recent bars |

## Build

```bash
npm run build
npm start
```
