from __future__ import annotations

import re
from typing import Any

import httpx

from app.config import get_settings


PRICE_RE = re.compile(
    r"(?:USD|US\$|\$|AED|€|£|SAR|₹)\s?\d[\d,]*(?:\.\d{1,2})?"
    r"|\d[\d,]*(?:\.\d{1,2})?\s?(?:USD|AED|EUR|GBP|SAR)/?(?:night|nt)?",
    re.IGNORECASE,
)

# Examples: 4.5/5, 4.5 out of 5, 4-star, Rated 4.6
RATING_RE = re.compile(
    r"(?:Rated\s+)?(?P<score>\d(?:\.\d)?)\s*(?:/\s*5|out of\s*5)"
    r"|(?P<stars>\d(?:\.\d)?)\s*[- ]?\s*stars?"
    r"|Rated\s+(?P<rated>\d(?:\.\d)?)",
    re.IGNORECASE,
)

REVIEW_COUNT_RE = re.compile(
    r"([\d,]+)\s*(?:reviews?|ratings?)",
    re.IGNORECASE,
)


def _extract_price_hint(text: str) -> str | None:
    match = PRICE_RE.search(text or "")
    return match.group(0).strip() if match else None


def _extract_rating(text: str) -> str | None:
    match = RATING_RE.search(text or "")
    if not match:
        return None
    if match.group("score"):
        return f"{match.group('score')}/5"
    if match.group("stars"):
        return f"{match.group('stars')}-star"
    if match.group("rated"):
        return match.group("rated")
    return None


def _extract_review_count(text: str) -> int | None:
    match = REVIEW_COUNT_RE.search(text or "")
    if not match:
        return None
    try:
        return int(match.group(1).replace(",", ""))
    except ValueError:
        return None


def _normalize_organic(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for idx, item in enumerate(items, start=1):
        title = item.get("title") or ""
        link = item.get("link") or ""
        snippet = item.get("snippet") or ""
        combined = f"{title} {snippet}"
        results.append(
            {
                "source": "organic",
                "title": title,
                "link": link,
                "snippet": snippet,
                "position": item.get("position") or idx,
                "price_hint": _extract_price_hint(combined),
                "rating": _extract_rating(combined),
                "review_count": _extract_review_count(combined),
                "address": None,
            }
        )
    return results


def _normalize_places(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for idx, item in enumerate(items, start=1):
        title = item.get("title") or ""
        address = item.get("address") or ""
        category = item.get("type") or item.get("category") or ""
        rating_val = item.get("rating")
        rating_count = item.get("ratingCount") or item.get("reviewsCount")
        website = item.get("website") or item.get("link") or ""
        cid = item.get("cid") or item.get("placeId") or ""
        link = website or (
            f"https://www.google.com/maps?cid={cid}" if cid else ""
        )
        snippet_parts = [p for p in [category, address] if p]
        if rating_val is not None:
            snippet_parts.insert(0, f"Google rating {rating_val}")
        if rating_count is not None:
            snippet_parts.append(f"{rating_count} reviews")
        snippet = " · ".join(snippet_parts)

        rating: str | None = None
        if rating_val is not None:
            rating = f"{rating_val}/5"

        review_count: int | None = None
        if rating_count is not None:
            try:
                review_count = int(str(rating_count).replace(",", ""))
            except ValueError:
                review_count = None

        results.append(
            {
                "source": "places",
                "title": title,
                "link": link,
                "snippet": snippet,
                "position": idx,
                "price_hint": _extract_price_hint(snippet),
                "rating": rating,
                "review_count": review_count,
                "address": address or None,
                "category": category or None,
            }
        )
    return results


async def _serper_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    if not settings.serper_api_key:
        raise RuntimeError("SERPER_API_KEY is not configured")

    headers = {
        "X-API-KEY": settings.serper_api_key,
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"https://google.serper.dev/{path}",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()


async def search_google(query: str, num: int = 20) -> list[dict[str, Any]]:
    """Call Serper Google Search and return normalized organic results."""
    data = await _serper_post("search", {"q": query, "num": num})
    organic = data.get("organic") or []
    return _normalize_organic(organic)


async def search_places(query: str, num: int = 20) -> list[dict[str, Any]]:
    """Call Serper Places (Maps) for hotels with ratings/review counts."""
    data = await _serper_post("places", {"q": query, "num": num})
    places = data.get("places") or []
    return _normalize_places(places)


async def search_hotels_live(
    query: str,
    location: str,
    extras: str | None = None,
    num: int = 20,
) -> dict[str, Any]:
    """Run organic + places searches and return a merged result set."""
    places_query = f"hotels in {location}"
    if extras:
        places_query = f"{places_query} {extras}"

    organic = await search_google(query, num=num)
    places: list[dict[str, Any]] = []
    places_error: str | None = None
    try:
        places = await search_places(places_query, num=num)
    except Exception as exc:  # noqa: BLE001
        places_error = str(exc)

    # Deduplicate by normalized title, prefer places (has ratings)
    merged: list[dict[str, Any]] = []
    seen: set[str] = set()

    def _key(title: str) -> str:
        return re.sub(r"\s+", " ", title).strip().lower()

    for item in places + organic:
        title = item.get("title") or ""
        key = _key(title)
        if not key or key in seen:
            continue
        seen.add(key)
        merged.append(item)

    return {
        "query_used": query,
        "places_query_used": places_query,
        "organic_count": len(organic),
        "places_count": len(places),
        "result_count": len(merged),
        "places_error": places_error,
        "results": merged[: max(num, 20)],
    }
