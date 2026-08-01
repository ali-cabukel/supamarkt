"""Tests for core API endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from supamarkt.api.app import create_app


@pytest.fixture
def app(isolated_test_db):
    return create_app()


@pytest.mark.asyncio
async def test_health_endpoint(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "sqlite"
