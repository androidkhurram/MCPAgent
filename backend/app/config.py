from pathlib import Path

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    azure_ai_foundry_endpoint: str = ""
    azure_ai_foundry_api_key: str = ""
    azure_ai_foundry_deployment: str = ""
    azure_api_version: str = "2024-08-01-preview"
    serper_api_key: str = ""
    serpapi_api_key: str = ""
    flight_mcp_server: str = ""
    cors_origins: str = "http://localhost:5173"
    max_tool_rounds: int = 3

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
