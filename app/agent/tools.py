"""Tool definitions and dispatcher for the agent loop."""
import json
import time
from typing import Any

from app.vision import claude_client
from app.pipeline.catalog import find_sku, search_catalog as _search_catalog
from app.pipeline.quoting import build_quote as _build_quote, format_quote_message


TOOL_SCHEMAS = [
    {
        "name": "analyze_product_image",
        "description": (
            "Identificá el producto en la imagen que el cliente acaba de enviar y "
            "buscalo en el catálogo. Llamá esta herramienta (sin parámetros) cada vez "
            "que el cliente envíe una foto."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "search_catalog",
        "description": (
            "Search the product catalog by free-text query (e.g. 'red Nike sneakers', "
            "'leather bag'). Returns up to 5 matching SKUs with id, name, brand, "
            "category, color, and unit price."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Product description or keywords to search.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results to return (default 5).",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "build_quote",
        "description": (
            "Generate a full price quote (unit price, subtotal, tax, shipping, total) "
            "for a confirmed SKU and quantity. Always call this after the customer "
            "confirms the product they want."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "sku_id": {
                    "type": "string",
                    "description": "The catalog SKU id to quote.",
                },
                "quantity": {
                    "type": "integer",
                    "description": "Number of units (default 1).",
                    "default": 1,
                },
            },
            "required": ["sku_id"],
        },
    },
]


async def dispatch_tool(
    name: str,
    tool_input: dict[str, Any],
    image_cache: dict[str, tuple[bytes, str]] | None = None,
) -> tuple[str, dict]:
    """
    Run the named tool and return (json_result_string, timing_dict).
    Timing dict has a single key f"{name}_ms".
    image_cache maps url → (bytes, media_type) so the vision tool reuses
    already-downloaded image data instead of re-fetching.
    """
    t0 = time.monotonic()

    if name == "analyze_product_image":
        result = await _run_analyze_image(image_cache or {})
    elif name == "search_catalog":
        result = _run_search_catalog(
            tool_input["query"], tool_input.get("limit", 5)
        )
    elif name == "build_quote":
        result = _run_build_quote(
            tool_input["sku_id"], tool_input.get("quantity", 1)
        )
    else:
        result = {"error": f"Unknown tool: {name}"}

    ms = int((time.monotonic() - t0) * 1000)
    return json.dumps(result), {f"{name}_ms": ms}


async def _run_analyze_image(image_cache: dict[str, tuple[bytes, str]]) -> dict:
    if not image_cache:
        return {"error": "No hay imagen disponible para analizar."}
    image_bytes, media_type = next(iter(image_cache.values()))
    extraction = await claude_client.extract_from_bytes(image_bytes, media_type)
    sku = find_sku(extraction)
    return {
        "extraction": extraction,
        "sku": _sku_summary(sku) if sku else None,
    }


def _run_search_catalog(query: str, limit: int) -> dict:
    skus = _search_catalog(query, limit)
    return {"results": [_sku_summary(s) for s in skus]}


def _run_build_quote(sku_id: str, quantity: int) -> dict:
    from app.pipeline.catalog import get_sku_by_id
    sku = get_sku_by_id(sku_id)
    if sku is None:
        return {"error": f"SKU '{sku_id}' no encontrado en el catálogo."}
    q = _build_quote(sku, quantity)
    return {
        "sku_id": q.sku_id,
        "sku_name": q.sku_name,
        "quantity": q.quantity,
        "unit_price": q.unit_price,
        "subtotal": q.subtotal,
        "tax": q.tax,
        "shipping": q.shipping,
        "total": q.total,
        "currency": q.currency,
        "message": format_quote_message(q),
    }


def _sku_summary(sku) -> dict:
    return {
        "id": sku.id,
        "name": sku.name,
        "brand": sku.brand,
        "category": sku.category,
        "color": sku.color,
        "unit_price": sku.unit_price,
        "currency": sku.currency,
    }
