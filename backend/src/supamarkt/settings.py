"""Application settings loaded from environment and .env file."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]

LlmProviderSetting = Literal["auto", "openai", "lmstudio", "ollama"]

DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173,"
    "http://127.0.0.1:5173,"
    "http://localhost:3000,"
    "http://127.0.0.1:3000,"
    "http://localhost:8000,"
    "http://127.0.0.1:8000"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    db_path: Path | None = Field(default=None, validation_alias="DB_PATH")
    database_url: str | None = Field(default=None, validation_alias="DATABASE_URL")
    database_schema: str = Field(default="", validation_alias="DATABASE_SCHEMA")
    secret_key: SecretStr = Field(
        default=SecretStr("change-me-in-production"),
        validation_alias="SECRET_KEY",
    )
    jwt_lifetime_seconds: int = Field(default=3600, validation_alias="JWT_LIFETIME_SECONDS")
    cors_origins_raw: str = Field(
        default=DEFAULT_CORS_ORIGINS,
        validation_alias="CORS_ORIGINS",
    )
    api_host: str = Field(default="127.0.0.1", validation_alias="API_HOST")
    api_port: int = Field(default=8000, validation_alias="API_PORT")
    api_reload: bool = Field(default=False, validation_alias="API_RELOAD")
    static_dir: str | None = Field(default=None, validation_alias="STATIC_DIR")
    llm_provider: LlmProviderSetting = Field(default="auto", validation_alias="LLM_PROVIDER")
    openai_api_key: SecretStr | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", validation_alias="OPENAI_MODEL")
    lmstudio_base_url: str = Field(
        default="http://localhost:1234/v1",
        validation_alias="LMSTUDIO_BASE_URL",
    )
    lmstudio_model: str = Field(default="local-model", validation_alias="LMSTUDIO_MODEL")
    lmstudio_api_key: SecretStr = Field(
        default=SecretStr("lm-studio"),
        validation_alias="LMSTUDIO_API_KEY",
    )
    ollama_base_url: str = Field(
        default="http://127.0.0.1:11434",
        validation_alias="OLLAMA_BASE_URL",
    )
    ollama_model: str = Field(default="llama3.2", validation_alias="OLLAMA_MODEL")
    finnhub_api_key: SecretStr = Field(default=SecretStr(""), validation_alias="FINNHUB_API_KEY")
    data_provider_primary: str = Field(
        default="yfinance",
        validation_alias="DATA_PROVIDER_PRIMARY",
        description="Primary OHLCV source: yfinance (free intraday) or finnhub (paid candles).",
    )
    intraday_interval: str = Field(default="5m", validation_alias="INTRADAY_INTERVAL")
    collect_lookback_days: int = Field(default=5, validation_alias="COLLECT_LOOKBACK_DAYS")
    collect_symbol_delay_seconds: float = Field(
        default=1.0,
        validation_alias="COLLECT_SYMBOL_DELAY_SECONDS",
    )
    data_disclaimer: str = Field(
        default=(
            "Research tool only — not investment advice. "
            "Free-tier data may be delayed or incomplete."
        ),
        validation_alias="DATA_DISCLAIMER",
    )

    @field_validator("db_path", mode="before")
    @classmethod
    def empty_db_path_is_none(cls, value: object) -> Path | None:
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        path = Path(value) if not isinstance(value, Path) else value
        if path == Path("."):
            return None
        return path

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        url = str(value).strip()
        if not url:
            return None
        if url.startswith("postgresql://"):
            return "postgresql+asyncpg://" + url.removeprefix("postgresql://")
        if url.startswith("postgres://"):
            return "postgresql+asyncpg://" + url.removeprefix("postgres://")
        return url

    @field_validator("database_schema", mode="before")
    @classmethod
    def normalize_database_schema(cls, value: str | None) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @field_validator("static_dir", mode="before")
    @classmethod
    def empty_static_dir_is_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value.strip()

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    @property
    def resolved_db_path(self) -> Path:
        path = self.db_path or BACKEND_ROOT / "data" / "supamarkt.db"
        if not path.is_absolute():
            path = BACKEND_ROOT / path
        return path

    @property
    def is_sqlite(self) -> bool:
        return self.resolved_database_url.startswith("sqlite")

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return f"sqlite+aiosqlite:///{self.resolved_db_path}"

    @property
    def static_dir_path(self) -> Path | None:
        if self.static_dir is None:
            return None
        return Path(self.static_dir)

    def has_openai_api_key(self) -> bool:
        if self.openai_api_key is None:
            return False
        return bool(self.openai_api_key.get_secret_value().strip())

    def resolved_llm_provider(self) -> str | None:
        if self.llm_provider == "openai":
            return "openai" if self.has_openai_api_key() else None
        if self.llm_provider == "lmstudio":
            return "lmstudio"
        if self.llm_provider == "ollama":
            return "ollama"
        if self.has_openai_api_key():
            return "openai"
        return "lmstudio"


@lru_cache
def get_settings() -> Settings:
    return Settings()
