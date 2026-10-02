"""Application configuration, loaded from environment variables / .env.

The Azure AI Foundry variables here use the SAME names that
FoundryChatClient reads, so the client and the app stay in sync.
"""
import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("MEDICAL_ASSISTANT_ENV_FILE", str(Path(__file__).with_name(".env"))),
        env_file_encoding="utf-8", extra="ignore"
    )

    # --- Azure AI Foundry ---
    # e.g. https://<resource>.services.ai.azure.com/api/projects/<project>
    azure_ai_project_endpoint: str = ""
    azure_ai_model_deployment_name: str = "gpt-5.4-nano"
    azure_ai_search_connection_name: str = ""
    azure_ai_search_endpoint: str = "https://umc-hackathon-devbox-fiq-search.search.windows.net"
    azure_ai_search_index_name: str = "who"
    # Optional local service-principal auth. If unset, the backend uses Azure CLI.
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    azure_client_secret: SecretStr | None = None

    @property
    def has_service_principal(self) -> bool:
        return bool(self.azure_tenant_id and self.azure_client_id and self.azure_client_secret)

    # --- API ---
    # Comma-separated list of allowed frontend origins.
    cors_allow_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    orchestration_timeout_seconds: int = Field(default=300, ge=1, le=900)

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
