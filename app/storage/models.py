from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Message:
    id: str
    channel: str          # "whatsapp" | "telegram"
    sender: str
    media_url: str
    received_at: datetime


@dataclass
class Extraction:
    message_id: str
    data: dict[str, Any]
    latency_ms: int


@dataclass
class Sku:
    id: str
    name: str
    category: str
    brand: str
    color: str
    unit_price: float
    currency: str
    weight_kg: float
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class Quote:
    message_id: str
    sku_id: str | None
    sku_name: str | None
    quantity: int
    subtotal: float
    tax: float
    shipping: float
    total: float
    currency: str
    status: str           # "quoted" | "unmatched"


@dataclass
class AgentEvent:
    """Emitted after every agent turn and forwarded via SSE."""
    message_id: str
    channel: str
    sender: str
    text: str | None              # inbound text (None for image-only messages)
    media_url: str | None         # inbound image URL if present
    reply_text: str               # final assistant reply sent to the customer
    extraction: dict[str, Any]    # last analyze_product_image result (empty if not called)
    quote: dict[str, Any] | None  # last build_quote result if a quote was generated
    tool_calls: list[dict]        # [{name, input, result_summary}] for all tool invocations
    latencies: dict[str, int]     # stage → ms (agent_ms + per-tool ms)
    received_at: str
