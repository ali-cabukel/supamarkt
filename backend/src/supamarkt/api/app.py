"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from supamarkt.api.routers import instruments, signals
from supamarkt.api.static_web import mount_static_web
from supamarkt.auth.deps import auth_backend, fastapi_users
from supamarkt.auth.models import User  # noqa: F401 — register user table
from supamarkt.auth.schemas import UserCreate, UserRead, UserUpdate
from supamarkt.db.engine import dispose_engine, get_engine
from supamarkt.db.init_db import init_schema
from supamarkt.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_schema(get_engine())
    yield
    await dispose_engine()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="supamarkt API",
        description=(
            "Global intraday market data and trading signals (US, UK, EU). "
            f"{settings.data_disclaimer}"
        ),
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(
        fastapi_users.get_auth_router(auth_backend),
        prefix="/api/auth/jwt",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/api/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/api/users",
        tags=["users"],
    )
    app.include_router(instruments.router, prefix="/api")
    app.include_router(signals.router, prefix="/api")

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str | bool]:
        settings = get_settings()
        return {
            "status": "ok",
            "database": "postgres" if not settings.is_sqlite else "sqlite",
            "database_schema": settings.database_schema,
            "llm_provider": settings.llm_provider,
            "llm_active": settings.resolved_llm_provider(),
            "openai_configured": settings.has_openai_api_key(),
            "openai_model": settings.openai_model,
            "lmstudio_base_url": settings.lmstudio_base_url,
            "ollama_base_url": settings.ollama_base_url,
        }

    mount_static_web(app, settings.static_dir_path)

    return app
