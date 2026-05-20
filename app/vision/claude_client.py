"""Claude Sonnet 4.6 vision wrapper.

Supports both URL-based and base64-encoded images.
Prompt caching is enabled on the (large, stable) system prompt.
"""
import base64
import json
import re
from typing import Any

import httpx
from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.vision.prompts import SYSTEM_PROMPT, USER_PROMPT

_client = Anthropic(api_key=settings.anthropic_api_key)

MODEL = "claude-sonnet-4-6"


def _clean_json(text: str) -> dict[str, Any]:
    """Strip any accidental markdown fences and parse JSON."""
    text = re.sub(r"```(?:json)?", "", text).strip()
    return json.loads(text)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
async def extract_from_url(image_url: str, media_type: str = "image/jpeg") -> dict[str, Any]:
    """Download image bytes and send to Claude for structured extraction."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(image_url)
        resp.raise_for_status()
        image_data = base64.standard_b64encode(resp.content).decode("utf-8")
        media_type = resp.headers.get("content-type", media_type).split(";")[0]

    return _call_claude(image_data, media_type)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
async def extract_from_bytes(image_bytes: bytes, media_type: str = "image/jpeg") -> dict[str, Any]:
    image_data = base64.standard_b64encode(image_bytes).decode("utf-8")
    return _call_claude(image_data, media_type)


def _call_claude(image_data: str, media_type: str) -> dict[str, Any]:
    response = _client.messages.create(
        model=MODEL,
        max_tokens=512,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                # Prompt caching — system prompt is stable across all requests
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {"type": "text", "text": USER_PROMPT},
                ],
            }
        ],
    )
    return _clean_json(response.content[0].text)
