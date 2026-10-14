"""Azure Functions MCP server — Flight Buddy tools."""

from __future__ import annotations

import json
import logging

import azure.functions as func

from flights import rank_flights_payload, search_flights_payload

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.mcp_tool()
@app.mcp_tool_property(arg_name="departure_id", description="IATA origin code, e.g. ISB", is_required=True)
@app.mcp_tool_property(arg_name="arrival_id", description="IATA destination code, e.g. JED", is_required=True)
@app.mcp_tool_property(arg_name="outbound_date", description="Departure date YYYY-MM-DD", is_required=True)
@app.mcp_tool_property(arg_name="return_date", description="Optional return date YYYY-MM-DD", is_required=False)
@app.mcp_tool_property(arg_name="max_price", description="Optional max ticket price", is_required=False)
@app.mcp_tool_property(arg_name="max_stops", description="Optional max stops (0=nonstop)", is_required=False)
@app.mcp_tool_property(arg_name="adults", description="Number of adults (default 1)", is_required=False)
@app.mcp_tool_property(arg_name="currency", description="Currency code (default USD)", is_required=False)
def search_flights(
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    return_date: str | None = None,
    max_price: str | None = None,
    max_stops: str | None = None,
    adults: str | None = None,
    currency: str | None = None,
) -> str:
    """Search live flights via Google Flights (SerpApi)."""
    try:
        payload = search_flights_payload(
            departure_id=departure_id,
            arrival_id=arrival_id,
            outbound_date=outbound_date,
            return_date=return_date or None,
            max_price=int(max_price) if max_price not in (None, "") else None,
            max_stops=int(max_stops) if max_stops not in (None, "") else None,
            adults=int(adults) if adults not in (None, "") else 1,
            currency=currency or "USD",
        )
    except Exception as exc:  # noqa: BLE001
        logging.exception("search_flights failed")
        payload = {"error": str(exc), "offers": [], "offer_count": 0}
    return json.dumps(payload)


@app.mcp_tool()
@app.mcp_tool_property(arg_name="offers_json", description="JSON from search_flights", is_required=True)
@app.mcp_tool_property(
    arg_name="prefer",
    description="cheapest | fastest | fewest_stops | balanced",
    is_required=False,
)
@app.mcp_tool_property(arg_name="limit", description="How many results to return", is_required=False)
def rank_flights(
    offers_json: str,
    prefer: str | None = None,
    limit: str | None = None,
) -> str:
    """Rank flight offers by preference."""
    try:
        pref = prefer or "balanced"
        if pref not in ("cheapest", "fastest", "fewest_stops", "balanced"):
            pref = "balanced"
        lim = int(limit) if limit not in (None, "") else 5
        payload = rank_flights_payload(offers_json, prefer=pref, limit=lim)  # type: ignore[arg-type]
    except Exception as exc:  # noqa: BLE001
        logging.exception("rank_flights failed")
        payload = {"error": str(exc), "ranked": []}
    return json.dumps(payload)


@app.mcp_tool()
@app.mcp_tool_property(arg_name="offer_json", description="One offer object as JSON", is_required=True)
def get_flight_details(offer_json: str) -> str:
    """Summarize a single flight offer."""
    try:
        offer = json.loads(offer_json)
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
        }
        return json.dumps(summary)
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"error": str(exc)})


@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def health(req: func.HttpRequest) -> func.HttpResponse:
    """Simple health endpoint for probes / sanity checks."""
    return func.HttpResponse(
        json.dumps({"status": "ok", "app": "flight-buddy-mcp"}),
        mimetype="application/json",
        status_code=200,
    )
