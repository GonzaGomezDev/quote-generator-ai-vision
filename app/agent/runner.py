"""Agent loop: handles every inbound message (text, image, or both).

Flow:
  1. If image_url present, download it immediately (Twilio URLs need Basic Auth).
  2. Load conversation history for (channel, sender).
  3. Build the new user message content blocks (image as base64 if present).
  4. Loop: call Claude with tool schemas; dispatch any tool_use blocks; feed results back.
  5. On end_turn / text stop: send reply, persist turns, broadcast SSE event.
"""
import base64
import json
import logging
import time
import uuid
from dataclasses import asdict
from datetime import datetime, timezone

import httpx
from anthropic import Anthropic

log = logging.getLogger(__name__)

from app.config import settings
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import TOOL_SCHEMAS, dispatch_tool
from app.storage.db import append_turn, insert_event, load_history
from app.storage.models import AgentEvent
from app.realtime.events import broadcast

_client = Anthropic(api_key=settings.anthropic_api_key)
MODEL = "claude-sonnet-4-6"
MAX_ITERATIONS = 5


async def _download_image(url: str) -> tuple[bytes, str]:
    """Download image bytes, adding Twilio Basic Auth for Twilio media URLs."""
    auth = None
    if "twilio.com" in url and settings.twilio_account_sid and settings.twilio_auth_token:
        auth = (settings.twilio_account_sid, settings.twilio_auth_token)

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(url, auth=auth)
        resp.raise_for_status()

    media_type = resp.headers.get("content-type", "image/jpeg").split(";")[0]
    return resp.content, media_type


async def run_agent(
    channel: str,
    sender: str,
    text: str | None,
    image_url: str | None,
    reply_fn,             # async callable(sender: str, text: str) → None
) -> AgentEvent:
    message_id = str(uuid.uuid4())
    received_at = datetime.now(timezone.utc).isoformat()
    latencies: dict[str, int] = {}
    tool_calls: list[dict] = []
    last_extraction: dict = {}
    last_quote: dict | None = None

    # ── Pre-download image (avoids Anthropic trying to fetch Twilio-auth URLs) ─
    # image_cache is passed to dispatch_tool so the vision tool reuses the bytes.
    image_cache: dict[str, tuple[bytes, str]] = {}
    if image_url:
        log.info("runner | downloading image url=%s", image_url)
        try:
            image_bytes, image_media_type = await _download_image(image_url)
            image_cache[image_url] = (image_bytes, image_media_type)
            log.info("runner | image downloaded ok bytes=%d media_type=%s", len(image_bytes), image_media_type)
        except Exception as exc:
            log.error("runner | image download failed url=%s error=%s", image_url, exc)
            note = f"[El cliente envió una imagen pero no se pudo descargar: {exc}]"
            text = f"{text}\n{note}" if text else note
            image_url = None

    # ── Build initial user content blocks ────────────────────────────────────
    content_blocks: list[dict] = []
    if image_url and image_url in image_cache:
        image_bytes, image_media_type = image_cache[image_url]
        content_blocks.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": image_media_type,
                "data": base64.standard_b64encode(image_bytes).decode(),
            },
        })
    if text:
        content_blocks.append({"type": "text", "text": text})
    if not content_blocks:
        content_blocks.append({"type": "text", "text": "(sin contenido)"})

    # ── Load history and append current user turn ─────────────────────────────
    history = await load_history(channel, sender)
    messages: list[dict] = history + [{"role": "user", "content": content_blocks}]

    # ── Agent loop ────────────────────────────────────────────────────────────
    t_agent_start = time.monotonic()
    reply_text = ""
    iterations = 0

    while iterations < MAX_ITERATIONS:
        iterations += 1
        response = _client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            tools=TOOL_SCHEMAS,
            messages=messages,
        )

        assistant_content = response.content

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in assistant_content:
                if block.type != "tool_use":
                    continue
                result_str, timing = await dispatch_tool(block.name, block.input, image_cache)
                latencies.update(timing)

                result_data = json.loads(result_str)
                tool_calls.append({
                    "name": block.name,
                    "input": block.input,
                    "result_summary": _summarise(block.name, result_data),
                })

                if block.name == "analyze_product_image":
                    last_extraction = result_data.get("extraction", {})
                elif block.name == "build_quote" and "error" not in result_data:
                    last_quote = {k: v for k, v in result_data.items() if k != "message"}

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_str,
                })

            messages.append({"role": "assistant", "content": assistant_content})
            messages.append({"role": "user", "content": tool_results})

        else:
            for block in assistant_content:
                if hasattr(block, "text"):
                    reply_text += block.text
            messages.append({"role": "assistant", "content": assistant_content})
            break

    latencies["agent_ms"] = int((time.monotonic() - t_agent_start) * 1000)

    if not reply_text:
        reply_text = "Lo siento, no pude procesar tu solicitud. Por favor, intentá de nuevo."

    # ── Send reply ────────────────────────────────────────────────────────────
    t_reply = time.monotonic()
    await reply_fn(sender, reply_text)
    latencies["reply_ms"] = int((time.monotonic() - t_reply) * 1000)

    # ── Persist conversation turns (full exchange incl. tool calls/results) ──
    for turn in messages[len(history):]:
        await append_turn(channel, sender, turn["role"], _serialise_blocks(turn["content"]))

    # ── Build and broadcast SSE event ─────────────────────────────────────────
    event = AgentEvent(
        message_id=message_id,
        channel=channel,
        sender=sender,
        text=text,
        media_url=image_url,
        reply_text=reply_text,
        extraction=last_extraction,
        quote=last_quote,
        tool_calls=tool_calls,
        latencies=latencies,
        received_at=received_at,
    )
    payload = asdict(event)
    await insert_event(payload)
    await broadcast(payload)

    return event


# ── Helpers ───────────────────────────────────────────────────────────────────

def _summarise(tool_name: str, result: dict) -> str:
    if "error" in result:
        return f"error: {result['error']}"
    if tool_name == "analyze_product_image":
        sku = result.get("sku")
        product = result.get("extraction", {}).get("product_guess", "desconocido")
        return f"identificado '{product}'" + (f" → coincide {sku['id']}" if sku else " → sin coincidencia")
    if tool_name == "search_catalog":
        n = len(result.get("results", []))
        return f"{n} resultado(s) encontrado(s)"
    if tool_name == "build_quote":
        return f"cotización {result.get('sku_name')} × {result.get('quantity')} = ${result.get('total')} {result.get('currency')}"
    return json.dumps(result)[:120]


def _serialise_blocks(blocks: list) -> list[dict]:
    """Convert content blocks to plain dicts for DB storage.
    - SDK Pydantic objects (ToolUseBlock, TextBlock) are converted via model_dump().
    - Image blocks are replaced with a text placeholder (strips base64).
    - tool_result and tool_use dicts pass through unchanged so history reloads
      correctly and the Anthropic API can match tool_use/tool_result pairs.
    """
    out = []
    for b in blocks:
        if hasattr(b, "model_dump"):
            b = b.model_dump(exclude_none=True)
        if isinstance(b, dict):
            if b.get("type") == "image":
                out.append({"type": "text", "text": "[el cliente envió una imagen]"})
            else:
                out.append(b)
        else:
            out.append({"type": "text", "text": str(b)})
    return out
