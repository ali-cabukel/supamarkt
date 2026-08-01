"""Async database persistence via SQLAlchemy."""

from __future__ import annotations

from pathlib import Path

from supamarkt.console import info, warn
from supamarkt.db.engine import get_engine
from supamarkt.db.init_db import init_schema
from supamarkt.settings import Settings, get_settings


class Database:
    def __init__(self, path: Path | None = None) -> None:
        settings = get_settings()
        self.settings: Settings = settings
        self.path = path or settings.resolved_db_path
        self._engine = get_engine()

    async def close(self) -> None:
        pass

    async def init(self) -> Path:
        if self.settings.is_sqlite:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            existed = self.path.exists()
        else:
            existed = True

        await init_schema(self._engine)

        if self.settings.is_sqlite:
            if existed and self.path.exists():
                warn(f"Database already exists: [bold]{self.path}[/bold]")
                info("Schema up to date")
            else:
                info(f"Created database: [bold]{self.path}[/bold]")
        else:
            info("Postgres schema up to date")

        return self.path

    def ensure_exists(self) -> None:
        if self.settings.is_sqlite and not self.path.exists():
            raise FileNotFoundError(f"Database not found at {self.path}. Run: supamarkt init-db")
