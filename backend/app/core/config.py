"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the Pigzel backend."""

    model_config = SettingsConfigDict(
        env_prefix="PIGZEL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Pigzel"
    app_version: str = "0.1.0"
    env: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"

    # Model Gateway — LLM configuration
    llm_provider: str = Field(default="mock", description="Configured LLM provider name.")
    llm_model: str = Field(default="mock-creative-v1", description="Default LLM model identifier.")
    llm_base_url: str | None = None
    llm_api_key: SecretStr | None = None
    llm_timeout_seconds: float = Field(default=60.0, gt=0)


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
