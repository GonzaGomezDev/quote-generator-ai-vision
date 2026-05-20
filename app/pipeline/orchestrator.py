"""Core pipeline: download → vision → match → quote → reply → SSE.

Returns a PipelineEvent with per-stage latency timings.
"""
import time
import uuid
from dataclasses import asdict
from datetime import datetime, timezone

from app.storage.models import PipelineEvent
from app.vision import claude_client
from app.pipeline.catalog import find_sku
from app.pipeline.quoting import build_quote, format_quote_message
from app.realtime.events import broadcast
from app.storage.db import insert_event


async def run_pipeline(
    image_url: str,
    channel: str,
    sender: str,
    reply_fn,           # async callable(sender, text) → None
) -> PipelineEvent:
    message_id = str(uuid.uuid4())
    latencies: dict[str, int] = {}

    # 1. Download + extract ───────────────────────────────────────────────────
    t0 = time.monotonic()
    extraction = await claude_client.extract_from_url(image_url)
    latencies["vision_ms"] = int((time.monotonic() - t0) * 1000)

    # 2. Catalog match ────────────────────────────────────────────────────────
    t1 = time.monotonic()
    sku = find_sku(extraction)
    latencies["match_ms"] = int((time.monotonic() - t1) * 1000)

    # 3. Quote ────────────────────────────────────────────────────────────────
    t2 = time.monotonic()
    quote_dict: dict | None = None
    reply_text: str

    if sku:
        qty = extraction.get("estimated_quantity", 1)
        q = build_quote(sku, qty)
        quote_dict = {
            "sku_id": q.sku_id,
            "sku_name": q.sku_name,
            "quantity": q.quantity,
            "unit_price": q.unit_price,
            "subtotal": q.subtotal,
            "tax": q.tax,
            "shipping": q.shipping,
            "total": q.total,
            "currency": q.currency,
        }
        reply_text = format_quote_message(q)
    else:
        reply_text = (
            "Sorry, I couldn't identify this product in our catalog. "
            "Please send a clearer photo or describe the item."
        )
    latencies["quote_ms"] = int((time.monotonic() - t2) * 1000)

    # 4. Reply ────────────────────────────────────────────────────────────────
    t3 = time.monotonic()
    await reply_fn(sender, reply_text)
    latencies["reply_ms"] = int((time.monotonic() - t3) * 1000)

    # 5. Persist + broadcast ──────────────────────────────────────────────────
    event = PipelineEvent(
        message_id=message_id,
        channel=channel,
        sender=sender,
        media_url=image_url,
        extraction=extraction,
        quote=quote_dict,
        latencies=latencies,
        received_at=datetime.now(timezone.utc).isoformat(),
    )
    payload = asdict(event)
    await insert_event(payload)
    await broadcast(payload)

    return event
