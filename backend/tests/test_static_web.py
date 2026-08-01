"""Tests for static web fallback routing."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from supamarkt.api.static_web import mount_static_web


def test_instrument_detail_path_serves_export_shell(tmp_path: Path) -> None:
    static_dir = tmp_path / "static"
    detail_page = static_dir / "instruments" / "0.html"
    detail_page.parent.mkdir(parents=True)
    detail_page.write_text("<html><body>instrument shell</body></html>", encoding="utf-8")

    app = FastAPI()
    mount_static_web(app, static_dir)
    client = TestClient(app)

    response = client.get("/instruments/42")

    assert response.status_code == 200
    assert "instrument shell" in response.text
