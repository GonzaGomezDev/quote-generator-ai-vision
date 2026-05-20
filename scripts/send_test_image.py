#!/usr/bin/env python
"""CLI smoke-test: extract product data from a local image file.

Usage:
    python scripts/send_test_image.py path/to/image.jpg
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.vision.claude_client import extract_from_bytes
from app.pipeline.catalog import find_sku, load_catalog
from app.pipeline.quoting import build_quote, format_quote_message


async def main(image_path: str) -> None:
    path = Path(image_path)
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    print(f"\n[1/3] Sending {path.name} to Claude Sonnet 4.6…")
    extraction = await extract_from_bytes(path.read_bytes(), "image/jpeg")
    print("Extraction:", json.dumps(extraction, indent=2))

    print("\n[2/3] Matching SKU…")
    load_catalog()
    sku = find_sku(extraction)
    if sku:
        print(f"Matched: {sku.id} — {sku.name} @ ${sku.unit_price}")
    else:
        print("No SKU matched (confidence below threshold).")
        return

    print("\n[3/3] Building quote…")
    qty = extraction.get("estimated_quantity", 1)
    quote = build_quote(sku, qty)
    print(format_quote_message(quote))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/send_test_image.py <image_path>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
