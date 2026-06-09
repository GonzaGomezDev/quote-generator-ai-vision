"""WhatsApp via Twilio webhook handler."""
import hmac
import hashlib

from fastapi import APIRouter, BackgroundTasks, Header, Request
from twilio.rest import Client as TwilioClient

from app.config import settings
from app.agent.runner import run_agent

router = APIRouter(tags=["whatsapp"])
_twilio = TwilioClient(settings.twilio_account_sid, settings.twilio_auth_token)

async def _reply(sender: str, text: str) -> None:
    _twilio.messages.create(
        from_=settings.twilio_whatsapp_from,
        to=sender,
        body=text,
    )


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    form = await request.form()
    data = dict(form)

    sender: str = data.get("From", "")
    text: str = data.get("Body", "").strip() or None
    media_url: str = data.get("MediaUrl0", "") or None

    if not sender:
        return {"status": "no_sender"}

    background_tasks.add_task(
        run_agent,
        channel="whatsapp",
        sender=sender,
        text=text,
        image_url=media_url,
        reply_fn=_reply,
    )
    return {"status": "queued"}
