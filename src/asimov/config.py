from __future__ import annotations

from pydantic import BaseModel, Field
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
    langgraph_api_key: str | None = Field(default=None, validation_alias="LANGGRAPH_API_KEY")
    langgraph_project: str = Field(default="asimov-level2", validation_alias="LANGGRAPH_PROJECT")
    langgraph_endpoint: str = Field(default="https://api.smith.langchain.com", validation_alias="LANGGRAPH_ENDPOINT")
    langgraph_tracing_enabled: bool = Field(default=False, validation_alias="LANGGRAPH_TRACING_ENABLED")

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
