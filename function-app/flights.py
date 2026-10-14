"""Shared Google Flights helpers (SerpApi) for Azure Functions MCP tools."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Literal

import httpx

Prefer = Literal["cheapest", "fastest", "fewest_stops", "balanced"]


def _api_key() -> str:
    key = os.getenv("SERPAPI_API_KEY") or os.getenv("SERP_API_KEY") or ""
    if not key:
        raise RuntimeError("SERPAPI_API_KEY is not configured on the Function App")
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
        "link": "https://www.google.com/travel/flights",
        "raw_bucket": bucket,
    }


def search_flights_payload(
    *,
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    return_date: str | None = None,
    max_price: int | None = None,
    max_stops: int | None = None,
    adults: int = 1,
    currency: str = "USD",
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "engine": "google_flights",
        "api_key": _api_key(),
        "departure_id": departure_id.upper().strip(),
        "arrival_id": arrival_id.upper().strip(),
        "outbound_date": outbound_date,
        "adults": max(1, adults),
        "currency": currency or "USD",
        "hl": "en",
        "gl": "us",
        "type": 1 if return_date else 2,
    }
    if return_date:
        params["return_date"] = return_date
    if max_price is not None:
        params["max_price"] = int(max_price)
    if max_stops is not None:
        if max_stops <= 0:
            params["stops"] = 1
        elif max_stops == 1:
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
            "max_stops": max_stops,
            "adults": adults,
            "currency": currency,
        },
        "offer_count": len(offers),
        "price_insights": {
            "lowest_price": insights.get("lowest_price"),
            "price_level": insights.get("price_level"),
        },
        "offers": offers[:25],
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
    return (price_n / 50.0) + (dur_n / 30.0) + (stops_n * 40.0)


def rank_flights_payload(
    offers_json: str,
    prefer: Prefer = "balanced",
    limit: int = 5,
) -> dict[str, Any]:
    data = json.loads(offers_json)
    if isinstance(data, list):
        offers = [o for o in data if isinstance(o, dict)]
    elif isinstance(data, dict):
        offers = [o for o in (data.get("offers") or []) if isinstance(o, dict)]
    else:
        offers = []

    scored = [{**o, "rank_score": round(_score_offer(o, prefer), 2), "prefer": prefer} for o in offers]
    scored.sort(key=lambda o: o["rank_score"])
    top = scored[: max(1, min(limit, 15))]
    return {
        "prefer": prefer,
        "ranked_count": len(top),
        "ranked": top,
        "winner": top[0] if top else None,
    }
