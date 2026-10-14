from __future__ import annotations

import json
from typing import Any

from app.services.serper import search_hotels_live

SEARCH_HOTELS_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "search_hotels",
        "description": (
            "Search live Google + Google Places via Serper for hotels matching the "
            "user's trip. Returns many candidates with price hints, ratings, and "
            "review counts when available. Use detailed queries including location, "
            "dates, room type, budget, and landmarks."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Full Google search query, e.g. "
                        "'best hotels near Burj Khalifa Dubai March 10-15 2027 "
                        "king room under $250 per night ratings'"
                    ),
                },
                "location": {
                    "type": "string",
                    "description": "City or area, e.g. Dubai",
                },
                "check_in": {
                    "type": "string",
                    "description": "Check-in date if known, e.g. 2026-03-10",
                },
                "check_out": {
                    "type": "string",
                    "description": "Check-out date if known, e.g. 2026-03-15",
                },
                "extras": {
                    "type": "string",
                    "description": "Optional extras: room size, amenities, budget",
                },
            },
            "required": ["query", "location"],
        },
    },
}

TOOL_DEFINITIONS = [SEARCH_HOTELS_TOOL]


def build_search_query(
    query: str,
    location: str,
    check_in: str | None = None,
    check_out: str | None = None,
    extras: str | None = None,
) -> str:
    parts = [query.strip()]
    lower = query.lower()
    if location and location.lower() not in lower:
        parts.append(location)
    if check_in and check_in not in query:
        parts.append(f"check-in {check_in}")
    if check_out and check_out not in query:
        parts.append(f"check-out {check_out}")
    if extras and extras.lower() not in lower:
        parts.append(extras)
    # Bias search toward rated listings / comparison pages
    if "rating" not in lower and "review" not in lower:
        parts.append("hotel ratings reviews")
    return " ".join(p for p in parts if p)


async def execute_tool(name: str, arguments: dict[str, Any]) -> str:
    if name != "search_hotels":
        return json.dumps({"error": f"Unknown tool: {name}"})

    query = build_search_query(
        query=arguments.get("query") or "",
        location=arguments.get("location") or "",
        check_in=arguments.get("check_in"),
        check_out=arguments.get("check_out"),
        extras=arguments.get("extras"),
    )
    location = arguments.get("location") or ""
    if not query.strip():
        return json.dumps({"error": "Empty search query", "results": []})

    try:
        payload = await search_hotels_live(
            query=query,
            location=location,
            extras=arguments.get("extras"),
            num=20,
        )
        return json.dumps(payload)
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"error": str(exc), "query_used": query, "results": []})
