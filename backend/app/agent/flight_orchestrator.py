"""Web-host agent loop: Foundry LLM + MCP Flight Buddy client."""

from __future__ import annotations

import json
import re
import time
from collections.abc import AsyncIterator
from typing import Any

from app.agent.flight_prompts import SYSTEM_PROMPT
from app.config import get_settings
from app.mcp.flight_client import call_mcp_tool, flight_mcp_session, list_openai_tools
from app.services.foundry import chat_completion

FLIGHTS_JSON_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE)


def _message_to_dict(message: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "role": message.role,
        "content": message.content,
    }
    if getattr(message, "tool_calls", None):
        data["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in message.tool_calls
        ]
    return data


def _parse_flights(content: str | None) -> tuple[str, list[dict[str, Any]]]:
    if not content:
        return "", []

    flights: list[dict[str, Any]] = []
    display = content
    match = FLIGHTS_JSON_RE.search(content)
    if match:
        try:
            payload = json.loads(match.group(1))
            raw = payload.get("flights") or []
            for item in raw:
                if not isinstance(item, dict):
                    continue
                stops = item.get("stops")
                if isinstance(stops, str) and stops.isdigit():
                    stops = int(stops)
                elif not isinstance(stops, int):
                    stops = None
                flights.append(
                    {
                        "airline": item.get("airline") or "Airline",
                        "flight_numbers": item.get("flight_numbers") or "",
                        "from_airport": item.get("from") or item.get("from_airport") or "",
                        "to_airport": item.get("to") or item.get("to_airport") or "",
                        "departure_time": item.get("departure_time"),
                        "arrival_time": item.get("arrival_time"),
                        "duration": item.get("duration"),
                        "stops": stops,
                        "price": item.get("price"),
                        "why": item.get("why") or "",
                        "link": item.get("link") or "",
                    }
                )
        except json.JSONDecodeError:
            flights = []
        display = (content[: match.start()] + content[match.end() :]).strip()

    return display, flights


def _truncate(text: str, limit: int = 400) -> str:
    text = text or ""
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _tool_result_summary(raw: str) -> dict[str, Any]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {"preview": _truncate(raw)}

    if "error" in payload:
        return {"error": payload.get("error")}

    ranked = payload.get("ranked") or []
    offers = payload.get("offers") or ranked
    winner = payload.get("winner")
    titles = []
    for offer in offers[:5]:
        if not isinstance(offer, dict):
            continue
        airlines = offer.get("airlines") or []
        label = ", ".join(airlines) if airlines else offer.get("airline") or "Flight"
        price = offer.get("price_label") or offer.get("price")
        titles.append(f"{label} {price or ''}".strip())

    return {
        "offer_count": payload.get("offer_count") or payload.get("ranked_count") or len(offers),
        "prefer": payload.get("prefer"),
        "winner": (
            {
                "airlines": (winner or {}).get("airlines"),
                "price": (winner or {}).get("price_label") or (winner or {}).get("price"),
                "duration": (winner or {}).get("duration_label"),
                "stops": (winner or {}).get("stops"),
            }
            if isinstance(winner, dict)
            else None
        ),
        "top": titles,
        "query": payload.get("query"),
        "summary": payload.get("summary"),
    }


def _trace(step: str, message: str, *, detail: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "type": "trace",
        "step": step,
        "message": message,
        "detail": detail or {},
        "ts": time.time(),
    }


async def run_flight_agent_events(
    messages: list[dict[str, str]],
) -> AsyncIterator[dict[str, Any]]:
    settings = get_settings()
    conversation: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *[{"role": m["role"], "content": m["content"]} for m in messages],
    ]

    yield _trace("started", "Flight Buddy agent started (MCP host)", detail={"user_turns": len(messages)})
    final_content = ""

    try:
        async with flight_mcp_session() as session:
            yield _trace("mcp_connect", "MCP client connected to Flight Buddy server")
            tools = await list_openai_tools(session)
            yield _trace(
                "mcp_tools",
                f"Discovered {len(tools)} MCP tool(s)",
                detail={"tools": [t["function"]["name"] for t in tools]},
            )

            for round_idx in range(settings.max_tool_rounds):
                round_num = round_idx + 1
                yield _trace(
                    "llm_request",
                    f"Calling Foundry model (round {round_num}/{settings.max_tool_rounds})",
                    detail={"round": round_num, "message_count": len(conversation)},
                )

                t0 = time.perf_counter()
                response = await chat_completion(conversation, tools=tools)
                elapsed_ms = int((time.perf_counter() - t0) * 1000)

                assistant_message = response.choices[0].message
                conversation.append(_message_to_dict(assistant_message))
                tool_calls = assistant_message.tool_calls or []

                if not tool_calls:
                    final_content = assistant_message.content or ""
                    yield _trace(
                        "llm_response",
                        "Model returned a final answer (no tool calls)",
                        detail={
                            "round": round_num,
                            "elapsed_ms": elapsed_ms,
                            "preview": _truncate(final_content, 280),
                        },
                    )
                    break

                yield _trace(
                    "llm_response",
                    f"Model requested {len(tool_calls)} MCP tool call(s)",
                    detail={
                        "round": round_num,
                        "elapsed_ms": elapsed_ms,
                        "tool_names": [tc.function.name for tc in tool_calls],
                    },
                )

                for tool_call in tool_calls:
                    name = tool_call.function.name
                    try:
                        args = json.loads(tool_call.function.arguments or "{}")
                    except json.JSONDecodeError:
                        args = {"_raw": tool_call.function.arguments}

                    yield _trace(
                        "tool_call",
                        f"MCP tools/call → {name}",
                        detail={"tool": name, "arguments": args, "via": "mcp"},
                    )
                    yield {"type": "status", "message": f"Calling MCP tool: {name}…"}

                    t1 = time.perf_counter()
                    result = await call_mcp_tool(
                        session,
                        name,
                        args if isinstance(args, dict) else {},
                    )
                    tool_ms = int((time.perf_counter() - t1) * 1000)
                    summary = _tool_result_summary(result)

                    yield _trace(
                        "tool_result",
                        f"MCP tool finished: {name}",
                        detail={"tool": name, "elapsed_ms": tool_ms, **summary},
                    )
                    conversation.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result,
                        }
                    )
            else:
                yield _trace(
                    "llm_request",
                    "Max tool rounds reached — forcing final answer",
                    detail={"max_tool_rounds": settings.max_tool_rounds},
                )
                response = await chat_completion(conversation, tools=None, tool_choice=None)
                final_content = response.choices[0].message.content or ""

        message, flights = _parse_flights(final_content)
        yield {"type": "final", "message": message, "flights": flights}
        yield _trace("done", "Flight Buddy completed", detail={"flight_count": len(flights)})
    except Exception as exc:  # noqa: BLE001
        yield {"type": "error", "message": str(exc)}
        yield _trace("error", "Flight Buddy failed", detail={"error": str(exc)})


async def run_flight_agent(messages: list[dict[str, str]]) -> dict[str, Any]:
    traces: list[dict[str, Any]] = []
    status: str | None = None
    message = ""
    flights: list[dict[str, Any]] = []
    error: str | None = None

    async for event in run_flight_agent_events(messages):
        etype = event.get("type")
        if etype == "trace":
            traces.append(event)
        elif etype == "status":
            status = event.get("message")
        elif etype == "final":
            message = event.get("message") or ""
            flights = event.get("flights") or []
        elif etype == "error":
            error = event.get("message") or "Unknown agent error"

    if error:
        raise RuntimeError(error)

    return {
        "message": message,
        "flights": flights,
        "status": status,
        "traces": traces,
    }
