"""Application configuration, loaded from environment variables / .env.

The Azure AI Foundry variables here use the SAME names that
FoundryChatClient reads, so the client and the app stay in sync.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- Azure AI Foundry ---
    # e.g. https://<resource>.services.ai.azure.com/api/projects/<project>
    azure_ai_project_endpoint: str = ""
    azure_ai_model_deployment_name: str = "gpt-5.4-mini"

    # --- API ---
    # Comma-separated list of allowed frontend origins.
    cors_allow_origins: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
