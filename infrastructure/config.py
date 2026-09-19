"""Configuration is explicit, environment-driven, and free of provider-specific logic."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from contracts.reasoning import ProviderMode


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CROSSLENS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = Field(default=8000, ge=1, le=65535)

    postgres_dsn: str = "postgresql://localhost:5432/crosslens"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: SecretStr | None = None
    chroma_host: str = "localhost"
    chroma_port: int = Field(default=8000, ge=1, le=65535)
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    file_store_root: Path = Path("data")
    max_upload_bytes: int = Field(default=50 * 1024 * 1024, gt=0)

    llm_provider: ProviderMode = ProviderMode.DISABLED
    vlm_provider: ProviderMode = ProviderMode.DISABLED
    embedding_provider: ProviderMode = ProviderMode.DISABLED
    llm_model: str | None = None
    vlm_model: str | None = None
    embedding_model: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()

