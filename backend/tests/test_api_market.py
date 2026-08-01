"""Tests for market data API routes."""

from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from supamarkt.api.app import create_app
from supamarkt.auth.deps import current_active_user
from supamarkt.auth.models import User


@pytest.fixture
def app(isolated_test_db):
    return create_app()


@pytest.fixture
def active_user() -> User:
    return User(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password="hashed",
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )


@pytest.mark.asyncio
async def test_instruments_requires_auth(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/instruments")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_signals_requires_auth(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/signals")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_signals_list_with_auth(app, active_user):
    async def override_user() -> User:
        return active_user

    app.dependency_overrides[current_active_user] = override_user
    transport = ASGITransport(app=app)
    try:
        async with app.router.lifespan_context(app):
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/signals?watchlist=default")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert body["watchlist"] == "default"
