"""Telegram Bot webhook handler."""
import hashlib
import hmac
import logging

import httpx
from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request, status

from app.config import settings
from app.pipeline.orchestrator import run_pipeline

router = APIRouter(tags=["telegram"])
logger = logging.getLogger(__name__)

_TELEGRAM_API = "https://api.telegram.org"


def _bot_url(method: str) -> str:
    return f"{_TELEGRAM_API}/bot{settings.telegram_bot_token}/{method}"


async def _get_file_url(file_id: str) -> str:
    """Resolve a file_id to a downloadable URL via Telegram's getFile API."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(_bot_url("getFile"), params={"file_id": file_id})
        resp.raise_for_status()
        file_path = resp.json()["result"]["file_path"]
    return f"{_TELEGRAM_API}/file/bot{settings.telegram_bot_token}/{file_path}"


async def _reply(chat_id: str, text: str) -> None:
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(
            _bot_url("sendMessage"),
            json={"chat_id": int(chat_id), "text": text},
        )


@router.post("/webhook/telegram")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_telegram_bot_api_secret_token: str = Header(default=""),
):
    # Verify secret token if configured
    if settings.telegram_webhook_secret:
        expected = hmac.new(
            settings.telegram_webhook_secret.encode(),
            settings.telegram_bot_token.encode(),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, x_telegram_bot_api_secret_token):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bad secret")

    payload = await request.json()
    logger.info("Telegram webhook payload: %s", payload)

    message = payload.get("message") or payload.get("channel_post", {})
    if not message:
        return {"status": "ignored"}

    chat_id = str(message.get("chat", {}).get("id", ""))
    if not chat_id:
        return {"status": "no_chat"}

    # Photos arrive as an array sorted by size ascending — take the largest
    photos = message.get("photo")
    document = message.get("document")

    file_id: str | None = None
    if photos:
        file_id = photos[-1]["file_id"]
    elif document and (document.get("mime_type", "").startswith("image/")):
        # User sent an uncompressed image as a file
        file_id = document["file_id"]

    if not file_id:
        return {"status": "no_image"}

    image_url = await _get_file_url(file_id)

    background_tasks.add_task(
        run_pipeline,
        image_url=image_url,
        channel="telegram",
        sender=chat_id,
        reply_fn=_reply,
    )
    return {"status": "queued"}
