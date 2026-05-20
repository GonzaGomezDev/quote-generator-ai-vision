#!/usr/bin/env python
"""One-shot setup script.

Run once after cloning:
    python scripts/seed.py

What it does:
  1. Creates data/app.db with the required tables (idempotent).
  2. Validates data/catalog.seed.json and prints a SKU summary.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.storage.db import init_db
import app.pipeline.catalog as catalog_module


async def main() -> None:
    print("-- Initialising database --------------------------------")
    await init_db()
    db_path = Path(__file__).parent.parent / "data" / "app.db"
    print(f"   OK  {db_path}")

    print("\n-- Loading catalog --------------------------------------")
    catalog_module.load_catalog()
    skus = catalog_module._catalog
    if not skus:
        print("   ERROR  data/catalog.seed.json is empty or missing.", file=sys.stderr)
        sys.exit(1)

    print(f"   {len(skus)} SKUs loaded\n")
    print(f"   {'ID':<10} {'Name':<42} {'Category':<14} {'Price':>8}")
    print(f"   {'-'*10} {'-'*42} {'-'*14} {'-'*8}")
    for sku in skus:
        print(f"   {sku.id:<10} {sku.name:<42} {sku.category:<14} ${sku.unit_price:>7.2f}")

    print("\n-- All good - ready to run ------------------------------")
    print("   uvicorn app.main:app --reload")
    print("   cd web && npm run dev")


if __name__ == "__main__":
    asyncio.run(main())
