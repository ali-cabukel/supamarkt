"""Click + Rich CLI for supamarkt."""

from __future__ import annotations

import asyncio

import click

from supamarkt.db.store import Database


def _run(coro) -> None:
    asyncio.run(coro)


@click.group()
@click.version_option(package_name="supamarkt", prog_name="supamarkt")
def cli() -> None:
    """Supamarkt backend CLI."""


@cli.command("init-db")
def init_db() -> None:
    """Create the SQLite database from the SQLAlchemy schema."""

    async def _init() -> None:
        db = Database()
        try:
            await db.init()
        finally:
            await db.close()

    _run(_init())


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
