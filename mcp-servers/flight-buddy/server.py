#!/usr/bin/env python3
"""Flight Buddy MCP server — tools backed by SerpApi Google Flights."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Literal

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

ROOT = Path(__file__).resolve().parent
# Load repo backend .env if present, then local .env
load_dotenv(ROOT.parents[1] / "backend" / ".env")
load_dotenv(ROOT / ".env")

mcp = FastMCP(
    "flight-buddy",
    instructions=(
        "Flight Buddy finds and ranks real flights via Google Flights (SerpApi). "
        "Use search_flights first, then rank_flights. Prefer IATA airport codes."
    ),
)

Prefer = Literal["cheapest", "fastest", "fewest_stops", "balanced"]


def _api_key() -> str:
    key = os.getenv("SERPAPI_API_KEY") or os.getenv("SERP_API_KEY") or ""
    if not key:
        raise RuntimeError(
            "SERPAPI_API_KEY is not set. Add it to backend/.env or mcp-servers/flight-buddy/.env"
        )
    return key


def _minutes_label(mins: int | None) -> str:
    if mins is None:
        return "n/a"
    h, m = divmod(int(mins), 60)
    if h and m:
        return f"{h}h {m}m"
    if h:
        return f"{h}h"
    return f"{m}m"


def _normalize_offer(raw: dict[str, Any], idx: int, bucket: str) -> dict[str, Any]:
    legs = raw.get("flights") or []
    layovers = raw.get("layovers") or []
    airlines: list[str] = []
    flight_numbers: list[str] = []
    for leg in legs:
        if not isinstance(leg, dict):
            continue
        airline = leg.get("airline")
        if airline and airline not in airlines:
            airlines.append(str(airline))
        fn = leg.get("flight_number")
        if fn:
            flight_numbers.append(str(fn))

    dep = legs[0].get("departure_airport") if legs else {}
    arr = legs[-1].get("arrival_airport") if legs else {}
    if not isinstance(dep, dict):
        dep = {}
    if not isinstance(arr, dict):
        arr = {}

    stops = max(0, len(legs) - 1) if legs else len(layovers)
    duration = raw.get("total_duration")
    price = raw.get("price")
    google_flights = (
        raw.get("google_flights_url")
        or raw.get("link")
        or "https://www.google.com/travel/flights"
    )

    offer_id = f"{bucket}-{idx}-" + "-".join(
        re.sub(r"\s+", "", fn) for fn in flight_numbers[:3]
    ) or f"{bucket}-{idx}"

    return {
        "id": offer_id,
        "airlines": airlines,
        "flight_numbers": flight_numbers,
        "departure_airport": dep.get("id"),
        "arrival_airport": arr.get("id"),
        "departure_time": dep.get("time"),
        "arrival_time": arr.get("time"),
        "stops": stops,
        "duration_minutes": duration,
        "duration_label": _minutes_label(duration if isinstance(duration, int) else None),
        "price": price,
        "price_label": f"${price}" if isinstance(price, (int, float)) else None,
        "extensions": raw.get("extensions") or [],
        "layovers": [
            {
                "airport": ly.get("id"),
                "name": ly.get("name"),
                "duration_minutes": ly.get("duration"),
                "overnight": bool(ly.get("overnight")),
            }
            for ly in layovers
            if isinstance(ly, dict)
        ],
        "booking_token": raw.get("booking_token"),
        "departure_token": raw.get("departure_token"),
        "link": google_flights,
        "raw_bucket": bucket,
    }


def _search_serpapi(
    *,
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    return_date: str | None,
    max_price: int | None,
    stops: int | None,
    adults: int,
    currency: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "engine": "google_flights",
        "api_key": _api_key(),
        "departure_id": departure_id.upper().strip(),
        "arrival_id": arrival_id.upper().strip(),
        "outbound_date": outbound_date,
        "adults": adults,
        "currency": currency,
        "hl": "en",
        "gl": "us",
        "type": 1 if return_date else 2,
    }
    if return_date:
        params["return_date"] = return_date
    if max_price is not None:
        params["max_price"] = int(max_price)
    # SerpApi: 0 any, 1 nonstop, 2 one-or-fewer, 3 two-or-fewer
    if stops is not None:
        if stops <= 0:
            params["stops"] = 1
        elif stops == 1:
            params["stops"] = 2
        else:
            params["stops"] = 3

    with httpx.Client(timeout=60.0) as client:
        response = client.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        data = response.json()

    if data.get("error"):
        raise RuntimeError(str(data["error"]))

    offers: list[dict[str, Any]] = []
    for bucket in ("best_flights", "other_flights"):
        items = data.get(bucket) or []
        for idx, item in enumerate(items, start=1):
            if isinstance(item, dict):
                offers.append(_normalize_offer(item, idx, bucket))

    insights = data.get("price_insights") or {}
    return {
        "query": {
            "from": departure_id.upper(),
            "to": arrival_id.upper(),
            "outbound_date": outbound_date,
            "return_date": return_date,
            "max_price": max_price,
            "stops": stops,
            "adults": adults,
            "currency": currency,
            "trip_type": "round_trip" if return_date else "one_way",
        },
        "offer_count": len(offers),
        "price_insights": {
            "lowest_price": insights.get("lowest_price"),
            "price_level": insights.get("price_level"),
            "typical_price_range": insights.get("typical_price_range"),
        },
        "offers": offers[:25],
        "search_metadata": data.get("search_metadata") or {},
    }


def _score_offer(offer: dict[str, Any], prefer: Prefer) -> float:
    price = offer.get("price")
    duration = offer.get("duration_minutes")
    stops = offer.get("stops")
    price_n = float(price) if isinstance(price, (int, float)) else 9_999.0
    dur_n = float(duration) if isinstance(duration, (int, float)) else 9_999.0
    stops_n = float(stops) if isinstance(stops, (int, float)) else 9.0

    if prefer == "cheapest":
        return price_n
    if prefer == "fastest":
        return dur_n
    if prefer == "fewest_stops":
        return stops_n * 10_000 + price_n
    # balanced: normalize roughly
    return (price_n / 50.0) + (dur_n / 30.0) + (stops_n * 40.0)


@mcp.tool()
def search_flights(
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    return_date: str | None = None,
    max_price: int | None = None,
    max_stops: int | None = None,
    adults: int = 1,
    currency: str = "USD",
) -> str:
    """Search live flights via Google Flights (SerpApi).

    Args:
        departure_id: IATA origin airport code, e.g. ISB, IST, JFK.
        arrival_id: IATA destination airport code, e.g. JED, LHR.
        outbound_date: Departure date YYYY-MM-DD.
        return_date: Optional return date YYYY-MM-DD for round trips.
        max_price: Optional maximum ticket price in the chosen currency.
        max_stops: Optional max stops (0=nonstop, 1=one stop, 2=two).
        adults: Number of adult passengers (default 1).
        currency: Currency code (default USD).
    """
    try:
        payload = _search_serpapi(
            departure_id=departure_id,
            arrival_id=arrival_id,
            outbound_date=outbound_date,
            return_date=return_date,
            max_price=max_price,
            stops=max_stops,
            adults=max(1, adults),
            currency=currency or "USD",
        )
    except Exception as exc:  # noqa: BLE001
        payload = {"error": str(exc), "offers": [], "offer_count": 0}
    return json.dumps(payload)


@mcp.tool()
def rank_flights(
    offers_json: str,
    prefer: Prefer = "balanced",
    limit: int = 5,
) -> str:
    """Rank flight offers from search_flights by preference.

    Args:
        offers_json: JSON string — either the full search_flights payload or a list of offers.
        prefer: cheapest | fastest | fewest_stops | balanced.
        limit: How many top offers to return (default 5).
    """
    try:
        data = json.loads(offers_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "offers_json must be valid JSON", "ranked": []})

    if isinstance(data, list):
        offers = [o for o in data if isinstance(o, dict)]
    elif isinstance(data, dict):
        offers = [o for o in (data.get("offers") or []) if isinstance(o, dict)]
    else:
        offers = []

    scored = []
    for offer in offers:
        score = _score_offer(offer, prefer)
        scored.append({**offer, "rank_score": round(score, 2), "prefer": prefer})

    scored.sort(key=lambda o: o["rank_score"])
    top = scored[: max(1, min(limit, 15))]
    return json.dumps(
        {
            "prefer": prefer,
            "ranked_count": len(top),
            "ranked": top,
            "winner": top[0] if top else None,
        }
    )


@mcp.tool()
def get_flight_details(offer_json: str) -> str:
    """Summarize a single flight offer JSON for the user.

    Args:
        offer_json: One offer object from search_flights/rank_flights as JSON string.
    """
    try:
        offer = json.loads(offer_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "offer_json must be valid JSON"})

    if not isinstance(offer, dict):
        return json.dumps({"error": "offer_json must be an object"})

    summary = {
        "id": offer.get("id"),
        "summary": (
            f"{', '.join(offer.get('airlines') or ['Unknown airline'])} "
            f"{' / '.join(offer.get('flight_numbers') or [])}: "
            f"{offer.get('departure_airport')} → {offer.get('arrival_airport')} · "
            f"{offer.get('duration_label')} · {offer.get('stops')} stop(s) · "
            f"{offer.get('price_label') or 'price n/a'}"
        ),
        "departure_time": offer.get("departure_time"),
        "arrival_time": offer.get("arrival_time"),
        "layovers": offer.get("layovers") or [],
        "extensions": offer.get("extensions") or [],
        "link": offer.get("link"),
        "note": "Confirm baggage and final price on the airline or Google Flights booking page.",
    }
    return json.dumps(summary)


@mcp.resource("baggage://policy")
def baggage_policy() -> str:
    """Sample baggage policy notes for international economy flights."""
    path = ROOT / "resources" / "baggage_policy.md"
    return path.read_text(encoding="utf-8")


@mcp.prompt()
def find_best_flight() -> str:
    """Guided workflow to find the best flight for a traveler."""
    return (
        "Ask the user for origin IATA, destination IATA, outbound date (YYYY-MM-DD), "
        "optional return date, budget, and preference (cheapest / fastest / fewest_stops / balanced). "
        "Then call search_flights, then rank_flights with that preference. "
        "Present the top 3 options with price, duration, stops, and why the winner fits. "
        "Remind them to confirm baggage and fare rules before booking."
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
