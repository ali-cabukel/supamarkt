from supamarkt.settings import DEFAULT_CORS_ORIGINS, Settings


def test_default_cors_origins_include_vite(monkeypatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    settings = Settings()
    assert "http://localhost:5173" in settings.cors_origins


def test_finnhub_key_from_env(monkeypatch):
    monkeypatch.setenv("FINNHUB_API_KEY", "secret-test-key")
    settings = Settings(_env_file=None)
    assert settings.finnhub_api_key.get_secret_value() == "secret-test-key"


def test_intraday_defaults(monkeypatch):
    monkeypatch.delenv("INTRADAY_INTERVAL", raising=False)
    monkeypatch.delenv("COLLECT_LOOKBACK_DAYS", raising=False)
    settings = Settings(_env_file=None)
    assert settings.intraday_interval == "5m"
    assert settings.collect_lookback_days == 5


def test_default_cors_origins_constant_matches_settings_default():
    settings = Settings(_env_file=None)
    assert settings.cors_origins_raw == DEFAULT_CORS_ORIGINS
