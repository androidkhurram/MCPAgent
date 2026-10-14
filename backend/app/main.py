from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.agent.flight_orchestrator import run_flight_agent, run_flight_agent_events
from app.agent.orchestrator import run_agent, run_agent_events
from app.config import get_settings

app = FastAPI(title="Samiaa Learning Agents", version="1.1.0")

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list or ["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)


class HotelCard(BaseModel):
    name: str
    price_hint: str | None = None
    rating: str | None = None
    review_count: int | None = None
    address: str | None = None
    why: str = ""
    link: str = ""
    snippet: str = ""


class TraceEvent(BaseModel):
    type: str = "trace"
    step: str
    message: str
    detail: dict[str, Any] = Field(default_factory=dict)
    ts: float | None = None


class FlightCard(BaseModel):
    airline: str
    flight_numbers: str = ""
    from_airport: str = ""
    to_airport: str = ""
    departure_time: str | None = None
    arrival_time: str | None = None
    duration: str | None = None
    stops: int | None = None
    price: str | None = None
    why: str = ""
    link: str = ""


class ChatResponse(BaseModel):
    message: str
    hotels: list[HotelCard] = Field(default_factory=list)
    status: str | None = None
    traces: list[TraceEvent] = Field(default_factory=list)


class FlightChatResponse(BaseModel):
    message: str
    flights: list[FlightCard] = Field(default_factory=list)
    status: str | None = None
    traces: list[TraceEvent] = Field(default_factory=list)


def _safe_messages(request: ChatRequest) -> list[dict[str, str]]:
    safe_messages = [
        {"role": m.role, "content": m.content}
        for m in request.messages
        if m.role in ("user", "assistant")
    ]
    if not safe_messages:
        raise HTTPException(status_code=400, detail="At least one user message is required")
    return safe_messages


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/flights/mcp/tools")
async def flight_mcp_tools() -> dict[str, Any]:
    """List tools/resources from the Flight Buddy MCP server (for learning UI)."""
    from app.mcp.flight_client import flight_mcp_session, list_openai_tools

    try:
        async with flight_mcp_session() as session:
            tools = await list_openai_tools(session)
            resources = await session.list_resources()
            prompts = await session.list_prompts()
            return {
                "host": "FastAPI web backend",
                "client": "MCP ClientSession (stdio)",
                "server": "flight-buddy",
                "tools": [
                    {
                        "name": t["function"]["name"],
                        "description": t["function"].get("description") or "",
                        "parameters": t["function"].get("parameters") or {},
                    }
                    for t in tools
                ],
                "resources": [
                    {"uri": str(r.uri), "name": r.name, "description": r.description or ""}
                    for r in (resources.resources or [])
                ],
                "prompts": [
                    {"name": p.name, "description": p.description or ""}
                    for p in (prompts.prompts or [])
                ],
            }
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"MCP discovery failed: {exc}") from exc


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    safe_messages = _safe_messages(request)

    try:
        result = await run_agent(safe_messages)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=502,
            detail=f"Agent request failed: {exc}",
        ) from exc

    return ChatResponse(
        message=result.get("message") or "",
        hotels=result.get("hotels") or [],
        status=result.get("status"),
        traces=result.get("traces") or [],
    )


async def _sse_chat(messages: list[dict[str, str]]) -> AsyncIterator[str]:
    try:
        async for event in run_agent_events(messages):
            yield f"data: {json.dumps(event, default=str)}\n\n"
    except Exception as exc:  # noqa: BLE001
        payload = {"type": "error", "message": f"Agent request failed: {exc}"}
        yield f"data: {json.dumps(payload)}\n\n"
    yield "data: {\"type\": \"stream_end\"}\n\n"


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    safe_messages = _safe_messages(request)
    return StreamingResponse(
        _sse_chat(safe_messages),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/flights/chat", response_model=FlightChatResponse)
async def flight_chat(request: ChatRequest) -> FlightChatResponse:
    safe_messages = _safe_messages(request)
    try:
        result = await run_flight_agent(safe_messages)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=502,
            detail=f"Flight agent failed: {exc}",
        ) from exc

    return FlightChatResponse(
        message=result.get("message") or "",
        flights=result.get("flights") or [],
        status=result.get("status"),
        traces=result.get("traces") or [],
    )


async def _sse_flights(messages: list[dict[str, str]]) -> AsyncIterator[str]:
    try:
        async for event in run_flight_agent_events(messages):
            yield f"data: {json.dumps(event, default=str)}\n\n"
    except Exception as exc:  # noqa: BLE001
        payload = {"type": "error", "message": f"Flight agent failed: {exc}"}
        yield f"data: {json.dumps(payload)}\n\n"
    yield 'data: {"type": "stream_end"}\n\n'


@app.post("/api/flights/chat/stream")
async def flight_chat_stream(request: ChatRequest) -> StreamingResponse:
    safe_messages = _safe_messages(request)
    return StreamingResponse(
        _sse_flights(safe_messages),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
