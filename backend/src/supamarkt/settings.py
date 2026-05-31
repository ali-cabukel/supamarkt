"""Application settings loaded from environment and .env file."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]

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

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    @property
    def resolved_db_path(self) -> Path:
        return self.db_path or BACKEND_ROOT / "data" / "supamarkt.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
