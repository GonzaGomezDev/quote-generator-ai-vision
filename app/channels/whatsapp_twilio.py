"""WhatsApp via Twilio Sandbox webhook handler."""
import hmac
import hashlib
from urllib.parse import urlencode

from fastapi import APIRouter, BackgroundTasks, Form, Header, HTTPException, Request, status
from twilio.rest import Client as TwilioClient

from app.config import settings
from app.pipeline.orchestrator import run_pipeline

router = APIRouter(tags=["whatsapp"])
_twilio = TwilioClient(settings.twilio_account_sid, settings.twilio_auth_token)


def _verify_twilio_signature(
    request_url: str,
    post_params: dict,
    signature: str,
    auth_token: str,
) -> bool:
    """Validate Twilio's X-Twilio-Signature header."""
    # Sort POST params and append to URL
    sorted_params = "".join(f"{k}{v}" for k, v in sorted(post_params.items()))
    s = request_url + sorted_params
    expected = hmac.new(auth_token.encode(), s.encode(), hashlib.sha1).digest()
    import base64
    expected_b64 = base64.b64encode(expected).decode()
    return hmac.compare_digest(expected_b64, signature)


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
    x_twilio_signature: str = Header(default=""),
):
    form = await request.form()
    data = dict(form)

    media_url: str = data.get("MediaUrl0", "")
    sender: str = data.get("From", "")

    if not media_url:
        # Text-only message — ignore for now
        return {"status": "no_media"}

    background_tasks.add_task(
        run_pipeline,
        image_url=media_url,
        channel="whatsapp",
        sender=sender,
        reply_fn=_reply,
    )
    return {"status": "queued"}
