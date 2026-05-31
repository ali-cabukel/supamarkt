# supamarkt

## Backend

Python API and services live in [`backend/`](backend/). See [backend/README.md](backend/README.md) for setup:

```bash
cd backend
cp .env.template .env
uv sync
uv run supamarkt init-db
uv run supamarkt-api
```
