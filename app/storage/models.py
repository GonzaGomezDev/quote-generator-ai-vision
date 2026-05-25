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
class PipelineEvent:
    """Emitted after every pipeline run and forwarded via SSE."""
    message_id: str
    channel: str
    sender: str
    media_url: str
    extraction: dict[str, Any]
    quote: dict[str, Any] | None
    latencies: dict[str, int]   # stage → ms
    received_at: str
