"""
Centralized configuration for the Agent Control Plane.

All environment variables and settings are managed here.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        app_env: The application environment (development, staging, production).
        log_level: Logging level for the application.
        llm_provider: The LLM provider to use (e.g., openai, azure, anthropic).
        llm_model: The specific model to use from the provider.
        openai_api_key: API key for OpenAI (if using OpenAI provider).
        openai_api_base: Base URL for OpenAI-compatible APIs.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application settings
    app_env: Literal["development", "staging", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # LLM settings
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"

    # OpenAI settings (optional - only needed if using OpenAI provider)
    openai_api_key: str | None = None
    openai_api_base: str | None = None

    # ERPNext settings
    erpnext_url: str | None = None
    erpnext_api_key: str | None = None
    erpnext_api_secret: str | None = None

    # Future: Add more provider-specific settings as needed
    # anthropic_api_key: str | None = None
    # azure_openai_endpoint: str | None = None
    # azure_openai_api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        The application settings.
    """
    return Settings()


# Global settings instance
settings = get_settings()

