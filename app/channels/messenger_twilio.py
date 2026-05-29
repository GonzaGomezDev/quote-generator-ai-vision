"""Facebook Messenger via Twilio webhook handler.

Twilio Messenger sends text and media as separate webhook POSTs for the same
user message. We buffer incoming parts per sender for BUFFER_SECS seconds so
they can be merged before the agent runs.
"""
import asyncio
import logging

from fastapi import APIRouter, Header, Request
from twilio.rest import Client as TwilioClient

log = logging.getLogger(__name__)

from app.config import settings
from app.agent.runner import run_agent

router = APIRouter(tags=["messenger"])
_twilio = TwilioClient(settings.twilio_account_sid, settings.twilio_auth_token)

_BUFFER_SECS = 10.0
# sender → {"text": str|None, "image_url": str|None}
_pending: dict[str, dict] = {}


async def _reply(sender: str, text: str) -> None:
    if not settings.twilio_messenger_from:
        raise ValueError("TWILIO_MESSENGER_FROM is not configured in .env")
    _twilio.messages.create(
        from_=settings.twilio_messenger_from,
        to=sender,
        body=text,
    )


async def _flush(sender: str) -> None:
    await asyncio.sleep(_BUFFER_SECS)
    entry = _pending.pop(sender, None)
    if not entry:
        return
    await run_agent(
        channel="messenger",
        sender=sender,
        text=entry.get("text"),
        image_url=entry.get("image_url"),
        reply_fn=_reply,
    )


@router.post("/webhook/messenger")
async def messenger_webhook(
    request: Request,
    x_twilio_signature: str = Header(default=""),
):
    form = await request.form()
    data = dict(form)

    sender: str = data.get("From", "")
    text: str = data.get("Body", "").strip() or None
    media_url: str = data.get("MediaUrl0", "") or None

    log.info("messenger webhook | full payload: %s", dict(data))
    log.info("messenger webhook | sender=%s text=%r media_url=%r", sender, text, media_url)

    if not sender:
        return {"status": "no_sender"}

    if sender in _pending:
        entry = _pending[sender]
        if text:
            entry["text"] = text
        if media_url:
            entry["image_url"] = media_url
        log.info("messenger webhook | merged into pending → %s", entry)
        return {"status": "merged"}

    _pending[sender] = {"text": text, "image_url": media_url}
    asyncio.create_task(_flush(sender))
    log.info("messenger webhook | buffered new entry, flush in %.1fs", _BUFFER_SECS)
    return {"status": "buffered"}
