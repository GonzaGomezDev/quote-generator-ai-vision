"""In-process SSE fan-out broker.

Any coroutine can call `broadcast(payload)` to push a JSON-serialisable dict
to all connected dashboard clients. Each client gets its own asyncio.Queue.
"""
import asyncio
import json
from collections.abc import AsyncGenerator

_subscribers: list[asyncio.Queue] = []


def subscribe() -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue(maxsize=100)
    _subscribers.append(q)
    return q


def unsubscribe(q: asyncio.Queue) -> None:
    try:
        _subscribers.remove(q)
    except ValueError:
        pass


async def broadcast(payload: dict) -> None:
    dead = []
    for q in _subscribers:
        try:
            q.put_nowait(payload)
        except asyncio.QueueFull:
            dead.append(q)
    for q in dead:
        unsubscribe(q)


async def event_stream(q: asyncio.Queue) -> AsyncGenerator[str, None]:
    """Yield SSE-formatted strings from the queue until the client disconnects."""
    try:
        while True:
            payload = await q.get()
            data = json.dumps(payload)
            yield f"data: {data}\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        unsubscribe(q)
