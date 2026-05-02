from __future__ import annotations

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ASIMOV Backend"
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"
    redis_url: str | None = None
    postgres_dsn: str | None = None
    ollama_url: str | None = None

    model_config = SettingsConfigDict(
        env_prefix="ASIMOV_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class DependencyState(BaseModel):
    ok: bool
    detail: str


settings = Settings()
