from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from openai import AsyncAzureOpenAI, AsyncOpenAI

from app.config import get_settings


def _is_foundry_openai_v1_endpoint(endpoint: str) -> bool:
    """True for Foundry resource endpoints that use /openai/v1 (not classic AOAI)."""
    lower = endpoint.lower()
    return (
        "services.ai.azure.com" in lower
        or "/openai/v1" in lower
        or "cognitiveservices.azure.com" in lower
    )


def _openai_v1_base_url(endpoint: str) -> str:
    """Normalize any Foundry URL to https://{host}/openai/v1."""
    raw = endpoint.strip()
    if not raw.startswith("http"):
        raw = f"https://{raw}"
    parsed = urlparse(raw.rstrip("/"))
    if not parsed.netloc:
        raise RuntimeError(f"Invalid AZURE_AI_FOUNDRY_ENDPOINT: {endpoint}")
    # If user already provided .../openai/v1, keep it
    path = parsed.path.rstrip("/")
    if path.endswith("/openai/v1"):
        return f"{parsed.scheme}://{parsed.netloc}{path}"
    return f"{parsed.scheme}://{parsed.netloc}/openai/v1"


def get_foundry_client() -> AsyncOpenAI | AsyncAzureOpenAI:
    settings = get_settings()
    if not settings.azure_ai_foundry_endpoint:
        raise RuntimeError("AZURE_AI_FOUNDRY_ENDPOINT is not configured")
    if not settings.azure_ai_foundry_api_key:
        raise RuntimeError("AZURE_AI_FOUNDRY_API_KEY is not configured")
    if not settings.azure_ai_foundry_deployment:
        raise RuntimeError("AZURE_AI_FOUNDRY_DEPLOYMENT is not configured")

    endpoint = settings.azure_ai_foundry_endpoint.rstrip("/")

    # Foundry project / resource endpoints (e.g. *.services.ai.azure.com)
    # use the OpenAI-compatible /openai/v1 surface — not the classic
    # /openai/deployments/{name}?api-version=... path.
    if _is_foundry_openai_v1_endpoint(endpoint):
        return AsyncOpenAI(
            base_url=_openai_v1_base_url(endpoint),
            api_key=settings.azure_ai_foundry_api_key,
        )

    return AsyncAzureOpenAI(
        azure_endpoint=endpoint,
        api_key=settings.azure_ai_foundry_api_key,
        api_version=settings.azure_api_version,
    )


async def chat_completion(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
    tool_choice: str | dict[str, Any] | None = "auto",
) -> Any:
    settings = get_settings()
    client = get_foundry_client()

    kwargs: dict[str, Any] = {
        "model": settings.azure_ai_foundry_deployment,
        "messages": messages,
    }
    if tools:
        kwargs["tools"] = tools
        if tool_choice is not None:
            kwargs["tool_choice"] = tool_choice

    return await client.chat.completions.create(**kwargs)
