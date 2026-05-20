#!/usr/bin/env python
"""Pre-load catalog into the catalog.py in-memory store (sanity check)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.pipeline.catalog import load_catalog, _catalog

load_catalog()
print(f"Loaded {len(_catalog)} SKUs:")
for sku in _catalog:
    print(f"  {sku.id}  {sku.name:<40}  ${sku.unit_price:.2f}")
