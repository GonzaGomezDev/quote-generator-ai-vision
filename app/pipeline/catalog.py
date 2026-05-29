"""SKU catalog loader and fuzzy matcher.

Loads catalog.seed.json once at startup. Match strategy:
  1. Build a combined search string per SKU: "<name> <brand> <category> <color>"
  2. Use rapidfuzz.process.extractOne against the vision extraction string.
  3. Return the best match if score >= MATCH_THRESHOLD, else None.
"""
import json
from pathlib import Path

from rapidfuzz import process, fuzz

from app.storage.models import Sku

CATALOG_PATH = Path(__file__).parent.parent.parent / "data" / "catalog.seed.json"
MATCH_THRESHOLD = 55  # out of 100

_catalog: list[Sku] = []
_search_strings: list[str] = []


def load_catalog() -> None:
    global _catalog, _search_strings
    raw = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    _catalog = [Sku(**item) for item in raw]
    _search_strings = [
        f"{s.name} {s.brand} {s.category} {s.color}".lower() for s in _catalog
    ]


def get_sku_by_id(sku_id: str) -> Sku | None:
    if not _catalog:
        load_catalog()
    for s in _catalog:
        if s.id == sku_id:
            return s
    return None


def search_catalog(query: str, limit: int = 5) -> list[Sku]:
    """Return up to `limit` SKUs ranked by fuzzy similarity to query."""
    if not _catalog:
        load_catalog()
    if not query.strip():
        return []
    results = process.extract(
        query.lower(), _search_strings, scorer=fuzz.token_set_ratio, limit=limit
    )
    return [_catalog[idx] for _match, score, idx in results if score >= MATCH_THRESHOLD]


def find_sku(extraction: dict) -> Sku | None:
    """Return the best-matching SKU or None if confidence is too low."""
    if not _catalog:
        load_catalog()

    query_parts = [
        extraction.get("product_guess", ""),
        extraction.get("brand") or "",
        extraction.get("category", ""),
        extraction.get("color") or "",
    ]
    query = " ".join(p for p in query_parts if p).lower().strip()
    if not query:
        return None

    result = process.extractOne(
        query, _search_strings, scorer=fuzz.token_set_ratio
    )
    if result is None:
        return None

    _match, score, idx = result
    if score < MATCH_THRESHOLD:
        return None
    return _catalog[idx]
