"""Lightweight smoke tests that do not require live API keys."""

from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.agent.orchestrator import _parse_hotels  # noqa: E402
from app.agent.tools import build_search_query  # noqa: E402
from app.services.serper import _extract_price_hint, _normalize_organic  # noqa: E402


def test_price_hint_extraction() -> None:
    assert _extract_price_hint("Rooms from $199/night near Downtown") == "$199"
    assert _extract_price_hint("Rates start at AED 450") is not None
    assert _extract_price_hint("No price here") is None


def test_rating_extraction() -> None:
    from app.services.serper import _extract_rating, _extract_review_count

    assert _extract_rating("Guests rate it 4.6/5 overall") == "4.6/5"
    assert _extract_rating("A popular 4-star hotel") == "4-star"
    assert _extract_review_count("Based on 1,234 reviews") == 1234


def test_normalize_organic() -> None:
    results = _normalize_organic(
        [
            {
                "title": "Grand Hotel Dubai — from $210",
                "link": "https://example.com/hotel",
                "snippet": "King rooms near Burj Khalifa. Rated 4.5/5 from 890 reviews",
                "position": 1,
            }
        ]
    )
    assert results[0]["title"].startswith("Grand Hotel")
    assert results[0]["price_hint"] == "$210"
    assert results[0]["rating"] == "4.5/5"
    assert results[0]["review_count"] == 890
    assert results[0]["link"] == "https://example.com/hotel"


def test_build_search_query_reinforces_fields() -> None:
    q = build_search_query(
        query="best hotels under $250",
        location="Dubai",
        check_in="2026-03-10",
        check_out="2026-03-15",
        extras="king room",
    )
    assert "Dubai" in q
    assert "2026-03-10" in q
    assert "king room" in q


def test_parse_hotels_json_block() -> None:
    content = """Here are my picks.

```json
{
  "hotels": [
    {
      "name": "Address Downtown",
      "price_hint": "$240/night",
      "why": "Near Burj Khalifa",
      "link": "https://example.com",
      "snippet": "Luxury stay"
    }
  ]
}
```
"""
    message, hotels = _parse_hotels(content)
    assert "Here are my picks." in message
    assert "```json" not in message
    assert hotels[0]["name"] == "Address Downtown"
    assert hotels[0]["price_hint"] == "$240/night"


def test_health_import() -> None:
    from app.main import app

    assert app.title == "Hotel Finder Agent"


def test_trace_helper_shape() -> None:
    from app.agent.orchestrator import _trace

    event = _trace("started", "Agent started", detail={"ok": True})
    assert event["type"] == "trace"
    assert event["step"] == "started"
    assert "ts" in event


if __name__ == "__main__":
    test_price_hint_extraction()
    test_rating_extraction()
    test_normalize_organic()
    test_build_search_query_reinforces_fields()
    test_parse_hotels_json_block()
    test_health_import()
    test_trace_helper_shape()
    print(json.dumps({"ok": True, "tests": 7}))
