"""MCP client that talks to the Flight Buddy stdio server."""

from __future__ import annotations

import json
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool

from app.config import get_settings

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SERVER = REPO_ROOT / "mcp-servers" / "flight-buddy" / "server.py"


def _server_params() -> StdioServerParameters:
    settings = get_settings()
    server_script = Path(settings.flight_mcp_server or DEFAULT_SERVER).resolve()
    if not server_script.exists():
        raise RuntimeError(f"Flight MCP server not found: {server_script}")

    env = os.environ.copy()
    if settings.serpapi_api_key:
        env["SERPAPI_API_KEY"] = settings.serpapi_api_key

    return StdioServerParameters(
        command=sys.executable,
        args=[str(server_script)],
        env=env,
        cwd=str(server_script.parent),
    )


@asynccontextmanager
async def flight_mcp_session() -> AsyncIterator[ClientSession]:
    """Open a short-lived MCP client session to the Flight Buddy server."""
    params = _server_params()
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


def mcp_tools_to_openai(tools: list[Tool]) -> list[dict[str, Any]]:
    """Convert MCP tool descriptors into OpenAI/Foundry function tools."""
    converted: list[dict[str, Any]] = []
    for tool in tools:
        schema = tool.inputSchema or {"type": "object", "properties": {}}
        converted.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or tool.name,
                    "parameters": schema,
                },
            }
        )
    return converted


def _content_to_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            text = getattr(block, "text", None)
            if text:
                parts.append(text)
            elif isinstance(block, dict) and block.get("text"):
                parts.append(str(block["text"]))
            else:
                parts.append(str(block))
        return "\n".join(parts)
    return str(content)


async def list_openai_tools(session: ClientSession) -> list[dict[str, Any]]:
    result = await session.list_tools()
    return mcp_tools_to_openai(list(result.tools or []))


async def call_mcp_tool(
    session: ClientSession,
    name: str,
    arguments: dict[str, Any],
) -> str:
    result = await session.call_tool(name, arguments=arguments)
    text = _content_to_text(result.content)
    if getattr(result, "isError", False):
        return json.dumps({"error": text or f"MCP tool {name} failed"})
    return text or json.dumps({"ok": True})
