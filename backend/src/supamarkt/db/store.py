"""Async SQLite persistence via SQLAlchemy."""

from __future__ import annotations

from pathlib import Path

from supamarkt.console import info
from supamarkt.db.engine import get_engine
from supamarkt.db.models import Base
from supamarkt.settings import get_settings


class Database:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or get_settings().resolved_db_path
        self._engine = get_engine()

    async def close(self) -> None:
        pass

    async def init(self) -> Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        existed = self.path.exists()
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        if existed:
            info(f"Database schema up to date: [bold]{self.path}[/bold]")
        else:
            info(f"Created database: [bold]{self.path}[/bold]")
        return self.path

    def ensure_exists(self) -> None:
        if not self.path.exists():
            raise FileNotFoundError(f"Database not found at {self.path}. Run: supamarkt init-db")
