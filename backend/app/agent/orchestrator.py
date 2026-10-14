from __future__ import annotations

import json
import re
import time
from collections.abc import AsyncIterator
from typing import Any

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import TOOL_DEFINITIONS, execute_tool
from app.config import get_settings
from app.services.foundry import chat_completion

HOTELS_JSON_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE)


def _message_to_dict(message: Any) -> dict[str, Any]:
    """Convert an OpenAI SDK message object into a serializable dict."""
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


def _parse_hotels(content: str | None) -> tuple[str, list[dict[str, Any]]]:
    if not content:
        return "", []

    hotels: list[dict[str, Any]] = []
    display = content
    match = HOTELS_JSON_RE.search(content)
    if match:
        try:
            payload = json.loads(match.group(1))
            raw = payload.get("hotels") or []
            for item in raw:
                if not isinstance(item, dict):
                    continue
                review_count = item.get("review_count")
                if isinstance(review_count, str):
                    digits = re.sub(r"[^\d]", "", review_count)
                    review_count = int(digits) if digits else None
                elif isinstance(review_count, float):
                    review_count = int(review_count)
                elif not isinstance(review_count, int):
                    review_count = None

                hotels.append(
                    {
                        "name": item.get("name") or "Hotel",
                        "price_hint": item.get("price_hint"),
                        "rating": item.get("rating"),
                        "review_count": review_count,
                        "address": item.get("address"),
                        "why": item.get("why") or "",
                        "link": item.get("link") or "",
                        "snippet": item.get("snippet") or "",
                    }
                )
        except json.JSONDecodeError:
            hotels = []
        display = (content[: match.start()] + content[match.end() :]).strip()

    return display, hotels


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

    results = payload.get("results") or []
    titles = [r.get("title") for r in results[:5] if isinstance(r, dict)]
    return {
        "query_used": payload.get("query_used"),
        "places_query_used": payload.get("places_query_used"),
        "result_count": payload.get("result_count", len(results)),
        "organic_count": payload.get("organic_count"),
        "places_count": payload.get("places_count"),
        "error": payload.get("error"),
        "places_error": payload.get("places_error"),
        "top_titles": titles,
    }


def _trace(
    step: str,
    message: str,
    *,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "type": "trace",
        "step": step,
        "message": message,
        "detail": detail or {},
        "ts": time.time(),
    }


async def run_agent_events(
    messages: list[dict[str, str]],
) -> AsyncIterator[dict[str, Any]]:
    """Yield live trace/status/final events for the single-agent tool loop."""
    settings = get_settings()
    conversation: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *[{"role": m["role"], "content": m["content"]} for m in messages],
    ]

    yield _trace("started", "Agent started", detail={"user_turns": len(messages)})
    final_content = ""

    try:
        for round_idx in range(settings.max_tool_rounds):
            round_num = round_idx + 1
            yield _trace(
                "llm_request",
                f"Calling Foundry model (round {round_num}/{settings.max_tool_rounds})",
                detail={"round": round_num, "message_count": len(conversation)},
            )

            t0 = time.perf_counter()
            response = await chat_completion(conversation, tools=TOOL_DEFINITIONS)
            elapsed_ms = int((time.perf_counter() - t0) * 1000)

            choice = response.choices[0]
            assistant_message = choice.message
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
                f"Model requested {len(tool_calls)} tool call(s)",
                detail={
                    "round": round_num,
                    "elapsed_ms": elapsed_ms,
                    "tool_names": [tc.function.name for tc in tool_calls],
                    "preview": _truncate(assistant_message.content or "", 200),
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
                    f"Running tool: {name}",
                    detail={"tool": name, "arguments": args},
                )
                yield {
                    "type": "status",
                    "message": "Searching live rates…",
                }

                t1 = time.perf_counter()
                result = await execute_tool(name, args if isinstance(args, dict) else {})
                tool_ms = int((time.perf_counter() - t1) * 1000)
                summary = _tool_result_summary(result)

                yield _trace(
                    "tool_result",
                    f"Tool finished: {name}",
                    detail={
                        "tool": name,
                        "elapsed_ms": tool_ms,
                        **summary,
                    },
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
            t0 = time.perf_counter()
            response = await chat_completion(conversation, tools=None, tool_choice=None)
            elapsed_ms = int((time.perf_counter() - t0) * 1000)
            final_content = response.choices[0].message.content or ""
            yield _trace(
                "llm_response",
                "Forced final answer received",
                detail={
                    "elapsed_ms": elapsed_ms,
                    "preview": _truncate(final_content, 280),
                },
            )

        message, hotels = _parse_hotels(final_content)
        yield {
            "type": "final",
            "message": message,
            "hotels": hotels,
        }
        yield _trace(
            "done",
            "Agent completed",
            detail={"hotel_count": len(hotels)},
        )
    except Exception as exc:  # noqa: BLE001
        yield {
            "type": "error",
            "message": str(exc),
        }
        yield _trace("error", "Agent failed", detail={"error": str(exc)})


async def run_agent(messages: list[dict[str, str]]) -> dict[str, Any]:
    """Run the agent and return message, hotels, status, and full traces."""
    traces: list[dict[str, Any]] = []
    status: str | None = None
    message = ""
    hotels: list[dict[str, Any]] = []
    error: str | None = None

    async for event in run_agent_events(messages):
        etype = event.get("type")
        if etype == "trace":
            traces.append(event)
        elif etype == "status":
            status = event.get("message")
        elif etype == "final":
            message = event.get("message") or ""
            hotels = event.get("hotels") or []
        elif etype == "error":
            error = event.get("message") or "Unknown agent error"

    if error:
        raise RuntimeError(error)

    return {
        "message": message,
        "hotels": hotels,
        "status": status,
        "traces": traces,
    }
