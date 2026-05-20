"""Pure quoting logic — no I/O, fully unit-testable."""
from dataclasses import dataclass

from app.config import settings
from app.storage.models import Sku

FLAT_SHIPPING_RATE = 4.99   # USD per kg
MIN_SHIPPING = 5.99
FREE_SHIPPING_THRESHOLD = 200.00


@dataclass
class QuoteResult:
    sku_id: str
    sku_name: str
    quantity: int
    unit_price: float
    subtotal: float
    tax: float
    shipping: float
    total: float
    currency: str


def build_quote(sku: Sku, quantity: int) -> QuoteResult:
    qty = max(1, quantity)
    subtotal = round(sku.unit_price * qty, 2)
    tax = round(subtotal * settings.tax_rate, 2)

    if subtotal >= FREE_SHIPPING_THRESHOLD:
        shipping = 0.0
    else:
        shipping = round(max(MIN_SHIPPING, sku.weight_kg * qty * FLAT_SHIPPING_RATE), 2)

    total = round(subtotal + tax + shipping, 2)

    return QuoteResult(
        sku_id=sku.id,
        sku_name=sku.name,
        quantity=qty,
        unit_price=sku.unit_price,
        subtotal=subtotal,
        tax=tax,
        shipping=shipping,
        total=total,
        currency=sku.currency,
    )


def format_quote_message(q: QuoteResult) -> str:
    lines = [
        f"*Quote for {q.sku_name}*",
        f"Qty: {q.quantity} × ${q.unit_price:.2f}",
        f"Subtotal: ${q.subtotal:.2f}",
        f"Tax ({settings.tax_rate*100:.0f}%): ${q.tax:.2f}",
        f"Shipping: {'FREE' if q.shipping == 0 else f'${q.shipping:.2f}'}",
        f"*Total: ${q.total:.2f} {q.currency}*",
    ]
    return "\n".join(lines)
